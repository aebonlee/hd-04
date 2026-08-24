# 안내 페이지 생성기 — 네 페이지가 같은 틀을 쓰도록 여기서 한 번에 만든다.
# 페이지를 손으로 고치면 다음에 다시 구울 때 날아간다. 내용은 아래 PAGES 를 고칠 것.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
STYLE = open('/tmp/shared_style.css', encoding='utf-8').read()

def page(slug, title, desc, nav, body):
    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title} — HD 생성형 AI 업무자동화 전문가과정</title>
<meta name="description" content="{desc}">
<style>{STYLE}</style>
<link rel="stylesheet" href="../css/hd-theme.css">
<style>
  /* ⚠ hd-theme.css 뒤에 와야 한다 — 메뉴의 <a> 에는 클래스가 없어
     테마의 a:not([class]) 규칙이 강조색을 주고, 그 색이 메뉴 배경과 같은 계열이라
     대비 1.24 로 글자가 묻힌다. */
  .hd.hd-app .topnav-links a,
  .hd.hd-app .topnav-links a:visited {{ color: rgba(255, 255, 255, .82); }}
  .hd.hd-app .topnav-links a:hover   {{ color: #ffffff; }}
  .hd.hd-app .topnav-links a.active  {{ color: #ffffff; border-bottom-color: #7ec8a0; }}
  .hd.hd-app .topnav-brand,
  .hd.hd-app .topnav-brand:visited   {{ color: #ffffff; }}
  .hd.hd-app .topnav-brand:hover     {{ color: #cfe0ee; }}

  /* 폭·제목·목록 간격은 공통 테마의 세로 리듬이 잡는다.
     여기서 또 정하면 값이 두 곳으로 갈려 다음 사람이 어디를 고쳐야 할지 모른다. */
  .guide pre {{ font-size: 12.5px; }}
  /* 안내 띠 — 위아래 간격은 테마(--sp-3)가 잡으므로 색과 안쪽 여백만 정한다 */
  .guide .warn {{
    border-left: 4px solid #c8341f; background: #fdeae7; color: #7a1a0c;
    padding: 16px 18px; border-radius: 8px; font-size: 14px; line-height: 1.75;
  }}
  .guide .tip {{
    border-left: 4px solid #0a6b34; background: #f0f7f2; color: #08422a;
    padding: 16px 18px; border-radius: 8px; font-size: 14px; line-height: 1.75;
  }}
  .guide .warn > :last-child, .guide .tip > :last-child {{ margin-bottom: 0; }}
  .guide table {{ font-size: 13.5px; }}
  .steps {{ counter-reset: s; list-style: none; padding-left: 0; }}
  .steps > li {{ counter-increment: s; position: relative; padding-left: 38px; margin-bottom: var(--sp-2); }}
  .steps > li::before {{
    content: counter(s); position: absolute; left: 0; top: 1px;
    width: 25px; height: 25px; border-radius: 50%; background: var(--accent); color: #fff;
    font-size: 13px; font-weight: 700; display: flex; align-items: center; justify-content: center;
  }}
</style>
</head>
<body class="hd hd-app">

{nav}

<header class="hero">
  <div class="wrap">
    <div class="eyebrow">사용 안내</div>
    <h1>{title}</h1>
    <p class="lede">{desc}</p>
  </div>
</header>

<div class="wrap guide" style="padding-top:var(--sp-5);padding-bottom:var(--sp-5)">
{body}
  <p style="margin:var(--sp-5) 0 0"><a href="../index.html">← 저장소 총정리로 돌아가기</a></p>
</div>

<footer class="foot">
  <div class="wrap">
    <p>HD 생성형 AI 업무자동화 전문가과정 1차수 · 현대건설기계</p>
    <p class="small">문의 dreamitbiz@naver.com · 010-2612-4256 · 카카오톡 aebon</p>
  </div>
</footer>

</body>
</html>
"""
