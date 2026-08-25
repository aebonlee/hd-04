# -*- coding: utf-8 -*-
"""안내 페이지 생성기 — python3 guide/gen.py 로 다시 굽는다."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from _tpl import page

# 메뉴는 build.py 가 _parts/nav_*.html 로 굽는다. 여기서 또 정의하면 두 곳이 갈린다.
_PARTS = os.path.join(os.path.dirname(HERE), '_parts')
NAV = {k: open(os.path.join(_PARTS, 'nav_%s.html' % k), encoding='utf-8').read()
       for k in ('openai', 'claude', 'solar', 'supabase')}

COMMON_SECURITY = """
<div class="warn">
  <b>가장 먼저 알아야 할 것 — 브라우저에 넣은 키는 숨겨지지 않습니다.</b><br>
  이 과정의 도구들은 서버 없이 브라우저에서 도는 정적 페이지입니다.
  키를 화면에 입력하면 그 키는 <b>내 브라우저 안에만</b> 있고 남에게 전송되지는 않지만,
  같은 PC를 쓰는 사람이 개발자도구로 꺼내 볼 수 있습니다.
  <b>공용 PC에서는 쓰고 나서 반드시 키를 지우세요.</b>
</div>

<div class="warn">
  <b>키를 GitHub에 올리지 마세요.</b><br>
  코드 파일이나 <code>config.js</code>에 키를 적어 커밋하면 공개 저장소에서 누구나 봅니다.
  올라간 키는 <b>지워도 커밋 기록에 남습니다.</b> 실수로 올렸다면 그 키를 즉시 폐기하고 새로 발급하세요.
  각 회사 콘솔에서 키를 지우면 그 순간부터 못 씁니다.
</div>
"""

BILLING = """
<h2>돈이 새지 않게 하는 법</h2>
<p>API는 쓴 만큼 돈이 나갑니다. 처음 쓰는 사람이 가장 많이 겪는 사고는
  <b>테스트하다 반복 호출을 걸어 두고 잊는 것</b>입니다.</p>
<ul>
  <li><b>사용 한도(limit)를 먼저 걸어 두세요.</b> 콘솔의 결제·한도 화면에서 월 상한을 정할 수 있습니다.
    한도를 걸면 넘어갈 때 호출이 막혀 요금이 더 안 늘어납니다.</li>
  <li><b>키를 용도별로 나누세요.</b> 실습용 키 하나, 실제 업무용 키 하나.
    실습용이 새면 그것만 폐기하면 됩니다.</li>
  <li><b>가격은 자주 바뀝니다.</b> 여기 숫자를 적지 않은 이유입니다.
    각 사의 공식 가격 페이지에서 확인하세요.</li>
</ul>
"""

PAGES = {}

# ─────────────────────────────────────────────────────────── OpenAI
PAGES['openai'] = dict(
  title="OpenAI API Key 발급·사용법",
  desc="ChatGPT를 만든 OpenAI의 API 키를 발급받아 이 과정의 도구에 넣는 방법입니다.",
  body=COMMON_SECURITY + """
<h2>1. 어디서 발급받나</h2>
<ol class="steps">
  <li><a href="https://platform.openai.com" target="_new" rel="noopener noreferrer">platform.openai.com</a> 에 로그인합니다.
    <b>chat.openai.com(챗지피티 화면)과 다른 곳</b>입니다. 유료 ChatGPT Plus를 쓰고 있어도 API는 따로 결제해야 합니다.</li>
  <li>오른쪽 위 계정 메뉴 → <b>API keys</b> (또는 Dashboard → API keys)로 들어갑니다.</li>
  <li><b>Create new secret key</b> 를 누르고 이름을 적습니다(예: <code>hd-실습</code>).</li>
  <li>화면에 뜬 키(<code>sk-</code> 로 시작)를 복사합니다.
    <b>이 화면을 닫으면 다시 볼 수 없습니다.</b> 잃어버리면 새로 만들어야 합니다.</li>
  <li>Billing(결제)에 카드가 등록돼 있어야 실제로 호출됩니다. 등록 전에는 호출이 거부됩니다.</li>
</ol>

<h2>2. 이 과정의 어디에 쓰나</h2>
<table>
  <thead><tr><th>프로젝트</th><th>쓰는 곳</th></tr></thead>
  <tbody>
    <tr><td>hd-project07 Field-Insight</td><td>현장 음성을 글로 옮기는 정밀 STT (선택 기능)</td></tr>
    <tr><td>hd-project10 부품 사진 파일명</td><td>사진 속 품번·브랜드 판독 (무료 OCR 대신 쓸 때)</td></tr>
  </tbody>
