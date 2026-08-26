/**
 * 화면 검사 — node tests/check_browser.js  (playwright 필요)
 *
 * 이 저장소가 실제로 깨진 방식은 거의 전부 CSS 였다. 커밋 기록에 그대로 남아 있다.
 *
 *   · 상단 메뉴 글자가 배경에 묻혔다 — 대비 1.24 로, 선택된 항목만 읽혔다
 *   · <main> 을 <div> 로 바꾸는 바람에 위아래 여백이 통째로 빠져
 *     히어로와 첫 제목이 붙었다
 *   · 같은 줄 카드인데 첫 칸만 높이를 채우고 나머지가 22px 밀렸다
 *   · 히어로 통계 상자가 흰 면으로 덮여 흰 글자가 사라졌다
 *
 * 이런 것은 파일을 읽어서는 잡히지 않는다. **브라우저에서 재야** 잡힌다.
 * 그래서 여기서는 눈으로 보던 것을 숫자로 바꿔 고정한다.
 *
 * playwright 가 없으면 조용히 건너뛴다 — 이것 하나 때문에 검사 전체가 막히면
 * 아무도 안 돌리게 된다. CI 에서는 설치하고 돌린다.
 */
'use strict';

var http = require('http');
var fs = require('fs');
var path = require('path');

var ROOT = path.join(__dirname, '..');
var PORT = 8794;

var PAGES = [
  'index.html', 'labs.html', 'projects.html',
  'guide/openai.html', 'guide/claude.html', 'guide/solar.html',
  'guide/gemini.html', 'guide/supabase.html'
];

var TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.png': 'image/png'
};

var pass = 0, fail = 0;
function ok(cond, label, detail) {
  if (cond) { pass++; return; }
  fail++;
  console.error('  X ' + label);
  if (detail) console.error('      ' + detail);
}
function group(n) { console.log('\n' + n); }

var chromium;
try {
  chromium = require('playwright').chromium;
} catch (e) {
  console.log('playwright 가 없어 화면 검사를 건너뜁니다 (CI 에서는 설치 후 돌립니다).');
  process.exit(0);
}

var server = http.createServer(function (req, res) {
  var rel = decodeURIComponent(req.url.split('?')[0]);
  if (rel === '/') rel = '/index.html';
  var file = path.join(ROOT, rel);
  if (file.indexOf(ROOT) !== 0 || !fs.existsSync(file) || fs.statSync(file).isDirectory()) {
    res.writeHead(404); res.end('not found'); return;
  }
  res.writeHead(200, { 'Content-Type': TYPES[path.extname(file)] || 'application/octet-stream' });
  fs.createReadStream(file).pipe(res);
});

/* 브라우저 안에서 도는 함수 — 색을 합성해 실제 대비를 잰다.
   투명도가 섞인 색(rgba(255,255,255,.82))과 그러데이션 배경을 그대로 다룬다. */
