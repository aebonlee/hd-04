#!/usr/bin/env node
/**
 * check-offline.mjs — 폐쇄망에서 깨질 곳을 찾는다
 *
 * 잡으려는 것은 하나다: **페이지를 여는 데 바깥이 필요한가.**
 *
 * 등급을 나눈다. 다 같은 무게가 아니다.
 *   막힘(blocking) — 이게 있으면 화면이 안 뜬다. 반드시 0이어야 한다.
 *       <link rel=stylesheet href=바깥>   ← 화면 그리기를 막는다
 *       <script src=바깥>                  ← 파싱을 막는다 (async/defer 여도 실행 순서가 깨진다)
 *       @import url(바깥)                  ← 위와 같다
 *       import … from '바깥'               ← 모듈이 통째로 안 뜬다
 *   깨짐(broken) — 화면은 뜨는데 그 자리만 빈다.
 *       <img src=바깥>, url(바깥) 배경
 *   선택(optional) — 사람이 눌렀을 때만 부른다. 폐쇄망이면 그 기능만 못 쓴다.
 *       fetch('https://api.…')  ← AI 인식 같은 것
 *
 * ⚠ 이 검사기를 만들며 밟은 함정
 *   - XML 네임스페이스(`http://schemas.openxmlformats.org/…`)는 **문자열**이지 요청이 아니다.
 *     xlsx·docx 라이브러리 안에 수십 개씩 들어 있어서, 안 거르면 결과가 통째로 가짜가 된다.
 *   - `<a href=바깥>` 은 사람이 눌러야 간다. 페이지를 여는 것과 무관하다.
 *   - 주석 안의 URL 은 요청이 아니다. "원본 CDN: …" 같은 출처 메모가 실제로 있다.
 *   - `+esm` 번들은 **자체 완결이 아니다.** 파일 안에서 또 바깥을 부른다.
 *     동봉한 파일 자신도 검사 대상에 넣어야 이걸 잡는다.
 */
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join, relative, extname } from 'node:path';

const ROOT = process.argv[2] || '/Volumes/aebon - 데이터/dreamit-web';
const REPOS = process.argv.slice(3);

/** 요청이 아니라 그냥 글자인 주소 */
const NOT_A_REQUEST =
  /^https?:\/\/(schemas\.(openxmlformats|microsoft)\.org|purl\.org|www\.w3\.org|openoffice\.org|schema\.org|ns\.adobe\.com|sheetjs\.com|localhost|127\.0\.0\.1)/;

const EXTERNAL = /^https?:\/\//i;

