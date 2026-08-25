# 안내 페이지 생성기 — 네 페이지가 같은 틀을 쓰도록 여기서 한 번에 만든다.
# 페이지를 손으로 고치면 다음에 다시 구울 때 날아간다. 내용은 아래 PAGES 를 고칠 것.
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
# 공용 스타일의 정본은 _parts/head.html 이다.
#
# ⚠ 그 파일에는 <style> 이 **두 덩이** 있고 순서에 뜻이 있다.
#     1) hd-theme.css **앞**  — 이 사이트의 기본 뼈대
#     2) hd-theme.css **뒤**  — 테마에 지는 것을 되돌리는 규칙
#   앞의 것만 가져오면 2)가 통째로 빠진다. 실제로 그렇게 되어 있어서
#   안내 페이지만 메뉴 세로 정렬이 12px 어긋나 있었다.
#   (예전에는 2)를 여기에 손으로 베껴 뒀는데, 한쪽만 고쳐져 갈라졌다.
#    베끼지 말고 읽어 올 것 — 두 곳에 같은 규칙을 두면 반드시 어긋난다.)
import re as _re
_head = open(os.path.join(os.path.dirname(HERE), '_parts', 'head.html'), encoding='utf-8').read()
# ⚠ 주석을 먼저 걷어낸다. head.html 의 HTML 주석 안에 `<style>` 이라는 **글자**가
#   들어 있어서, 그냥 찾으면 정규식이 거기서부터 뜬다. 그러면 두 번째 덩이가
#   `--> <link ...> <style>` 로 시작하는 쓰레기가 되고, 그 글자를 CSS 로 읽던
#   브라우저가 오류 복구를 하면서 **뒤따르는 규칙 몇 개를 통째로 삼킨다.**
#   눈에는 "왜 이 규칙만 안 먹지"로만 보인다. 실제로 그래서 메뉴 ul 여백이 남았다.
_clean = _re.sub(r'<!--.*?-->', '', _head, flags=_re.S)
_blocks = _re.findall(r'<style>(.*?)</style>', _clean, _re.S)
assert len(_blocks) == 2, '_parts/head.html 의 <style> 이 %d 덩이다 — 순서를 다시 확인할 것' % len(_blocks)
for _b in _blocks:
    assert '<style' not in _b and '<link' not in _b, 'CSS 안에 태그가 섞였다 — 주석 제거가 안 먹었다'
STYLE, STYLE_AFTER = _blocks[0], _blocks[1]

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
<style>{STYLE_AFTER}</style>
<style>
  /* 안내 페이지에만 필요한 것. 메뉴·카드 등 공통 규칙은
     _parts/head.html 이 정본이라 여기에 다시 적지 않는다. */
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
  /* 번호 단계는 한 항목이 여러 줄이라 일반 목록(8px)보다 벌려야 경계가 보인다.
     테마의 `.hd.hd-app li` 가 (0,2,1) 이므로 여기도 그만큼 올려야 이긴다. */
  .hd.hd-app .steps > li {{
    counter-increment: s; position: relative; padding-left: 38px;
    margin-bottom: var(--sp-3);
  }}
  .hd.hd-app .steps > li:last-child {{ margin-bottom: 0; }}
  .hd.hd-app .steps {{ margin-bottom: var(--sp-3); }}
  .hd.hd-app .steps > li::before {{
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
