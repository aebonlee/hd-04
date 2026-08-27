# -*- coding: utf-8 -*-
"""
hd-04 페이지 생성기 — python3 build.py

메뉴가 일곱 페이지에 있으므로 **여기 한 곳에서만** 정의한다.
페이지 HTML 을 손으로 고치면 다시 구울 때 날아간다. 내용은 _parts/ 를 고칠 것.
"""
import os, re
from metablock import preserve

# ─── 전환 스위치 ────────────────────────────────────────────────────
#
# 저장소를 전부 private 으로 돌리는 날 **이 한 줄만 False 로 바꾸고 다시 구우면**
# 된다. 열여섯 장을 손으로 고칠 일이 없다.
#
# 왜 필요한가 — 무료 플랜에서는 private 저장소의 GitHub Pages 가 서비스되지
# 않는다. 그래서 전환하는 순간 카드의 "데모 열기"·"페이지 열기" 24개가 전부
# 죽는다. 링크가 남아 있으면 누르는 사람은 그것이 고장인지 의도인지 모른다.
#
# False 로 두면 이렇게 바뀐다.
#   · github.io 를 가리키는 단추를 **모두 뺀다** (저장소 단추는 남긴다)
#   · 두 섹션 머리에 왜 없어졌는지 적는다
#   · 히어로 통계의 "100% GitHub Pages 배포" 를 사실에 맞게 바꾼다
#   · 실습 섹션의 "Settings → Pages 에서 켜면 됩니다" 안내를 걷어낸다
#     (private 이면 켜도 안 된다 — 그대로 두면 틀린 안내가 된다)
#
# 저장소 단추는 남긴다. private 이어도 **권한이 있는 사람에게는 열리기** 때문이다.
# 대신 안내에 권한이 필요하다고 적는다.
PAGES_LIVE = True

HERE = os.path.dirname(os.path.abspath(__file__))
def _no_pages(html, name):
    """PAGES_LIVE 가 False 일 때 조각을 고쳐 준다.

    조각 파일(_parts/) 자체는 건드리지 않는다. **구울 때만** 바꾼다.
    그래야 스위치를 다시 True 로 돌리면 원래대로 돌아온다.

    개수를 세서 하나도 못 바꿨으면 소리 내어 죽는다. 조각의 표기가 바뀌면
    이 함수가 조용히 아무 일도 안 하게 되는데, 그러면 전환하는 날
    "고쳤다"고 믿은 채 죽은 링크가 그대로 나간다.
    """
    if name not in ('sec_labs', 'sec_projects'):
        return html

    # ① github.io 를 가리키는 단추를 뺀다 ("데모 열기" · "페이지 열기")
    html, n = re.subn(
        r'<a class="btn[^"]*" href="https://aebonlee\.github\.io/[^"]*"[^>]*>[^<]*</a>',
        '', html)
    assert n > 0, '%s: 뺄 github.io 단추를 못 찾았다' % name

    # ② 왜 없어졌는지 섹션 머리에 적는다. 없으면 "링크가 빠진 것"으로 보인다.
    note = ('\n      <div class="note"><b>저장소를 비공개로 돌리면서 '
            '"%s" 단추를 뺐습니다.</b> 무료 플랜에서는 비공개 저장소의 '
            'GitHub Pages 가 서비스되지 않아 주소가 열리지 않습니다. '
            '<b>저장소</b> 단추는 그대로 두었습니다 — 권한이 있는 계정으로 '
            '로그인하면 열립니다. 각자 클론해 둔 사본은 그대로 쓰실 수 있습니다.</div>'
            % ('페이지 열기' if name == 'sec_labs' else '데모 열기'))
    html, n = re.subn(r'(</h2>)', r'\1' + note.replace('\\', '\\\\'), html, count=1)
    assert n == 1, '%s: 안내를 넣을 </h2> 를 못 찾았다' % name

    # ③ 실습 섹션의 "Settings → Pages 에서 켜면 됩니다" 는 이제 틀린 안내다.
    #    private 이면 켜도 안 된다.
    if name == 'sec_labs':
        stale = ('<div class="note">실습 저장소의 "페이지 열기"는 해당 저장소의 '
                 'GitHub Pages 설정이 켜져 있을 때 동작합니다.')
        assert stale in html, 'sec_labs: 걷어낼 옛 안내를 못 찾았다'
        html = re.sub(re.escape(stale) + r'.*?</div>', '', html, count=1, flags=re.S)

    return html