</table>
<p>둘 다 <b>키 없이도 동작합니다.</b> 10번은 브라우저 안에서 도는 무료 OCR이 기본이고,
  07번은 브라우저 기본 음성인식이 기본입니다. 키는 정확도를 올리고 싶을 때만 넣으세요.</p>

<h2>3. 화면에 넣기</h2>
<p>각 도구의 설정 칸에 붙여 넣으면 됩니다. 키는 그 브라우저에만 저장되고 서버로 가지 않습니다.</p>

<h2>4. 직접 호출해 보기</h2>
<p>터미널에서 키가 살아 있는지 확인하는 가장 짧은 방법입니다.</p>
<pre><code>curl https://api.openai.com/v1/chat/completions \\
  -H "Authorization: Bearer $OPENAI_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "안녕하세요"}]
  }'</code></pre>
<div class="tip">
  키를 명령어에 직접 쓰지 말고 <code>export OPENAI_API_KEY="sk-..."</code> 처럼 환경변수에 두세요.
  명령어에 적으면 터미널 기록(<code>history</code>)에 키가 그대로 남습니다.
</div>

<h2>5. 안 될 때</h2>
<table>
  <thead><tr><th>증상</th><th>원인</th></tr></thead>
  <tbody>
    <tr><td>401 Unauthorized</td><td>키가 틀렸거나 폐기됨. 앞뒤 공백이 붙어 들어간 경우도 흔합니다</td></tr>
    <tr><td>429 Too Many Requests</td><td>한도 초과 또는 너무 빠른 연속 호출. 잠시 뒤 재시도</td></tr>
    <tr><td>insufficient_quota</td><td>결제 수단이 없거나 잔액 소진 — Billing 확인</td></tr>
  </tbody>
</table>
""" + BILLING)

# ─────────────────────────────────────────────────────────── Claude
PAGES['claude'] = dict(
  title="Claude API Key 발급·사용법",
  desc="이 과정에서 주로 쓴 Claude의 API 키를 발급받아 도구에 넣는 방법입니다.",
  body=COMMON_SECURITY + """
<h2>1. 어디서 발급받나</h2>
<ol class="steps">
  <li><a href="https://console.anthropic.com" target="_new" rel="noopener noreferrer">console.anthropic.com</a> 에 로그인합니다.
    <b>claude.ai(대화 화면)와 다른 곳</b>입니다. Claude Pro를 쓰고 있어도 API는 따로 결제합니다.</li>
  <li>왼쪽 메뉴 → <b>API Keys</b> → <b>Create Key</b>.</li>
  <li>이름을 적고(예: <code>hd-실습</code>) 만든 뒤 키를 복사합니다.
    <code>sk-ant-</code> 로 시작합니다. <b>이 화면을 닫으면 다시 볼 수 없습니다.</b></li>
  <li>Plans &amp; Billing 에서 크레딧을 충전해야 실제로 호출됩니다.</li>
</ol>

<h2>2. 이 과정의 어디에 쓰나</h2>
<table>
  <thead><tr><th>프로젝트</th><th>쓰는 곳</th></tr></thead>
  <tbody>
    <tr><td>hd-project07 Field-Insight</td><td>현장 이슈를 정형화하는 판단 (선택 기능)</td></tr>
    <tr><td>hd-project10 부품 사진 파일명</td><td>사진 속 품번·브랜드 판독 (무료 OCR 대신 쓸 때)</td></tr>
  </tbody>
</table>

<h2>3. 모델 고르기</h2>
<p>이름이 비슷해 헷갈리기 쉽습니다. 실습에서는 아래 정도만 알면 됩니다.</p>
<table>
  <thead><tr><th>모델 ID</th><th>언제 쓰나</th></tr></thead>
  <tbody>
    <tr><td><code>claude-opus-5</code></td><td>가장 똑똑한 쪽. 판단이 중요한 일</td></tr>
    <tr><td><code>claude-sonnet-5</code></td><td>속도와 비용의 균형</td></tr>
    <tr><td><code>claude-haiku-4-5</code></td><td>단순 분류·추출처럼 가벼운 일</td></tr>
  </tbody>
</table>
<div class="tip">
  모델 ID는 <b>날짜를 붙이지 않습니다.</b> <code>claude-opus-5</code> 가 완성된 이름입니다.
  예전 방식대로 <code>-20250101</code> 같은 것을 붙이면 없는 모델이 되어 404가 납니다.
</div>

