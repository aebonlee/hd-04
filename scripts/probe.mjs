#!/usr/bin/env node
/**
 * probe.mjs — 폐쇄망을 실제로 만들어 놓고 화면을 열어 본다
 *
 * 정적 검사(check-offline.mjs)는 소스에 적힌 주소만 본다.
 * JS 가 만들어 붙이는 주소나 라이브러리가 스스로 부르는 것은 못 잡는다.
 * 그래서 여기서는 진짜로 **바깥을 끊고** 연다.
 *
 *   --host-resolver-rules="MAP * 0.0.0.0:1, EXCLUDE localhost"
 *     localhost 말고는 전부 죽은 주소로 보낸다.
 *     실제 폐쇄망보다 오히려 가혹하다 — 진짜 폐쇄망은 응답 없이 기다리지만
 *     여기서는 즉시 거절된다. 즉 **여기서 뜨면 폐쇄망에서도 뜬다.**
 *
 * 두 가지를 함께 본다. 하나만으로는 판정이 안 된다.
 *   ① 바깥으로 나간 요청이 있는가   → 0 이어야 한다
 *   ② 화면이 실제로 그려졌는가      → 요청이 0 이어도 하얀 화면이면 실패다
 */
import { spawn } from 'node:child_process';
import { mkdtempSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';

const CHROME = '/Users/Shared/Previously Relocated Items 6/Security/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';
const BASE = process.env.BASE || 'http://localhost:8899';
const PAGES = process.argv.slice(2);

const profile = mkdtempSync(join(tmpdir(), 'hd-offline-'));
const chrome = spawn(CHROME, [
  '--headless=new',
  '--remote-debugging-port=9333',
  `--user-data-dir=${profile}`,
  '--no-first-run', '--no-default-browser-check', '--disable-gpu',
  '--window-size=1280,900',
  // ── 폐쇄망을 만든다 ──
  '--host-resolver-rules=MAP * 0.0.0.0:1, EXCLUDE localhost',
  '--proxy-server=direct://', '--proxy-bypass-list=*',
  'about:blank',
], { stdio: 'ignore' });

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function cdpTargets() {
  for (let i = 0; i < 60; i++) {
    try {
      const r = await fetch('http://localhost:9333/json/version');
      if (r.ok) return true;
    } catch { /* 아직 안 떴다 */ }
    await sleep(250);
  }
  throw new Error('크롬이 뜨지 않았습니다');
}

/** CDP 세션 하나 */
function connect(wsUrl) {
  const ws = new WebSocket(wsUrl);
  let id = 0;
  const waiting = new Map();
  const listeners = [];
  const ready = new Promise((res, rej) => { ws.onopen = res; ws.onerror = rej; });
  ws.onmessage = ev => {
    const m = JSON.parse(ev.data);
    if (m.id && waiting.has(m.id)) { waiting.get(m.id)(m.result); waiting.delete(m.id); }
    else if (m.method) listeners.forEach(f => f(m));
  };
  return {
    ready,
    send(method, params) {
      const myId = ++id;
      return new Promise(res => { waiting.set(myId, res); ws.send(JSON.stringify({ id: myId, method, params })); });
    },
    on(fn) { listeners.push(fn); },
    close() { try { ws.close(); } catch {} },
  };
}

const results = [];

try {
  await cdpTargets();

  for (const page of PAGES) {
    const t = await (await fetch('http://localhost:9333/json/new?about:blank', { method: 'PUT' })).json();
    const s = connect(t.webSocketDebuggerUrl);
    await s.ready;

    const requests = [];
    const failures = [];
    const consoleErrs = [];
    s.on(m => {
      if (m.method === 'Network.requestWillBeSent') requests.push(m.params.request.url);
      if (m.method === 'Network.loadingFailed') failures.push(m.params);
      if (m.method === 'Runtime.exceptionThrown') {
        const d = m.params.exceptionDetails;
        consoleErrs.push((d.exception && d.exception.description || d.text || '').split('\n')[0].slice(0, 110));
      }
    });
    await s.send('Network.enable');
    await s.send('Runtime.enable');
    await s.send('Page.enable');

    await s.send('Page.navigate', { url: BASE + page });
    await sleep(3200);

    const evalRes = await s.send('Runtime.evaluate', {
      expression: `(() => {
        const b = document.body;
        return JSON.stringify({
          title: (document.title||'').slice(0,44),
          h: b ? Math.round(b.getBoundingClientRect().height) : 0,
          text: b ? (b.innerText||'').replace(/\\s+/g,' ').trim().length : 0,
        });
      })()`, returnByValue: true,
    });
    let info = {};
    try { info = JSON.parse(evalRes.result.value); } catch {}

    const external = [...new Set(requests
      .filter(u => /^https?:\/\//.test(u))
      .map(u => { try { return new URL(u).origin; } catch { return null; } })
      .filter(o => o && o !== BASE))];

    results.push({ page, external, info, failures: failures.length, consoleErrs });
    s.close();
    await fetch(`http://localhost:9333/json/close/${t.id}`);
  }
} finally {
  chrome.kill();
  try { rmSync(profile, { recursive: true, force: true }); } catch {}
}

let bad = 0;
console.log('═'.repeat(74));
console.log('  바깥을 끊은 크롬으로 실제 열어 봄  (localhost 외 전부 차단)');
console.log('═'.repeat(74));
for (const r of results) {
  const ext = r.external.length > 0;
  // 화면이 그려졌다고 볼 최소선.
  // ⚠ 처음엔 400px·200자로 잡았다가 hd-project07 을 가짜로 잡았다.
  //   접수 건이 없을 때의 빈 화면이라 글자가 141자였다 — 앱은 멀쩡했다.
  //   "글자가 적다"는 고장이 아니다. 하얀 화면(0px·0자)이 고장이다.
  const painted = r.info.h >= 250 && r.info.text >= 60;
  const ok = !ext && painted;
  if (!ok) bad++;
  console.log(`${ok ? '  ✅' : '  ❌'} ${r.page.padEnd(42)} ${String(r.info.h || 0).padStart(5)}px ${String(r.info.text || 0).padStart(6)}자`);
  if (ext) console.log(`        바깥 요청: ${r.external.join('  ')}`);
  if (!painted) console.log(`        화면이 그려지지 않았습니다 (제목: ${r.info.title || '없음'})`);
  if (r.consoleErrs.length) r.consoleErrs.slice(0, 3).forEach(e => console.log(`        ⚠ ${e}`));
}
console.log('═'.repeat(74));
console.log(`  ${results.length}개 중 ${results.length - bad}개 정상 · ${bad}개 문제`);
process.exit(bad ? 1 : 0);