def P(n):
    html = open(os.path.join(HERE, '_parts', n + '.html'), encoding='utf-8').read()
    return html if PAGES_LIVE else _no_pages(html, n)

HEAD      = P('head')
BODY_OPEN = P('body_open')
FOOT      = P('foot')

MENU = [
    ('labs',     '실습내역',        'labs.html'),
    ('projects', '프로젝트 소개',    'projects.html'),
    ('openai',   'OpenAI API Key',  'guide/openai.html'),
    ('claude',   'Claude API Key',  'guide/claude.html'),
    ('solar',    'Solar API Key',   'guide/solar.html'),
    ('gemini',   'Gemini API Key',  'guide/gemini.html'),
    ('supabase', 'Supabase 사용법',  'guide/supabase.html'),
]

def nav(active, root=''):
    items = []
    for key, label, href in MENU:
        cls = ' class="active" aria-current="page"' if key == active else ''
        items.append(f'      <li><a href="{root}{href}"{cls}>{label}</a></li>')
    return (
        '<nav class="topnav" aria-label="주요 메뉴">\n'
        '  <div class="wrap topnav-inner">\n'
        f'    <a class="topnav-brand" href="{root}index.html">HD 과정 총정리</a>\n'
        '    <ul class="topnav-links">\n' + '\n'.join(items) + '\n'
        '    </ul>\n'
        '  </div>\n'
        '</nav>'
    )

def hero(eyebrow, title, lede, stats_html=''):
    return (
        '<header class="hero">\n'
        '  <div class="wrap">\n'
        f'    <div class="eyebrow">{eyebrow}</div>\n'
        f'    <h1>{title}</h1>\n'
        f'    <p class="lede">{lede}</p>\n'
        f'{stats_html}'
        '  </div>\n'
        '</header>'
    )

