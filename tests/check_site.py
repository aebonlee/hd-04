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

# 칩의 범위(hd-project01 ~ hd-projectNN)도 카드 수와 맞아야 한다
m = re.search(r'hd-project01 ~ hd-project(\d+)', projects)
ok(m is not None, '프로젝트 칩에 범위가 적혀 있다')
if m:
    eq(int(m.group(1)), project_cards, '칩의 마지막 번호 == 프로젝트 카드 수')

# 본문 곳곳의 "N종" 표기도 같아야 한다
for rel, html in (('index.html', home), ('projects.html', projects)):
    for n in set(re.findall(r'실전 업무 도구 (\d+)종', html)):
        eq(int(n), project_cards, '%s — "실전 업무 도구 %s종" 표기가 카드 수와 맞는다' % (rel, n))

m = re.search(r'<b>(\d+)개 프로젝트 모두', projects)
if m:
    eq(int(m.group(1)), project_cards, '하단 안내의 "N개 프로젝트" 가 카드 수와 맞는다')


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
    ok(demo is not None, 'HD-PROJECT%s — 데모 링크가 있다' % no)
    ok(repo is not None, 'HD-PROJECT%s — 저장소 링크가 있다' % no)
    if demo and repo:
        # 카드를 복사해 만들면서 번호 하나를 안 고치는 것이 가장 흔한 실수다
        eq((demo.group(1), repo.group(1)), (no, no),
           'HD-PROJECT%s — 데모·저장소 링크가 같은 번호를 가리킨다' % no)

eq(len(seen), len(set(seen)), '프로젝트 번호가 중복되지 않는다')
eq(seen, ['%02d' % i for i in range(1, len(seen) + 1)],
   '프로젝트 번호가 01부터 빠짐없이 이어진다')
eq(len(seen), project_cards, '번호가 붙은 카드 수 == 전체 카드 수')


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
