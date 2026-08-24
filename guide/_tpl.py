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
  .guide {{ max-width: 860px; }}
  .guide h2 {{ margin-top: 36px; }}
  .guide h3 {{ margin-top: 24px; }}
  .guide ol, .guide ul {{ padding-left: 20px; line-height: 1.85; }}
  .guide li {{ margin-bottom: 6px; }}
  .guide pre {{ font-size: 12.5px; }}
  .guide .warn {{
    border-left: 4px solid #c8341f; background: #fdeae7; color: #7a1a0c;
    padding: 14px 16px; border-radius: 8px; margin: 18px 0; font-size: 14px; line-height: 1.7;
  }}
  .guide .tip {{
    border-left: 4px solid #0a6b34; background: #f0f7f2; color: #08422a;
    padding: 14px 16px; border-radius: 8px; margin: 18px 0; font-size: 14px; line-height: 1.7;
  }}
  .guide table {{ font-size: 13.5px; margin: 14px 0; }}
  .steps {{ counter-reset: s; list-style: none; padding-left: 0; }}
  .steps > li {{ counter-increment: s; position: relative; padding-left: 38px; margin-bottom: 16px; }}
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

<div class="wrap guide">
{body}
  <p style="margin:40px 0 0"><a href="../index.html">← 저장소 총정리로 돌아가기</a></p>
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
