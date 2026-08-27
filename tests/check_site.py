# -*- coding: utf-8 -*-
"""
사이트 검사 — python3 tests/check_site.py

이 저장소는 손으로 쓴 페이지가 아니라 **구워 내는 페이지**다.
그래서 깨지는 방식도 정해져 있다. 지금까지 실제로 깨진 자리를 여기에 고정한다.

  · 다시 구웠더니 <head> 의 OG 메타 20줄이 통째로 사라졌다
    (화면은 멀쩡해서, 카카오톡에 링크를 붙여 보고서야 알았다)
  · 페이지를 손으로 고쳤다가 다음에 다시 구울 때 날아갔다
  · 프로젝트를 하나 더했는데 히어로 통계 숫자는 그대로였다 (10 → 11 정정 커밋)
  · 카드의 '데모 열기'와 '저장소'가 서로 다른 번호를 가리켰다
  · target="_new" 만 붙이고 rel="noopener noreferrer" 를 빠뜨렸다
  · 링크가 없는 파일을 가리켰다

의존성 없이 표준 라이브러리만 쓴다. 이 저장소에는 빌드 도구가 없다.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# build.py 의 전환 스위치를 그대로 읽는다. 여기에 True/False 를 베껴 적으면
# 둘이 어긋나는 순간 검사가 거짓말을 한다.
sys.path.insert(0, ROOT)
import build as _build            # noqa: E402
PAGES_LIVE = _build.PAGES_LIVE
SITE = 'https://aebonlee.github.io/hd-04/'

TOP_PAGES = ['index.html', 'labs.html', 'projects.html']
GUIDE_PAGES = ['guide/%s.html' % s for s in
               ('openai', 'claude', 'solar', 'gemini', 'supabase')]
PAGES = TOP_PAGES + GUIDE_PAGES

passed = 0
failed = 0


def ok(cond, label, detail=''):
    global passed, failed
    if cond:
        passed += 1
    else:
        failed += 1
        sys.stderr.write('  X %s\n' % label)
        if detail:
            sys.stderr.write('      %s\n' % detail)


def eq(actual, expected, label):
    ok(actual == expected, label, '기대: %r  실제: %r' % (expected, actual))


def group(name):
    print('\n' + name)


def read(rel):
    return io.open(os.path.join(ROOT, rel), encoding='utf-8').read()


# ─────────────────────────────────────────── 1. 다시 구워도 같은가
group('1. 다시 구워도 같은가 (생성기가 무엇도 잃지 않는가)')

tmp = tempfile.mkdtemp(prefix='hd04-')
try:
    work = os.path.join(tmp, 'site')
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    for script in ('build.py', os.path.join('guide', 'gen.py')):
        r = subprocess.run([sys.executable, script], cwd=work,
                           capture_output=True, text=True)
        ok(r.returncode == 0, '%s 가 오류 없이 돈다' % script, r.stderr.strip()[-400:])

    for rel in PAGES + ['_parts/nav_%s.html' % k for k in
                        ('openai', 'claude', 'solar', 'gemini', 'supabase')]:
        before = read(rel)
        after = io.open(os.path.join(work, rel), encoding='utf-8').read()
        ok(before == after,
           '%s — 다시 구워도 그대로다' % rel,
           '커밋된 판과 다시 구운 판이 다릅니다. '
           '페이지를 손으로 고쳤거나 생성기가 무언가를 잃고 있습니다.')
finally:
    shutil.rmtree(tmp, ignore_errors=True)


# ─────────────────────────────────────────── 2. HD:META 블록
group('2. HD:META 블록 — 링크 미리보기가 살아 있는가')

for rel in PAGES:
    html = read(rel)
    ok('HD:META:BEGIN' in html and 'HD:META:END' in html,
       '%s — HD:META 블록이 있다' % rel,
       '다시 구우면서 사라졌을 수 있습니다 (metablock.py 참조).')

    for prop in ('og:title', 'og:description', 'og:image', 'og:url', 'twitter:card'):
        ok(prop in html, '%s — %s 가 있다' % (rel, prop))

    # og:image 가 상대 경로면 카카오톡·슬랙이 미리보기를 만들지 못한다
    for m in re.finditer(r'<meta property="og:(image|url)" content="([^"]+)"', html):
        ok(m.group(2).startswith(SITE),
           '%s — og:%s 가 절대 주소다' % (rel, m.group(1)),
           m.group(2))

    m = re.search(r'<meta property="og:image" content="' + re.escape(SITE) + r'([^"]+)"', html)
    if m:
        ok(os.path.exists(os.path.join(ROOT, m.group(1))),
           '%s — og:image 파일이 저장소에 있다' % rel, m.group(1))

    m = re.search(r'<link rel="canonical" href="([^"]+)"', html)
    ok(m is not None and m.group(1).startswith(SITE),
       '%s — canonical 이 절대 주소다' % rel)


# ─────────────────────────────────────────── 3. 링크
group('3. 링크 — 없는 파일을 가리키지 않는가')

LINK = re.compile(r'(?:href|src)="([^"]+)"')

for rel in PAGES:
    html = read(rel)
    base = os.path.dirname(os.path.join(ROOT, rel))
    for target in set(LINK.findall(html)):
        if re.match(r'^(https?:|mailto:|tel:|data:|#|//)', target):
            continue
        path = os.path.normpath(os.path.join(base, target.split('#')[0].split('?')[0]))
        ok(os.path.exists(path), '%s → %s 가 실재한다' % (rel, target))

group('3-1. 새 창으로 여는 링크에 rel="noopener noreferrer" 가 붙어 있는가')

# target 만 두면 새 창이 opener 를 통해 원래 창을 건드릴 수 있다.
ANCHOR = re.compile(r'<a\b[^>]*>', re.S)
for rel in PAGES:
    bad = []
    for tag in ANCHOR.findall(read(rel)):
        if 'target="_new"' in tag or 'target="_blank"' in tag:
            if 'noopener' not in tag or 'noreferrer' not in tag:
                bad.append(re.sub(r'\s+', ' ', tag)[:90])
    ok(not bad, '%s — 새 창 링크에 rel 이 빠진 것이 없다' % rel, '\n      '.join(bad))


# ─────────────────────────────────────────── 4. 숫자가 실제와 맞는가
group('4. 히어로 통계 숫자가 카드 수와 맞는가')

home = read('index.html')
labs = read('labs.html')
projects = read('projects.html')


def stat(page_html, label):
    m = re.search(r'<div class="stat"><b>([^<]+)</b><span>' + re.escape(label) + r'</span>',
                  page_html)
    return m.group(1) if m else None


def cards(section_html):
    """섹션 안의 카드 수. .cards 격자 안의 것만 센다."""
    m = re.search(r'<div class="cards">(.*?)\n      </div>', section_html, re.S)
    body = m.group(1) if m else section_html
    return len(re.findall(r'<div class="card">', body))


lab_cards = cards(labs)
project_cards = cards(projects)

eq(stat(home, '실습 저장소'), str(lab_cards), '홈 통계의 실습 저장소 수 == 실습 카드 수')
eq(stat(home, '수강생 프로젝트'), str(project_cards), '홈 통계의 프로젝트 수 == 프로젝트 카드 수')

# 칩에 적힌 번호가 실제 카드와 정확히 같아야 한다.
# 번호가 이어지지 않으므로(01~12 다음이 17) '마지막 번호 == 카드 수' 는 더 이상
# 성립하지 않는다. 그 가정으로 두면 카드를 더할 때 조용히 어긋난다.
def numbers_in(label):
    """'hd-project01~12 · 17' → {1..12, 17}"""
    out = set()
    label = label.replace('hd-project', '')
    for part in re.split(r'[·,]', label):
        part = part.strip()
        m2 = re.match(r'^(\d+)\s*~\s*(\d+)$', part)
        if m2:
            out.update(range(int(m2.group(1)), int(m2.group(2)) + 1))
        elif re.match(r'^\d+$', part):
            out.add(int(part))
    return out

m = re.search(r'<span class="chip[^"]*">([^<]*hd-project[^<]*)</span>', projects)
ok(m is not None, '프로젝트 칩에 번호가 적혀 있다')
if m:
    chip = numbers_in(m.group(1))
    on_cards = set(int(n) for n in re.findall(r'HD-PROJECT(\d+)', projects))
    eq(sorted(chip), sorted(on_cards), '칩의 번호 == 카드의 번호')

# 본문 곳곳의 "N종" 표기도 같아야 한다.
#
# 예전에는 index/projects 의 "실전 업무 도구 N종" 만 봤다. 그래서
# _parts/sec_curriculum.html 의 "실전 프로젝트 10종을 완성합니다" 가
# 프로젝트가 13개가 되도록 10 인 채로 남아 있었다 — 구운 페이지에도
# 그대로 나가고 있었는데 아무 검사도 걸리지 않았다.
# 이제 소스와 구운 페이지를 **전부** 훑는다.
#
# 다만 모든 "N종" 을 세면 안 된다. 카드 본문에는 프로젝트 수가 아닌
# "시트 이름 7종"(17번), "반복 업무 자동화 4종"(02번 제목) 이 있다.
# 그래서 '실전/수강생' 이 앞에 붙은 것만 본다.
# README.md 도 넣는다. 실제로 "hd-project01 ~ hd-project12 (12종)" 이 카드가
# 열일곱 장이 되는 동안 그대로 남아 있었다 — 소스만 보던 검사가 못 봤다.
SOURCES = [r for r in ['build.py', 'README.md'] + ['_parts/' + n for n in
           sorted(os.listdir(os.path.join(ROOT, '_parts')))]
           if r.endswith(('.py', '.html', '.md'))]
COUNT_PHRASE = re.compile(r'(?:실전|수강생)\s*(?:프로젝트|업무\s*도구)\s*(\d+)\s*종')
for rel in PAGES + SOURCES:
    for n in set(COUNT_PHRASE.findall(read(rel))):
        eq(int(n), project_cards,
           '%s — "…%s종" 표기가 카드 수와 맞는다' % (rel, n))

m = re.search(r'<b>(\d+)개 프로젝트 모두', projects)
if m:
    eq(int(m.group(1)), project_cards, '하단 안내의 "N개 프로젝트" 가 카드 수와 맞는다')

# 구운 페이지만 보면 놓친다. 소스(_parts/, build.py)에 적힌 범위도 카드 수와 맞아야 한다.
# 실제로 _parts/hero.html 이 hd-project01~11 · "11" 을 든 채 남아 있었다. build.py 가
# 그 조각을 읽어만 두고 쓰지 않아(HERO_HOME) 구운 페이지는 12 였고, 검사도 통과했다.
# build.py 는 "내용은 _parts/ 를 고칠 것"이라고 적어 두었으므로, 그 말을 믿고 고친
# 사람은 아무 일도 일어나지 않는 파일을 고치게 된다.
for rel in SOURCES:
    if not rel.endswith(('.py', '.html', '.md')):
        continue
    # 소스에 적힌 번호 목록도 카드와 같아야 한다.
    # 표기가 두 가지다: "hd-project01 ~ hd-project12" 와 "hd-project01~12 · 17"
    # '~' 가 들어간 범위 표기만 본다. 개별 링크(hd-project07)는 5번 검사가 따로 본다.
    for m3 in re.finditer(r'hd-project\d+\s*~\s*(?:hd-project)?[\d\s·,]+', read(rel)):
        got = numbers_in(m3.group(0))
        if not got:
            continue
        eq(sorted(got), sorted(on_cards),
           '%s — "%s" 의 번호가 카드와 맞는다' % (rel, m3.group(0).strip()))

# 읽어만 두고 쓰지 않는 조각이 남지 않게 — 위 상황을 만든 원인 자체를 막는다
build_src = read('build.py')
for name in re.findall(r"P\('([a-z_]+)'\)", build_src):
    var = re.search(r"(\w+)\s*=\s*P\('%s'\)" % name, build_src)
    if var:
        ok(len(re.findall(r'\b%s\b' % var.group(1), build_src)) > 1,
           'build.py — _parts/%s.html 을 읽었으면 실제로 쓴다' % name)


# 하단 안내가 "저장소마다 supabase/schema.sql 이 들어 있습니다" 라고 단언하고 있었다.
# 카드를 두 장 더하자 거짓이 됐다 — 13·14 는 DB 를 쓰지 않는다.
# 몇 곳인지 숫자를 적었으면 그 숫자가 카드 수와 다른지 확인할 수 있어야 한다.
m = re.search(r'<b>(\d+)개</b>\s*저장소에는\s*<code>supabase', projects)
ok(m is not None, '하단 안내가 Supabase 저장소 수를 숫자로 적는다',
   '"저장소마다" 처럼 전부라고 단언하면 예외가 생겼을 때 거짓이 된다')
if m:
    ok(int(m.group(1)) <= project_cards,
       'Supabase 저장소 수가 전체 카드 수를 넘지 않는다',
       '%s > %s' % (m.group(1), project_cards))
    ok(int(m.group(1)) < project_cards,
       '전부가 아니라면 예외를 따로 밝힌다',
       '전부라면 "저장소마다" 로 쓰는 편이 낫다')
    ok('데이터베이스가 필요 없습니다' in projects,
       'DB 를 쓰지 않는 저장소가 어느 것인지 밝힌다')


# ─────────────────────────────────────────── 5. 프로젝트 카드
group('5. 프로젝트 카드 — 번호와 링크가 서로 맞는가')

CARD = re.compile(r'<div class="card">(.*?)</div>\s*</div>', re.S)
seen = []
for body in CARD.findall(projects):
    m = re.search(r'HD-PROJECT(\d+)', body)
    if not m:
        continue
    no = m.group(1)
    seen.append(no)

    owner = re.search(r'<span class="owner">([^<]+)</span>', body)
    ok(owner is not None and owner.group(1).strip() != '',
       'HD-PROJECT%s — 기획자 이름이 있다' % no)

    demo = re.search(r'href="https://aebonlee\.github\.io/hd-project(\d+)/"', body)
    repo = re.search(r'href="https://github\.com/aebonlee/hd-project(\d+)"', body)
    # 저장소를 비공개로 돌리면 Pages 가 서지 않으므로 데모 단추가 없는 것이 맞다.
    if PAGES_LIVE:
        ok(demo is not None, 'HD-PROJECT%s — 데모 링크가 있다' % no)
    else:
        ok(demo is None, 'HD-PROJECT%s — 비공개 전환 뒤에는 데모 링크가 없다' % no)
    ok(repo is not None, 'HD-PROJECT%s — 저장소 링크가 있다' % no)
    if demo and repo:
        # 카드를 복사해 만들면서 번호 하나를 안 고치는 것이 가장 흔한 실수다
        eq((demo.group(1), repo.group(1)), (no, no),
           'HD-PROJECT%s — 데모·저장소 링크가 같은 번호를 가리킨다' % no)

eq(len(seen), len(set(seen)), '프로젝트 번호가 중복되지 않는다')
# 번호는 기획서 번호를 따른다. 17번 기획서로 만든 프로젝트는 hd-project17 이다.
# 그래서 '01부터 빠짐없이 이어진다'는 성립하지 않는다 — 01~12 다음이 17 이다.
# 순서(오름차순)만 지키면 된다. 사람이 목록을 훑을 때 번호가 왔다갔다 하지 않게.
eq(seen, sorted(seen), '프로젝트 번호가 오름차순이다')
ok(all(re.match(r'^\d{2}$', n) for n in seen), '프로젝트 번호가 두 자리다', str(seen))
eq(len(seen), project_cards, '번호가 붙은 카드 수 == 전체 카드 수')


# ─────────────────────────────────────────── 5-1. 전환 스위치
#
# build.py 의 PAGES_LIVE 를 False 로 돌리면 저장소를 비공개로 바꾼 뒤의 판이
# 나온다. **그날이 오기 전에 여기서 실제로 구워 본다.**
#
# 아무도 눌러 보지 않은 스위치는 정작 필요한 날 안 돈다. 게다가 _no_pages()
# 는 조각의 표기에 기대는 코드라, 카드 표기가 바뀌면 조용히 아무 일도 안
# 하게 될 수 있다 — 그러면 "고쳤다"고 믿은 채 죽은 링크가 그대로 나간다.
group('5-1. 전환 스위치 — 비공개로 돌린 판이 실제로 구워지는가')

tmp = tempfile.mkdtemp(prefix='hd04-off-')
try:
    work = os.path.join(tmp, 'site')
    shutil.copytree(ROOT, work, ignore=shutil.ignore_patterns('.git', '__pycache__'))

    gen = os.path.join(work, 'build.py')
    src = io.open(gen, encoding='utf-8').read()
    flipped = src.replace('PAGES_LIVE = True', 'PAGES_LIVE = False', 1)
    ok(flipped != src, 'build.py 에 PAGES_LIVE 스위치가 있다')
    io.open(gen, 'w', encoding='utf-8').write(flipped)

    r = subprocess.run([sys.executable, 'build.py'], cwd=work,
                       capture_output=True, text=True)
    ok(r.returncode == 0, '스위치를 끄고도 오류 없이 구워진다', r.stderr.strip()[-500:])

    if r.returncode == 0:
        off_projects = io.open(os.path.join(work, 'projects.html'), encoding='utf-8').read()
        off_labs = io.open(os.path.join(work, 'labs.html'), encoding='utf-8').read()
        off_index = io.open(os.path.join(work, 'index.html'), encoding='utf-8').read()

        # ① 카드의 github.io 단추가 전부 빠졌는가
        for rel, html in (('projects.html', off_projects), ('labs.html', off_labs)):
            left = re.findall(r'<a class="btn[^"]*" href="https://aebonlee\.github\.io/[^"]*"',
                              html)
            eq(left, [], '%s — 데모/페이지 단추가 하나도 남지 않는다' % rel)

        # ② 저장소 단추는 남아 있어야 한다. 권한이 있으면 열리기 때문이다.
        eq(len(re.findall(r'>저장소</a>', off_projects)), project_cards,
           'projects.html — 저장소 단추는 카드마다 그대로 있다')
        ok(len(re.findall(r'>저장소</a>', off_labs)) > 0,
           'labs.html — 저장소 단추는 그대로 있다')

        # ③ 왜 없어졌는지 적혀 있는가. 안 적으면 "링크가 빠진 것"으로 보인다.
        for rel, html in (('projects.html', off_projects), ('labs.html', off_labs)):
            ok('저장소를 비공개로 돌리면서' in html,
               '%s — 단추가 없어진 이유를 적는다' % rel)

        # ④ 이제 틀린 안내가 된 문장이 걷혔는가.
        #    private 이면 Settings → Pages 에서 켜도 안 된다.
        ok('Settings → Pages' not in off_labs,
           'labs.html — "Pages 를 켜면 됩니다" 안내가 걷힌다')

        # ⑤ 히어로 통계도 사실에 맞게 바뀌는가
        ok('GitHub Pages 배포</span>' not in off_index,
           'index.html — "100% GitHub Pages 배포" 가 사라진다')

        # ⑥ 스위치를 껐다고 카드가 사라지면 안 된다
        eq(len(re.findall(r'<div class="no">HD-PROJECT', off_projects)), project_cards,
           'projects.html — 카드 수는 그대로다')
finally:
    shutil.rmtree(tmp, ignore_errors=True)


# ─────────────────────────────────────────── 6. 메뉴
group('6. 메뉴가 여덟 장에 똑같이 들어갔는가')

MENU_ITEM = re.compile(r'<li><a href="[^"]*"[^>]*>([^<]+)</a></li>')
home_menu = MENU_ITEM.findall(re.search(r'<ul class="topnav-links">(.*?)</ul>', home, re.S).group(1))
ok(len(home_menu) >= 5, '홈 메뉴 항목이 채워져 있다', str(home_menu))

for rel in PAGES:
    html = read(rel)
    m = re.search(r'<ul class="topnav-links">(.*?)</ul>', html, re.S)
    ok(m is not None, '%s — 상단 메뉴가 있다' % rel)
    if m:
        eq(MENU_ITEM.findall(m.group(1)), home_menu, '%s — 메뉴 항목이 홈과 같다' % rel)

    # 지금 보고 있는 장은 하나만 표시된다
    active = len(re.findall(r'aria-current="page"', html))
    ok(active <= 1, '%s — 현재 위치 표시가 하나 이하다' % rel, '%d개' % active)


# ─────────────────────────────────────────── 결과
print('\n' + ('X ' if failed else 'O ') + '%d 통과 / %d 실패' % (passed, failed))
sys.exit(1 if failed else 0)