/** 주석을 걷어낸다 — 주석 속 URL 은 부르지 않는다 */
function stripComments(src, ext) {
  if (ext === '.html') {
    return src.replace(/<!--[\s\S]*?-->/g, m => m.replace(/[^\n]/g, ' '));
  }
  return src
    .replace(/\/\*[\s\S]*?\*\//g, m => m.replace(/[^\n]/g, ' '))
    .replace(/(^|[^:'"\\])\/\/[^\n]*/g, (m, p) => p + ' '.repeat(m.length - p.length));
}

function lineOf(src, idx) {
  return src.slice(0, idx).split('\n').length;
}

const RULES = [
  // ── 막힘 ────────────────────────────────────────────────────────────
  { level: 'blocking', why: '스타일시트 — 화면 그리기를 막는다',
    re: /<link\b[^>]*\brel\s*=\s*["']?stylesheet["']?[^>]*\bhref\s*=\s*["']([^"']+)["']/gi, g: 1 },
  { level: 'blocking', why: '스타일시트 — 화면 그리기를 막는다',
    re: /<link\b[^>]*\bhref\s*=\s*["']([^"']+)["'][^>]*\brel\s*=\s*["']?stylesheet["']?/gi, g: 1 },
  { level: 'blocking', why: '스크립트 — 파싱을 막는다',
    re: /<script\b[^>]*\bsrc\s*=\s*["']([^"']+)["']/gi, g: 1 },
  { level: 'blocking', why: '@import — 스타일시트와 같다',
    re: /@import\s+(?:url\()?\s*["']?([^"')\s;]+)/gi, g: 1 },
  { level: 'blocking', why: 'ES 모듈 — 모듈이 통째로 안 뜬다',
    re: /\bimport\s+(?:[\w${}\s,*]+\s+from\s+)?["']([^"']+)["']/g, g: 1 },
  { level: 'blocking', why: '동적 import',
    re: /\bimport\(\s*["']([^"']+)["']/g, g: 1 },

  // ── 깨짐 ────────────────────────────────────────────────────────────
  { level: 'broken', why: '이미지 — 그 자리만 빈다',
    re: /<(?:img|source|video|audio)\b[^>]*\bsrc\s*=\s*["']([^"']+)["']/gi, g: 1 },
  { level: 'broken', why: 'CSS url() — 배경·글꼴이 안 나온다',
    re: /url\(\s*["']?([^"')]+)["']?\s*\)/gi, g: 1 },
  { level: 'broken', why: 'preconnect/preload — 쓸데없이 기다린다',
    re: /<link\b[^>]*\brel\s*=\s*["']?(?:preconnect|preload|dns-prefetch)["']?[^>]*\bhref\s*=\s*["']([^"']+)["']/gi, g: 1 },

  // ── JS 가 만들어 붙이는 것 ──────────────────────────────────────────
  // hd-05 를 이 규칙이 없어서 놓쳤다. React·Babel 주소를 변수에 담아 두고
  // 나중에 script 태그를 만들어 붙이는 코드였다. 태그도 import 도 아니라
  // 위 규칙 어디에도 안 걸렸고, 폐쇄망에서 화면이 **통째로 백지**였다.
  // 그래서 잘 알려진 CDN 이름은 어디에 적혀 있든 잡는다.
  { level: 'blocking', why: 'JS 안의 CDN 주소 — 실행 중에 태그로 붙는다',
    re: /["'`](https?:\/\/(?:unpkg\.com|cdn\.jsdelivr\.net|cdnjs\.cloudflare\.com|esm\.sh|cdn\.skypack\.dev|fonts\.googleapis\.com|ajax\.googleapis\.com)\/[^"'`]*)["'`]/g,
    g: 1, jsOnly: true },

  // ── 선택 ────────────────────────────────────────────────────────────
  { level: 'optional', why: '사람이 눌렀을 때만 부른다',
    re: /\bfetch\(\s*["'`]([^"'`]+)["'`]/g, g: 1 },
];

function walk(dir, out = []) {
  for (const name of readdirSync(dir)) {
    if (name === 'node_modules' || name.startsWith('.') || name === 'og') continue;
    const p = join(dir, name);
    const st = statSync(p);
    if (st.isDirectory()) walk(p, out);
    else if (['.html', '.css', '.js', '.mjs'].includes(extname(name))) out.push(p);
  }
  return out;
}

const findings = [];
const repos = REPOS.length ? REPOS
  : readdirSync(ROOT).filter(d => /^hd-(0[1-8]|project\d+)$/.test(d));

let scanned = 0;
for (const repo of repos) {
  let files;
  try { files = walk(join(ROOT, repo)); } catch { continue; }
  for (const f of files) {
    scanned++;
    const raw = readFileSync(f, 'utf8');
    const src = stripComments(raw, extname(f));
    for (const rule of RULES) {
      // 동봉한 라이브러리 자신은 CDN 이름 규칙에서 뺀다 — 파일 안에 원본 주소가
      // 주석·소스맵으로 남아 있어 통째로 가짜 결과가 된다.
      // 단, 그 파일이 **실제로 부르는지**는 런타임 탐침(probe.mjs)이 따로 잡는다.
      if (rule.jsOnly && (!/\.m?js$/.test(f) || /[\\/]lib[\\/]/.test(f))) continue;
      rule.re.lastIndex = 0;
      let m;
      while ((m = rule.re.exec(src))) {
        const url = m[rule.g];
        if (!EXTERNAL.test(url)) continue;
        if (NOT_A_REQUEST.test(url)) continue;
        findings.push({
          repo, file: relative(ROOT, f), line: lineOf(src, m.index),
          level: rule.level, why: rule.why, url: url.slice(0, 88),
        });
      }
    }
  }
}

// 같은 줄에 여러 규칙이 걸릴 수 있다 — 가장 무거운 것만 남긴다
const rank = { blocking: 0, broken: 1, optional: 2 };
const best = new Map();
for (const f of findings) {
  const k = `${f.file}:${f.line}:${f.url}`;
  if (!best.has(k) || rank[f.level] < rank[best.get(k).level]) best.set(k, f);
}
const list = [...best.values()].sort((a, b) => rank[a.level] - rank[b.level] || a.file.localeCompare(b.file));

const label = { blocking: '🔴 막힘', broken: '🟠 깨짐', optional: '🟡 선택' };
let last = '';
for (const f of list) {
  if (f.level !== last) { console.log(`\n${label[f.level]}`); last = f.level; }
  console.log(`   ${f.file}:${f.line}  ${f.why}`);
  console.log(`      ${f.url}`);
}

const n = l => list.filter(x => x.level === l).length;
console.log(`\n${'═'.repeat(62)}`);
console.log(`  파일 ${scanned}개 검사 · 리포 ${repos.length}개`);
console.log(`  🔴 막힘 ${n('blocking')}  🟠 깨짐 ${n('broken')}  🟡 선택 ${n('optional')}`);
console.log('═'.repeat(62));

process.exit(n('blocking') + n('broken') > 0 ? 1 : 0);
