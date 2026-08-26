# -*- coding: utf-8 -*-
"""
HD:META 블록 보존 — build.py 와 guide/gen.py 가 함께 쓴다.

여덟 페이지의 <head> 에는 파비콘·canonical·OG·twitter 메타가
`<!-- === HD:META:BEGIN === -->` ~ `<!-- === HD:META:END === -->` 사이에 들어 있다.
이 블록은 **저장소 밖의 스크립트**가 넣어 둔 것이라 두 생성기가 알지 못한다.

그래서 예전에는 페이지를 다시 구울 때마다 여덟 장에서 이 블록이 통째로 사라졌다.
눈에 띄지 않는 손실이다 — 화면은 멀쩡하고, 카카오톡·슬랙에 링크를 붙였을 때에야
미리보기가 안 뜨는 것으로 드러난다.

그래서 굽기 직전에 **기존 파일에서 블록을 꺼내 되돌려 넣는다.**
블록이 없던 파일(새 페이지)은 그대로 둔다.

⚠ 이 블록의 **문구에는 원본이 없다.** 구운 HTML 안에만 산다.
   보존만 하므로 다시 굽는다고 갱신되지 않는다 — 고치려면 페이지 파일의
   블록을 직접 손봐야 한다. 다른 내용은 `_parts/` 를 고치라고 되어 있어서
   여기만 예외다.

   실제로 프로젝트가 13개가 되도록 og:title 이 "수강생 프로젝트 12종" 인 채로
   남아 있었다. 화면에는 안 보이고 **카카오톡·슬랙에 링크를 붙였을 때만**
   드러나는 자리라 아무도 눈치채지 못했다.
   지금은 tests/check_site.py 가 구운 페이지까지 훑어 이 어긋남을 잡는다.
"""
import io
import os
import re

BEGIN = 'HD:META:BEGIN'
END = 'HD:META:END'

_BLOCK = re.compile(r'<!--\s*=+\s*' + BEGIN + r'.*?' + END + r'\s*=+\s*-->\n?', re.S)
_DESC = re.compile(r'(<meta name="description" content="[^"]*">\n?)')
# 블록이 description 바로 뒤에 붙어 있는가 — 총정리 세 장이 그렇다
_AFTER_DESC = re.compile(
    r'<meta name="description" content="[^"]*">\s*<!--\s*=+\s*' + BEGIN, re.S)


def extract(path):
    """기존 파일에서 HD:META 블록을 꺼낸다. 없으면 None."""
    if not os.path.exists(path):
        return None
    old = io.open(path, encoding='utf-8').read()
    m = _BLOCK.search(old)
    return m.group(0) if m else None


def preserve(path, html):
    """
    새로 구운 html 에 기존 파일의 HD:META 블록을 **원래 자리에** 되돌려 넣는다.

    자리가 페이지마다 다르다.
      · 총정리(index·labs·projects) — <meta name="description"> 바로 뒤
      · 안내(guide/*)              — </head> 직전
    아무 데나 넣어도 브라우저는 읽지만, 그러면 다시 구울 때마다 20줄이 위아래로
    옮겨 다니며 diff 를 채운다. 실제로 바뀐 것이 무엇인지 안 보이게 된다.
    """
    if not os.path.exists(path):
        return html
    old = io.open(path, encoding='utf-8').read()
    m = _BLOCK.search(old)
    if not m:
        return html
    if BEGIN in html:          # 이미 들어 있으면 건드리지 않는다
        return html

    block = m.group(0)
    if not block.endswith('\n'):
        block += '\n'

    if _AFTER_DESC.search(old):
        new, n = _DESC.subn(lambda d: d.group(1) + block, html, count=1)
        where = '<meta name="description">'
    else:
        new, n = re.subn(r'</head>', block + '</head>', html, count=1)
        where = '</head>'

    if n != 1:
        # 조용히 블록을 잃는 것보다 멈추는 편이 낫다.
        raise SystemExit(
            '%s: %s 를 찾지 못해 HD:META 블록을 되돌릴 수 없습니다.\n'
            '  블록을 잃지 않으려면 이 자리를 먼저 확인하세요.' % (path, where))
    return new
