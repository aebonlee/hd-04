# -*- coding: utf-8 -*-
"""
hd-04 페이지 생성기 — python3 build.py

메뉴가 일곱 페이지에 있으므로 **여기 한 곳에서만** 정의한다.
페이지 HTML 을 손으로 고치면 다시 구울 때 날아간다. 내용은 _parts/ 를 고칠 것.
"""
import os, re
from metablock import preserve

HERE = os.path.dirname(os.path.abspath(__file__))
P = lambda n: open(os.path.join(HERE, '_parts', n + '.html'), encoding='utf-8').read()

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

STATS = '''    <div class="stats">
      <div class="stat"><b>7</b><span>실습 저장소</span></div>
      <div class="stat"><b>15</b><span>수강생 프로젝트</span></div>
      <div class="stat"><b>4+2</b><span>실습 4일 + 프로젝트 2일</span></div>
      <div class="stat"><b>100%</b><span>GitHub Pages 배포</span></div>
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
            실전 업무 도구 15종입니다. 각자의 실제 업무 문제를 풀었습니다.</p>
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
          '수강생 기획서를 기반으로 개발한 실전 프로젝트(hd-project01~14 · 17)를 한 페이지에 정리했습니다.',
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
     '수강생이 직접 기획해 개발한 실전 업무 도구 15종',
     'projects',
     hero('각자 기획해 만든 것', '수강생 프로젝트',
          '수강생이 직접 쓴 프로젝트 기획서를 Claude Code 작업 지시서로 옮겨 개발한 '
          '실전 업무 도구 15종입니다. 각자의 실제 업무 문제를 풀었습니다.'),
     P('sec_projects'))

print('\n안내 페이지 메뉴 조각도 갱신')
for key, _, _ in MENU[2:]:
    open(os.path.join(HERE, '_parts', f'nav_{key}.html'), 'w', encoding='utf-8').write(nav(key, '../'))