<h2>4. 직접 호출해 보기</h2>
<pre><code>curl https://api.anthropic.com/v1/messages \\
  -H "x-api-key: $ANTHROPIC_API_KEY" \\
  -H "anthropic-version: 2023-06-01" \\
  -H "content-type: application/json" \\
  -d '{
    "model": "claude-opus-5",
    "max_tokens": 1024,
    "messages": [{"role": "user", "content": "안녕하세요"}]
  }'</code></pre>
<div class="tip">
  OpenAI와 <b>헤더가 다릅니다.</b> Claude는 <code>Authorization: Bearer</code> 가 아니라
  <code>x-api-key</code> 를 쓰고, <code>anthropic-version</code> 헤더가 <b>반드시</b> 있어야 합니다.
  이 두 가지를 빠뜨리는 것이 가장 흔한 실수입니다.
</div>

<h2>5. 안 될 때</h2>
<table>
  <thead><tr><th>증상</th><th>원인</th></tr></thead>
  <tbody>
    <tr><td>401 authentication_error</td><td>키가 틀렸거나 <code>Authorization</code> 헤더에 넣음 → <code>x-api-key</code> 로</td></tr>
    <tr><td>400 invalid_request_error</td><td><code>anthropic-version</code> 누락, 또는 <code>max_tokens</code> 누락(필수입니다)</td></tr>
    <tr><td>404 not_found_error</td><td>모델 ID가 틀림 — 날짜를 붙이지 않았는지 확인</td></tr>
    <tr><td>429 rate_limit_error</td><td>너무 빠른 연속 호출 또는 한도 초과</td></tr>
    <tr><td>credit balance is too low</td><td>크레딧 소진 — Plans &amp; Billing 에서 충전</td></tr>
  </tbody>
</table>
""" + BILLING)

# ─────────────────────────────────────────────────────────── Solar
PAGES['solar'] = dict(
  title="Solar(Upstage) API Key 발급·사용법",
  desc="국내 업스테이지의 Solar 모델 API 키를 발급받아 도구에 넣는 방법입니다. 한국어 문서 처리에 강합니다.",
  body=COMMON_SECURITY + """
<h2>1. 어디서 발급받나</h2>
<ol class="steps">
  <li><a href="https://console.upstage.ai" target="_new" rel="noopener noreferrer">console.upstage.ai</a> 에 가입·로그인합니다.</li>
  <li><b>API Keys</b> 메뉴에서 새 키를 만듭니다.</li>
  <li>만들어진 키를 복사합니다. <b>이 화면을 닫으면 다시 볼 수 없습니다.</b></li>
  <li>가입 시 체험용 크레딧이 주어지는 경우가 있습니다. 소진 후에는 결제 등록이 필요합니다.</li>
</ol>

<h2>2. 이 과정의 어디에 쓰나</h2>
<table>
  <thead><tr><th>프로젝트</th><th>쓰는 곳</th></tr></thead>
  <tbody>
    <tr><td>hd-project10 부품 사진 파일명</td>
        <td>문서·이미지에서 글자를 읽어 내는 기능(Document Digitization).
            한국어와 도면·라벨 같은 실무 이미지에 강합니다</td></tr>
  </tbody>
</table>

<h2>3. 직접 호출해 보기</h2>
<p>Solar의 대화 API는 <b>OpenAI와 같은 형식</b>을 씁니다. 그래서 OpenAI용 코드에서
  주소와 모델 이름만 바꿔도 대부분 돌아갑니다.</p>
<pre><code>curl https://api.upstage.ai/v1/chat/completions \\
  -H "Authorization: Bearer $UPSTAGE_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{
    "model": "solar-pro2",
    "messages": [{"role": "user", "content": "안녕하세요"}]
  }'</code></pre>
<div class="tip">
  <b>모델 이름은 콘솔에서 확인하세요.</b> 업스테이지는 모델을 비교적 자주 갱신합니다.
  여기 적은 이름이 맞지 않으면 콘솔의 Models 문서에 있는 현재 이름으로 바꾸면 됩니다.
</div>

<h2>4. 문서·이미지에서 글자 읽기</h2>
<p>10번 프로젝트가 쓰는 것은 대화 API가 아니라 <b>문서 판독</b> 쪽입니다.</p>
<pre><code>curl https://api.upstage.ai/v1/document-digitization \\
  -H "Authorization: Bearer $UPSTAGE_API_KEY" \\
  -F "document=@부품사진.jpg" \\
  -F "model=ocr"</code></pre>