var MEASURE = function () {
  function parse(c) {
    var m = /rgba?\(([^)]+)\)/.exec(c);
    if (!m) return null;
    var v = m[1].split(',').map(function (x) { return parseFloat(x); });
    return { r: v[0], g: v[1], b: v[2], a: v.length > 3 ? v[3] : 1 };
  }
  function over(fg, bg) {                       // fg 를 bg 위에 얹는다
    var a = fg.a;
    return { r: fg.r * a + bg.r * (1 - a),
             g: fg.g * a + bg.g * (1 - a),
             b: fg.b * a + bg.b * (1 - a), a: 1 };
  }
  function lum(c) {
    var f = [c.r, c.g, c.b].map(function (v) {
      v /= 255;
      return v <= 0.03928 ? v / 12.92 : Math.pow((v + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * f[0] + 0.7152 * f[1] + 0.0722 * f[2];
  }
  function ratio(a, b) {
    var la = lum(a), lb = lum(b);
    return (Math.max(la, lb) + 0.05) / (Math.min(la, lb) + 0.05);
  }

  /** 이 요소 뒤에 실제로 깔린 색들. 그러데이션이면 각 색 정지점을 모두 돌려준다. */
  function backgrounds(el) {
    var layers = [], bases = [{ r: 255, g: 255, b: 255, a: 1 }];
    for (var n = el; n; n = n.parentElement) {
      var s = getComputedStyle(n);
      if (s.backgroundImage && s.backgroundImage !== 'none') {
        var stops = (s.backgroundImage.match(/rgba?\([^)]+\)/g) || [])
          .map(parse).filter(Boolean);
        if (stops.length) { bases = stops; break; }
      }
      var c = parse(s.backgroundColor);
      if (c && c.a > 0) {
        if (c.a >= 1) { bases = [c]; break; }
        layers.push(c);
      }
    }
    return bases.map(function (base) {
      var out = base;
      for (var i = layers.length - 1; i >= 0; i--) out = over(layers[i], out);
      return out;
    });
  }

  /** 가장 나쁜 대비. 그러데이션 위 글자는 어두운 쪽·밝은 쪽 둘 다 봐야 한다. */
  function contrast(el) {
    var fg = parse(getComputedStyle(el).color);
    if (!fg) return null;
    var worst = Infinity;
    backgrounds(el).forEach(function (bg) {
      worst = Math.min(worst, ratio(over(fg, bg), bg));
    });
    return Math.round(worst * 100) / 100;
  }

  function rect(el) { return el.getBoundingClientRect(); }
  function texts(sel) { return [].slice.call(document.querySelectorAll(sel)); }

  var navLinks = texts('.topnav-links a');
  var statLabels = texts('.stats .stat b, .stats .stat span');
  var lede = document.querySelector('.hero .lede');
  var main = document.querySelector('main') || document.querySelector('.guide');
  var hero = document.querySelector('.hero');

  /* 같은 줄에 놓인 카드들의 윗선이 맞는가.
     줄은 **왼쪽 좌표가 되돌아가는 지점**으로 가른다. top 으로 묶으면
     밀려난 카드끼리 다시 한 묶음이 되어, 어긋난 것이 도리어 정렬된 것으로 읽힌다
     (실제로 이 검사를 그렇게 썼다가 일부러 낸 어긋남을 놓쳤다). */
  var rows = [];
  texts('.cards').forEach(function (grid) {
    var row = [], prevLeft = -Infinity;
    [].slice.call(grid.children).forEach(function (c) {
      if (!c.classList.contains('card')) return;
      var r = rect(c);
      if (r.left <= prevLeft + 1 && row.length) { rows.push(row); row = []; }
      prevLeft = r.left;
      row.push(Math.round(r.top));
    });
    if (row.length) rows.push(row);
  });

  return {
    navLinkContrast: navLinks.map(contrast),
    navLinkCount: navLinks.length,
    statContrast: statLabels.map(contrast),
    ledeContrast: lede ? contrast(lede) : null,
    heroBottom: hero ? rect(hero).bottom : null,
    firstContentTop: main && main.firstElementChild
      ? rect(main.firstElementChild).top : null,
    cardRowSpread: rows.map(function (v) {
      return Math.max.apply(null, v) - Math.min.apply(null, v);
    }),
    h1Count: document.querySelectorAll('h1').length,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth
  };
};

server.listen(PORT, '127.0.0.1', function () {
  run().then(function () {
    server.close();
    console.log('\n' + (fail ? 'X ' : 'O ') + pass + ' 통과 / ' + fail + ' 실패');
    process.exit(fail ? 1 : 0);
  }).catch(function (e) {
    server.close();
    console.error(e);
    process.exit(1);
  });
});

async function run() {
  var launch = {};
  if (process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE) {
    launch.executablePath = process.env.PLAYWRIGHT_CHROMIUM_EXECUTABLE;
  }
  var browser = await chromium.launch(launch);
  var page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

  var errors = [];
  page.on('pageerror', function (e) { errors.push(String(e.message)); });

  group('1. 여덟 장이 모두 뜬다');
  for (var i = 0; i < PAGES.length; i++) {
    var res = await page.goto('http://127.0.0.1:' + PORT + '/' + PAGES[i],
                              { waitUntil: 'networkidle' });
    ok(res && res.status() === 200, PAGES[i] + ' — 200 으로 열린다');
  }
  ok(errors.length === 0, '자바스크립트 오류가 없다', errors.join(' | '));

  group('2. 대비 · 여백 · 정렬 — 브라우저에서 실제로 잰다');
  for (var j = 0; j < PAGES.length; j++) {
    await page.goto('http://127.0.0.1:' + PORT + '/' + PAGES[j], { waitUntil: 'networkidle' });
    await page.waitForTimeout(120);
    var m = await page.evaluate(MEASURE);

    ok(m.navLinkCount >= 5, PAGES[j] + ' — 메뉴 항목이 있다', String(m.navLinkCount));
    var worstNav = Math.min.apply(null, m.navLinkContrast);
    ok(worstNav >= 4.5, PAGES[j] + ' — 메뉴 글자 대비가 4.5 이상',
       '가장 나쁜 값 ' + worstNav);

    if (m.ledeContrast !== null) {
      ok(m.ledeContrast >= 4.5, PAGES[j] + ' — 히어로 설명 글자 대비가 4.5 이상',
         String(m.ledeContrast));
    }
    if (m.statContrast.length) {
      var worstStat = Math.min.apply(null, m.statContrast);
      ok(worstStat >= 4.5, PAGES[j] + ' — 히어로 통계 글자 대비가 4.5 이상',
         '가장 나쁜 값 ' + worstStat);
    }

    layout(PAGES[j], m);
  }

  group('3. 좁은 화면에서 가로로 밀리지 않는다');
  await page.setViewportSize({ width: 390, height: 844 });
  for (var k = 0; k < PAGES.length; k++) {
    await page.goto('http://127.0.0.1:' + PORT + '/' + PAGES[k], { waitUntil: 'networkidle' });
    await page.waitForTimeout(120);
    var over = await page.evaluate(function () {
      return document.documentElement.scrollWidth - document.documentElement.clientWidth;
    });
    ok(over <= 1, PAGES[k] + ' — 390px 에서 가로 스크롤이 없다', over + 'px 넘침');
  }

  await browser.close();

  function layout(name, m) {
    // 히어로와 첫 제목이 붙어 버리던 자리
    if (m.heroBottom !== null && m.firstContentTop !== null) {
      var gap = Math.round(m.firstContentTop - m.heroBottom);
      ok(gap >= 20, name + ' — 히어로와 본문 첫 요소 사이가 20px 이상',
         gap + 'px (main 의 위아래 여백이 빠졌을 수 있습니다)');
    }
    // 같은 줄 카드의 윗선이 어긋나던 자리
    var spread = m.cardRowSpread.length ? Math.max.apply(null, m.cardRowSpread) : 0;
    ok(spread <= 2, name + ' — 같은 줄 카드의 윗선이 맞는다', spread + 'px 어긋남');
    ok(m.h1Count === 1, name + ' — h1 이 하나다', m.h1Count + '개');
  }
}
