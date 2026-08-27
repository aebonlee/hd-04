# hd-04 — 교육과정 총정리 페이지

> 🌐 **배포 페이지: [https://aebonlee.github.io/hd-04/](https://aebonlee.github.io/hd-04/)** · 저장소: https://github.com/aebonlee/hd-04

HD 생성형 AI 업무자동화 전문가과정(1차수, 현대건설)에서 사용된 저장소를 한 페이지로 정리한 정적 안내 사이트입니다.

- 실습 저장소: hd-01 ~ hd-08 (7개 실습 — 04번은 이 총정리 페이지)
- 수강생 프로젝트: hd-project01~16 · 17 (기획서 기반 실전 업무 도구 17종)

배포: https://aebonlee.github.io/hd-04/ (main 푸시 시 gh-pages 브랜치로 자동 게시)

## 고치는 법

페이지 HTML 을 손으로 고치지 마세요 — 다시 구우면 날아갑니다.
내용은 `_parts/` 를, 메뉴는 `build.py` 의 `MENU` 를, 안내 페이지는 `guide/gen.py` 를 고칩니다.

```bash
python3 build.py        # index.html · labs.html · projects.html · _parts/nav_*.html
python3 guide/gen.py    # guide/*.html
```

### 저장소를 비공개로 돌리는 날

`build.py` 첫머리의 **`PAGES_LIVE = True` 한 줄을 `False` 로 바꾸고 다시 구우면**
됩니다. 카드 스물네 장을 손으로 고칠 일이 없습니다.

무료 플랜에서는 비공개 저장소의 GitHub Pages 가 서비스되지 않습니다.
그래서 전환하는 순간 「데모 열기」·「페이지 열기」 24개가 전부 죽는데,
링크가 남아 있으면 누르는 사람은 그것이 고장인지 의도인지 모릅니다.

`False` 로 두면 굽는 동안 이렇게 바뀝니다 (조각 파일 자체는 건드리지 않으므로
`True` 로 돌리면 원래대로 돌아옵니다).

| | |
|---|---|
| github.io 를 가리키는 단추 | **전부 뺍니다** |
| 저장소 단추 | **남깁니다** — 비공개여도 권한이 있으면 열립니다 |
| 두 섹션 머리 | 왜 없어졌는지 적습니다 |
| 실습 섹션의 "Settings → Pages 에서 켜면 됩니다" | 걷어냅니다 (비공개면 켜도 안 됩니다) |
| 히어로 통계 "100% GitHub Pages 배포" | "100% 클론해서 바로 실행" 으로 |

`tests/check_site.py` 가 **끈 판을 실제로 구워 봅니다.** 아무도 눌러 보지 않은
스위치는 정작 필요한 날 안 돕니다.

`<head>` 의 `HD:META` 블록(파비콘 · canonical · OG · twitter)은 저장소 밖 스크립트가
넣어 둔 것이라 두 생성기가 알지 못합니다. 그래서 굽기 직전에 기존 파일에서 꺼내
**원래 자리에 되돌려 넣습니다** (`metablock.py`). 예전에는 다시 구울 때마다
여덟 장에서 이 20줄이 통째로 사라졌고, 화면은 멀쩡해서 카카오톡에 링크를
붙여 보고서야 알았습니다.

## 검사

```bash
python3 tests/check_site.py     # 258 통과 — 다시 구워도 같은가 · 숫자 · 링크 · 메뉴
node    tests/check_browser.js  #  66 통과 — 대비 · 여백 · 정렬 (playwright 필요)
```

`tests/check_site.py` 는 임시 폴더에 저장소를 복사해 두 생성기를 돌린 뒤
커밋된 HTML 과 한 글자까지 비교합니다. 페이지를 손으로 고쳤거나 생성기가
무언가를 잃고 있으면 여기서 걸립니다.

`tests/check_browser.js` 는 지금까지 실제로 깨졌던 자리를 숫자로 고정합니다 —
메뉴 글자 대비(예전에 1.24까지 떨어져 글자가 사라졌습니다), 히어로와 본문 사이 여백,
같은 줄 카드의 윗선. playwright 가 없으면 조용히 건너뜁니다.

둘 다 `.github/workflows/test.yml` 이 PR 마다 돌립니다.
`main` 브랜치 보호에서 「필수 상태 체크」로 걸 수 있는 체크가 이 `test` 잡입니다.