<h2>5. 안 될 때</h2>
<table>
  <thead><tr><th>증상</th><th>원인</th></tr></thead>
  <tbody>
    <tr><td>401</td><td>키가 틀렸거나 <code>Bearer </code> 접두어 누락</td></tr>
    <tr><td>404 / model not found</td><td>모델 이름이 바뀜 — 콘솔에서 현재 이름 확인</td></tr>
    <tr><td>429</td><td>호출이 너무 잦음 또는 한도 초과</td></tr>
  </tbody>
</table>
""" + BILLING)

# ─────────────────────────────────────────────────────────── Supabase
PAGES['supabase'] = dict(
  title="Supabase 사용법",
  desc="여러 사람이 같은 자료를 보게 하려면 서버가 필요합니다. 무료로 시작할 수 있는 Supabase를 각자 계정에 붙이는 방법입니다.",
  body="""
<h2>왜 필요한가</h2>
<p>이 과정의 도구들은 기본적으로 <b>내 브라우저에만</b> 자료를 담습니다.
  혼자 쓰는 도구(구매 분석·컨테이너 산출·사진 파일명)는 그것으로 충분합니다.</p>
<p>그런데 <b>여럿이 주고받아야 하는 도구</b>는 그러면 목적이 성립하지 않습니다.
  협력업체가 각자 응답하고, 팀이 서로 보고, 접수자와 전문가가 주고받아야 하는데
  자료가 각자 브라우저에만 있으면 <b>서로 안 보이기 때문</b>입니다.</p>
<table>
  <thead><tr><th>서버가 필요한 프로젝트</th><th>왜</th></tr></thead>
  <tbody>
    <tr><td>hd-project02 결품 응답</td><td>여러 업체가 같은 표를 보고 각자 응답</td></tr>
    <tr><td>hd-project03 재고 실사</td><td>업체가 입력하고 담당자가 검토</td></tr>
    <tr><td>hd-project05 해외영업 포털</td><td>팀원이 주간업무·환율·출장을 함께 봄</td></tr>
    <tr><td>hd-project07 Field-Insight</td><td>접수자와 전문가가 다른 사람</td></tr>
    <tr><td>hd-project08 업무공유 대시보드</td><td>"공유"가 목적</td></tr>
    <tr><td>hd-project11 KPI 자동화</td><td>사업장별 담당자가 각자 입력</td></tr>
  </tbody>
</table>

<h2>1. 내 프로젝트 만들기</h2>
<ol class="steps">
  <li><a href="https://supabase.com" target="_new" rel="noopener noreferrer">supabase.com</a> 에 GitHub 계정으로 가입합니다.</li>
  <li><b>New project</b> — 이름과 지역(<b>Northeast Asia (Seoul)</b> 권장)을 고릅니다.</li>
  <li><b>데이터베이스 비밀번호</b>를 정합니다. 이건 따로 적어 두세요. 잊으면 재설정해야 합니다.</li>
  <li>1~2분 기다리면 준비됩니다.</li>
</ol>

<h2>2. 표 만들기 — SQL 붙여 넣기</h2>
<ol class="steps">
  <li>쓰려는 프로젝트 저장소에서 <code>supabase/schema.sql</code> 파일을 엽니다.</li>
  <li><b>전체를 복사</b>합니다.</li>
  <li>Supabase 화면 왼쪽 → <b>SQL Editor</b> → 붙여 넣고 <b>Run</b>.</li>
  <li>표·정책·함수가 한 번에 만들어집니다. <b>여러 번 실행해도 안전</b>하게 짜여 있습니다.</li>
</ol>
<div class="tip">
  각 저장소의 <code>supabase/README.md</code> 에 그 프로젝트만의 준비 절차(계정 만들기 등)가 더 적혀 있습니다.
  SQL만 올리고 계정 연결을 빠뜨리면 <b>로그인은 되는데 자료가 하나도 안 보이는</b> 상태가 됩니다.
</div>

<h2>3. 앱에 연결하기</h2>
<ol class="steps">
  <li>Supabase → <b>Settings → API</b> 에서 두 값을 복사합니다.
    <ul>
      <li><b>Project URL</b></li>
      <li><b>Project API keys → anon / public</b></li>
    </ul>
  </li>
  <li>저장소의 <code>js/config.js</code> 를 열어 두 값을 붙여 넣고
    <code>USE_SUPABASE</code> 를 <code>true</code> 로 바꿉니다.</li>
  <li>커밋·푸시하면 배포된 페이지가 서버를 씁니다.</li>
</ol>
<div class="tip">
  커밋하지 않고 잠깐 확인만 하려면 주소 뒤에 <code>?supabase=1</code> 을 붙이면 됩니다.