def page(path, title, desc, active, hero_html, body, root=''):
    """페이지 하나를 굽는다.

    ⚠ 본문은 반드시 `<main>` 안에 넣는다. `<div>` 로 바꾸면 안 된다.
      위아래 여백이 `main { padding:44px 0 30px }` 한 곳에만 있어서,
      main 이 없으면 **히어로와 첫 제목이 붙어 버린다.**
      가로 여백은 `.wrap { padding:0 24px }` 가 따로 맡는다 — 둘을 한
      요소에 겹치면 `.wrap` 의 단축 속성이 세로 여백을 0 으로 되돌린다.
      (실제로 조각으로 쪼개면서 <main> 을 빠뜨려 세 페이지가 다 붙었다)
    """
    # 하위 폴더면 상대 경로를 한 단계 올린다
    head = HEAD.replace('href="css/', f'href="{root}css/') if root else HEAD
    html = f"""{head}<title>{title}</title>
<meta name="description" content="{desc}">
</head>{BODY_OPEN}

{nav(active, root)}

{hero_html}

<main>
<div class="wrap">
{body}
</div>
</main>

{FOOT}
"""
    full = os.path.join(HERE, path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    # 저장소 밖 스크립트가 넣어 둔 HD:META 블록을 되돌려 넣는다 (metablock.py 주석 참조).
    # 이걸 안 하면 다시 구울 때마다 파비콘·OG 메타가 통째로 사라진다.
    html = preserve(full, html)
    open(full, 'w', encoding='utf-8').write(html)
    print(f'  {path}: {len(html):,}자')

# ── HEAD 에서 기존 title/description 을 걷어낸다(중복 방지) ────────────
HEAD = re.sub(r'<title>.*?</title>\s*', '', HEAD, flags=re.S)
HEAD = re.sub(r'<meta name="description"[^>]*>\s*', '', HEAD)

# 마지막 타일만 스위치를 탄다. 비공개로 돌리면 Pages 가 서지 않으므로
# "100% GitHub Pages 배포" 가 거짓이 된다.
_DEPLOY_STAT = ('      <div class="stat"><b>100%</b><span>GitHub Pages 배포</span></div>'
                if PAGES_LIVE else
                '      <div class="stat"><b>100%</b><span>클론해서 바로 실행</span></div>')

STATS = '''    <div class="stats">
      <div class="stat"><b>7</b><span>실습 저장소</span></div>
      <div class="stat"><b>17</b><span>수강생 프로젝트</span></div>
      <div class="stat"><b>4+2</b><span>실습 4일 + 프로젝트 2일</span></div>
''' + _DEPLOY_STAT + '''
    </div>
'''

# ── 홈 ────────────────────────────────────────────────────────────────
HOME_BODY = P('sec_curriculum') + '''
    <section>
      <h2>어디로 갈까요</h2>
      <p class="sec-sub">과정 산출물은 성격이 둘로 나뉩니다.</p>
      <div class="cards">
        <div class="card">
          <div class="no">수업 중 함께 만든 것</div>
          <h3>실습내역</h3>
          <p class="lead">4일간 Claude Code 로 함께 만든 저장소 7개입니다.
            정적 페이지부터 Supabase 연동까지 단계별로 쌓아 올렸습니다.</p>
          <div class="links"><a class="btn primary" href="labs.html">실습내역 보기</a></div>
        </div>
        <div class="card">
          <div class="no">각자 기획해 만든 것</div>
          <h3>프로젝트 소개</h3>
          <p class="lead">수강생이 직접 쓴 기획서를 작업 지시서로 옮겨 개발한
            실전 업무 도구 17종입니다. 각자의 실제 업무 문제를 풀었습니다.</p>
          <div class="links"><a class="btn blue" href="projects.html">프로젝트 보기</a></div>
        </div>
      </div>
    </section>
'''

page('index.html',
     '생성형 AI 업무자동화 전문가과정 — 저장소 총정리',
     '현대건설기계 생성형 AI 업무자동화 전문가과정 1차수의 실습 저장소와 수강생 프로젝트 총정리',
     None,
     hero('HD 생성형 AI 업무자동화 전문가과정 · 1차수',
          '실습 &amp; 프로젝트 저장소 총정리',
          '현대건설 생성형 AI 업무자동화 전문가과정에서 Claude Code로 진행한 4일간의 실습 저장소(hd-01~08)와,<br>'
          '수강생 기획서를 기반으로 개발한 실전 프로젝트(hd-project01~16 · 17)를 한 페이지에 정리했습니다.',
          STATS),
     HOME_BODY)

# ── 실습내역 ──────────────────────────────────────────────────────────
page('labs.html',
     '실습내역 — HD 생성형 AI 업무자동화 전문가과정',
     '수업 중 Claude Code 로 함께 만든 실습 저장소 hd-01~hd-08',
     'labs',
     hero('수업 중 함께 만든 것', '실습내역',
          '4일간 Claude Code 로 함께 만든 저장소입니다. 정적 웹페이지에서 시작해 '
          'Supabase 연동, 실전 대시보드까지 단계별로 쌓아 올렸습니다.'),
     P('sec_labs'))

# ── 프로젝트 소개 ─────────────────────────────────────────────────────
page('projects.html',
     '프로젝트 소개 — HD 생성형 AI 업무자동화 전문가과정',
     '수강생이 직접 기획해 개발한 실전 업무 도구 17종',
     'projects',
     hero('각자 기획해 만든 것', '수강생 프로젝트',
          '수강생이 직접 쓴 프로젝트 기획서를 Claude Code 작업 지시서로 옮겨 개발한 '
          '실전 업무 도구 17종입니다. 각자의 실제 업무 문제를 풀었습니다.'),
     P('sec_projects'))

print('\n안내 페이지 메뉴 조각도 갱신')
for key, _, _ in MENU[2:]:
    open(os.path.join(HERE, '_parts', f'nav_{key}.html'), 'w', encoding='utf-8').write(nav(key, '../'))