</div>

<div class="warn">
  <b>service_role 키는 절대 넣지 마세요.</b><br>
  같은 화면에 <code>anon</code> 키와 <code>service_role</code> 키가 나란히 있습니다.
  <code>anon</code> 은 브라우저에 노출돼도 되는 키이고, 실제 차단은 아래 RLS가 합니다.
  하지만 <code>service_role</code> 은 <b>모든 보안 규칙을 통째로 우회</b>합니다.
  그 키가 공개 저장소에 올라가면 누구나 전체 데이터를 읽고 지울 수 있습니다.
</div>

<h2>4. 누가 무엇을 볼 수 있는가 — RLS</h2>
<p>Supabase는 <b>Row Level Security(RLS)</b> 로 행 단위 접근을 막습니다.
  이 과정의 스키마에는 이미 정책이 들어 있습니다.</p>
<ul>
  <li><b>업체는 자기 것만</b> 봅니다 — 화면 필터가 아니라 DB가 막습니다.
    화면에서만 막으면 주소만 바꿔도 남의 자료가 보입니다.</li>
  <li><b>기록성 표(로그·응답)는 고치거나 지울 수 없습니다.</b>
    UPDATE·DELETE 정책을 아예 만들지 않았습니다. 사후 조작을 막기 위해서입니다.</li>
  <li>RLS가 "지금 접속한 사람이 누구인지" 알려면 <b>Auth 사용자와 업체를 이어 줘야</b> 합니다.
    이어 주지 않으면 로그인은 되는데 아무것도 안 보입니다.</li>
</ul>

<h2>5. 확인하는 법</h2>
<ol class="steps">
  <li>페이지를 열면 맨 위에 띠가 뜹니다.
    <b>"서버에 연결됨"</b> 이면 성공, <b>"이 브라우저에만 저장됩니다"</b> 면 아직 데모입니다.
    실패한 경우 띠에 이유가 함께 나옵니다.</li>
  <li><b>다른 브라우저(또는 시크릿 창)</b> 로 열어 같은 자료가 보이는지 확인합니다.
    이게 진짜 확인 방법입니다 — 같은 브라우저에서는 데모 모드여도 자료가 보입니다.</li>
</ol>

<h2>6. SQL이 맞는지 미리 확인하기</h2>
<p>운영에서 처음 돌리지 않도록, 저장소마다 검증 스크립트를 넣어 두었습니다.</p>
<pre><code>./scripts/sqltest/run.sh</code></pre>
<p>임시 PostgreSQL을 잠깐 띄워 <code>schema.sql</code> 을 <b>실제로 적용해 보고</b>
  제약·정책·권한이 의도대로인지 확인한 뒤 지웁니다. 기존 설치에 영향이 없습니다.
  (PostgreSQL이 없으면 <code>brew install postgresql@17</code>)</p>

<h2>7. 안 될 때</h2>
<table>
  <thead><tr><th>증상</th><th>원인</th></tr></thead>
  <tbody>
    <tr><td>relation "..." does not exist</td><td><code>schema.sql</code> 을 아직 실행하지 않음</td></tr>
    <tr><td>로그인은 되는데 목록이 비어 있음</td><td>Auth 사용자와 업체/팀원 행을 안 이어 줌 (RLS가 전부 걸러 냄)</td></tr>
    <tr><td>new row violates row-level security policy</td><td>쓰기 권한이 없는 계정 — 관리자 표에 등록됐는지 확인</td></tr>
    <tr><td>Invalid API key</td><td>키를 잘못 복사했거나 앞뒤 공백이 붙음</td></tr>
    <tr><td>"다른 사람이 먼저 저장했습니다"</td><td>정상 동작입니다 — 동시 편집을 막은 것.
        새로고침해 최신 자료를 받은 뒤 다시 입력하세요</td></tr>
  </tbody>
</table>

<h2>8. 무료 한도</h2>
<p>무료 플랜으로 이 과정의 도구들을 쓰기에는 충분합니다.
  다만 <b>일정 기간 아무도 접속하지 않으면 프로젝트가 일시 정지</b>될 수 있습니다.
  정지되면 대시보드에서 다시 켜면 됩니다. 정확한 한도는 공식 가격 페이지에서 확인하세요.</p>
""")

for slug, d in PAGES.items():
    html = page(slug, d['title'], d['desc'], NAV[slug], d['body'])
    with open(os.path.join(HERE, slug + '.html'), 'w', encoding='utf-8') as f:
        f.write(html)
    print('생성:', slug + '.html', len(html), '자')
