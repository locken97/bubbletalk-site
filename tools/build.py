#!/usr/bin/env python3
"""버블톡 사이트 만들기: 공통 머리·꼬리 + 앱 약관(lib/data/terms.dart)에서 이용약관을 가져와 HTML로.
사용: python3 build.py <앱 저장소 경로> <사이트 저장소 경로>
"""
import html
import re
import sys
from pathlib import Path

APP = Path(sys.argv[1])
OUT = Path(sys.argv[2])

terms_src = (APP / 'lib/data/terms.dart').read_text(encoding='utf-8')

OPERATOR = '메종 드 무아'
EMAIL = 'bubbletalk.service@gmail.com'
DRAFT = '법률 검토 전 초안이에요. 정식 출시 전에 내용이 바뀔 수 있어요.'


def dart_doc(name):
    """const <name> = TermsDoc(...) 에서 summary와 (제목, 본문) 목록"""
    start = terms_src.index(f'const {name} = TermsDoc(')
    end = terms_src.index('\n);', start)
    block = terms_src[start:end]
    def strings(s):
        return ''.join(re.findall(r"'((?:[^'\\]|\\.)*)'", s))
    summary = strings(re.search(r'summary:(.*?),\n  sections', block, re.S).group(1))
    sections = []
    for m in re.finditer(r"TermsSection\((.*?)\),\n", block, re.S):
        lits = re.findall(r"'((?:[^'\\]|\\.)*)'", m.group(1))
        sections.append((lits[0], ''.join(lits[1:]).replace('\\n', '\n')))
    return summary, sections


def body_html(text):
    """'1. ...\\n2. ...' → <ol>, '• ...' → <ul>, 그 밖은 <p>"""
    lines = [l for l in text.split('\n') if l.strip()]
    out = []
    kind = None
    for l in lines:
        m = re.match(r'^(\d+)\.\s*(.*)$', l)
        b = re.match(r'^•\s*(.*)$', l)
        k, content = ('ol', m.group(2)) if m else ('ul', b.group(1)) if b else ('p', l)
        if k != kind:
            if kind in ('ol', 'ul'):
                out.append(f'</{kind}>')
            if k in ('ol', 'ul'):
                out.append(f'<{k}>')
            kind = k
        c = html.escape(content)
        out.append(f'<li>{c}</li>' if k in ('ol', 'ul') else f'<p>{c}</p>')
    if kind in ('ol', 'ul'):
        out.append(f'</{kind}>')
    return '\n'.join(out)


NAV = [('index.html', '소개'), ('notice.html', '공지사항'), ('inquiry.html', '문의하기')]


def page(filename, title, desc, main, extra_head=''):
    nav = '\n'.join(
        f'<a href="{href}"{" aria-current=\"page\"" if href == filename else ""}>{label}</a>'
        for href, label in NAV)
    full_title = '버블톡' if filename == 'index.html' else f'{title} · 버블톡'
    return f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{full_title}</title>
<meta name="description" content="{html.escape(desc)}">
<meta property="og:title" content="{full_title}">
<meta property="og:description" content="{html.escape(desc)}">
<meta property="og:image" content="https://bubbletalk.kr/assets/icon-256.png">
<meta property="og:url" content="https://bubbletalk.kr/{'' if filename == 'index.html' else filename}">
<meta name="theme-color" content="#8ECDF2">
<link rel="icon" type="image/png" href="assets/favicon.png">
<link rel="apple-touch-icon" href="assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Jua&family=Gowun+Dodum&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard-dynamic-subset.min.css">
<link rel="stylesheet" href="assets/style.css">
{extra_head}</head>
<body>
<a class="skip" href="#main">본문으로 건너뛰기</a>
<header class="top">
  <div class="wrap">
    <a class="brand" href="index.html"><img src="assets/icon-256.png" alt="" width="36" height="36"><span>버블톡</span></a>
    <nav class="nav" aria-label="사이트 메뉴">
{nav}
    </nav>
  </div>
</header>
<main id="main">
{main}
</main>
<footer>
  <div class="wrap">
    <div>
      <p><strong>버블톡</strong> · 운영 {OPERATOR}</p>
      <p>문의 <a href="inquiry.html">문의하기</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p>© 2026 버블톡. All rights reserved.</p>
    </div>
    <div class="links">
      <a href="notice.html">공지사항</a>
      <a href="inquiry.html">문의하기</a>
      <a href="terms.html">이용약관</a>
      <a href="privacy.html"><strong>개인정보 처리방침</strong></a>
      <a href="delete-account.html">계정 삭제 요청</a>
      <a href="child-safety.html">아동 안전 표준</a>
    </div>
  </div>
</footer>
</body>
</html>
'''


# ── 소개 ─────────────────────────────────────────
index_main = '''<section class="hero">
  <div class="bubbles" aria-hidden="false"></div>
  <div class="wrap">
    <div>
      <h1>말하고, 보고,<br><em>퐁!</em> 사라지는 대화</h1>
      <p class="lead">버블톡은 말풍선(버블)이 정해진 시간만 떠 있다가 퐁 하고 사라지는 메신저예요.
        쌓이는 기록 대신 지금 나누는 대화에 집중해요. 사진도 링크도 없어서 아이도 안심하고 써요.</p>
      <div class="badges">
        <span class="soon">곧 만나요 · 안드로이드 먼저</span>
        <a class="ghost" href="#safe">안심하고 쓰는 이유</a>
      </div>
    </div>
    <div class="chat" aria-label="버블톡 대화 예시">
      <div class="room">우리 반 수다방<small>4명 · 버블 수명 1분</small></div>
      <div class="lines">
        <div class="b them">오늘 숙제 뭐였지?</div>
        <div class="b mine">수학 익힘책 24쪽!</div>
        <div class="b them2">나도 지금 하는 중 ㅋㅋ</div>
      </div>
    </div>
  </div>
</section>

<section class="block alt">
  <div class="wrap">
    <h2>버블톡은 이렇게 달라요</h2>
    <p class="sub">기록을 남기는 메신저가 아니라, 대화하는 순간을 위한 메신저예요.</p>
    <div class="grid">
      <div class="card c-sky"><div class="dot">🫧</div><h3>사라지는 버블</h3>
        <p>버블은 방마다 정한 시간(30초~24시간)만 떠 있다가 퐁 하고 사라져요. 간직하고 싶은 버블만 길게 눌러 내 휴대폰에 보관해요.</p></div>
      <div class="card c-me"><div class="dot">🔒</div><h3>대화는 서버에 안 남아요</h3>
        <p>1:1 대화는 종단간 암호화로 받는 사람 휴대폰에서만 열려요. 운영자도 대화 내용을 볼 수 없고, 서버에 저장하지 않아요.</p></div>
      <div class="card c-mint"><div class="dot">🧒</div><h3>아이도 안심</h3>
        <p>사진·파일은 보낼 수 없고 링크는 눌러도 열리지 않아요. 만 14세 미만은 보호자 동의를 받아야 쓸 수 있어요.</p></div>
      <div class="card c-coral"><div class="dot">📌</div><h3>공지는 남고, 잡담은 사라지는 단체방</h3>
        <p>방장이 거는 띠와 핀버블로 꼭 필요한 공지는 남기고, 나머지 대화는 가볍게 흘려보내요.</p></div>
      <div class="card c-amber"><div class="dot">❓</div><h3>퀴즈방</h3>
        <p>방장이 문제를 내고 모두 함께 풀어요. 상식·넌센스·계산·구구단 기본 문제와 내가 만든 문제로, 스피드 퀴즈도 할 수 있어요.</p></div>
      <div class="card c-pink"><div class="dot">🎉</div><h3>작은 재미</h3>
        <p>같은 이모티콘을 동시에 보내면 찌찌뽕! 생일과 친구 기념일에는 대화방에서 함께 축하해요.</p></div>
    </div>
  </div>
</section>

<section class="block" id="safe">
  <div class="wrap">
    <h2>안심하고 쓰는 이유</h2>
    <p class="sub">아이에게 처음 쥐여 주는 메신저가 될 수 있도록 만들었어요.</p>
    <ul class="promise">
      <li>대화 내용을 서버에 저장하거나 광고·분석에 쓰지 않아요.</li>
      <li>전화번호와 실명을 받지 않아요. 주소록은 읽지 않고, 초대할 사람만 직접 골라요.</li>
      <li>사진·이미지·파일 보내기가 없어요. 링크는 글자로만 보여요.</li>
      <li>만 14세 미만은 보호자 동의로 계정이 열리고, 새 친구도 보호자가 승인해요.</li>
      <li>버블·프로필을 신고할 수 있고, 신고한 사람은 상대에게 알리지 않아요.</li>
      <li>전화번호·계좌번호처럼 보이는 내용을 쓰면 보내기 전에 알려 줘요.</li>
    </ul>
  </div>
</section>

<section class="block alt cta">
  <div class="wrap">
    <h2>곧 만나요</h2>
    <p class="sub">안드로이드 앱을 먼저 준비하고 있어요. 소식이 궁금하면 메일로 물어봐 주세요.</p>
    <span class="soon">구글 플레이 출시 준비 중</span>
  </div>
</section>
<script src="assets/site.js" defer></script>'''

# ── 이용약관 ────────────────────────────────────────
summary, sections = dart_doc('serviceTerms')
toc = ' · '.join(f'<a href="#s{i}">{html.escape(h)}</a>' for i, (h, _) in enumerate(sections))
terms_main = f'''<article class="doc"><div class="wrap">
<h1>서비스 이용약관</h1>
<p class="meta">운영 {OPERATOR} · 시행일: 정식 출시일</p>
<p class="draft">{DRAFT}</p>
<div class="summary">{html.escape(summary)}</div>
<nav class="toc" aria-label="목차">{toc}</nav>
''' + '\n'.join(f'<h2 id="s{i}">{html.escape(h)}</h2>\n{body_html(b)}' for i, (h, b) in enumerate(sections)) + '''
</div></article>'''

# ── 개인정보 처리방침 ─────────────────────────────────
p_summary, p_sections = dart_doc('privacyTerms')
g_summary, g_sections = dart_doc('guardianTerms')
ps = dict(p_sections)
gs = dict(g_sections)
privacy_main = f'''<article class="doc"><div class="wrap">
<h1>개인정보 처리방침</h1>
<p class="meta">운영 {OPERATOR} · 시행일: 정식 출시일</p>
<p class="draft">{DRAFT}</p>
<div class="summary">{html.escape(p_summary)}</div>
<p>{OPERATOR}(이하 "운영자")는 버블톡(이하 "서비스")을 이용하는 회원의 개인정보를 「개인정보 보호법」에 따라 처리하며, 다음과 같이 처리방침을 알려 드립니다.</p>

<h2>1. 처리하는 개인정보 항목</h2>
{body_html(ps['수집하는 항목'])}
<h3>만 14세 미만 회원의 보호자에게서 받는 정보</h3>
{body_html(gs['보호자에게서 받는 정보'])}

<h3>사이트(bubbletalk.kr) 문의하기를 쓸 때</h3>
<ul><li>문의 종류·제목·내용과 운영자의 답변, 문의한 버블톡 계정(아이디·닉네임)</li></ul>

<h2>2. 처리하지 않는 정보</h2>
{body_html(ps['수집하지 않는 것'])}

<h2>3. 처리 목적</h2>
{body_html(ps['이용 목적'])}

<h2>4. 보유 기간과 파기</h2>
{body_html(ps['보관 기간'])}
<ul>
<li>퀴즈 진행 기록(문제·답)은 그 방에서 다음 퀴즈를 시작하거나 방이 사라질 때, 방장이 보관한 퀴즈 결과(참여자 닉네임·맞힌 개수·순위)는 방장이 지울 때, 퀴즈방 누적 점수판은 방장이 초기화하거나 방이 사라질 때 삭제합니다.</li>
<li>보호자 동의가 5일 안에 오지 않은 만 14세 미만 아이 계정과 받은 정보는 지웁니다.</li>
<li>사이트 문의와 답변은 탈퇴하면 계정과 함께 삭제합니다.</li>
<li>파기할 때는 전자적 파일을 복구할 수 없는 방법으로 지웁니다.</li>
</ul>

<h2>5. 대화 내용의 처리</h2>
<ul>
<li>운영자는 대화 내용을 서버에 저장하거나 백업하지 않으며, 광고·추천·분석에 쓰지 않습니다.</li>
<li>1:1 대화의 버블은 보내는 회원의 휴대폰에서 암호화(종단간 암호화)되어 받는 회원의 휴대폰에서만 열 수 있습니다. 상대 화면에 띄워질 때까지만 암호화된 상태로 서버에 잠시 머물고, 띄워지면 바로 지워집니다. 띄워지지 않은 버블은 24시간 뒤 자동으로 지워집니다.</li>
<li>회원이 신고할 때 직접 첨부한 버블과 신고 사유는 신고 처리를 위해 저장됩니다.</li>
<li>퀴즈의 문제·정답·답은 서버가 채점해야 하므로 종단간 암호화하지 않고 서버에 저장됩니다(위 4번의 기간 동안).</li>
</ul>

<h2>6. 만 14세 미만 아동의 개인정보</h2>
<h3>동의 방법</h3>
{body_html(gs['동의 방법'])}
<h3>아이에게서 받는 정보</h3>
{body_html(gs['아이에게서 받는 정보'])}
<h3>보호자의 권리</h3>
{body_html(gs['보호자의 권리'])}

<h2>7. 처리 위탁과 국외 이전</h2>
<p>서비스 제공을 위해 다음 업체에 개인정보 처리를 맡기고 있습니다. 이전 국가·이전 일시·연락처 등 세부 내용은 법률 검토를 거쳐 정식 출시 전에 보완합니다.</p>
<table class="plain">
<tr><th>Supabase</th><td>회원 정보·친구·대화방 정보를 저장하는 서버와 데이터베이스 (서울 지역 서버)</td></tr>
<tr><th>Google Firebase</th><td>휴대폰 알림 전송. 알림에는 버블 내용 없이 방 번호와 보낸 사람 닉네임만 담깁니다.</td></tr>
<tr><th>Google Gmail</th><td>가입 확인 코드, 비밀번호 찾기, 보호자 동의 메일 보내기와 받기</td></tr>
</table>

<h2>8. 정보주체의 권리와 행사 방법</h2>
<p>회원(만 14세 미만은 보호자)은 언제든 개인정보 열람, 정정, 삭제, 처리 정지를 요청하고 동의를 철회할 수 있습니다.
앱의 설정에서 직접 하거나 <a href="mailto:{EMAIL}">{EMAIL}</a>으로 요청하면 지체 없이 처리합니다.
계정 삭제는 <a href="delete-account.html">계정 삭제 요청</a> 안내를 참고해 주세요.</p>

<h2>9. 안전성 확보 조치</h2>
<ul>
<li>비밀번호는 원래 글자를 알 수 없는 방식으로 암호화하여 저장합니다.</li>
<li>1:1 대화는 종단간 암호화하며, 대화 암호화용 비밀 열쇠는 회원의 휴대폰에만 있습니다.</li>
<li>서버의 개인정보에는 꼭 필요한 기능만 접근할 수 있도록 권한을 나눠 둡니다.</li>
<li>휴대폰에 보관한 버블은 휴대폰의 보안 저장소에 암호화하여 저장합니다.</li>
</ul>

<h2>10. 자동으로 수집하는 장치</h2>
<p>버블톡 앱과 이 사이트는 광고나 행동 분석을 위한 쿠키·추적 도구를 쓰지 않습니다. 사이트에서 공지사항·문의하기에 로그인하면 로그인 상태를 기억하기 위해 그 브라우저의 저장소에 로그인 열쇠를 저장하며, 로그아웃하면 지워집니다.</p>

<h2>11. 개인정보 보호책임자</h2>
<table class="plain">
<tr><th>운영자</th><td>{OPERATOR}</td></tr>
<tr><th>연락처</th><td><a href="mailto:{EMAIL}">{EMAIL}</a></td></tr>
</table>

<h2>12. 권익 침해 구제</h2>
<p>개인정보 침해에 대한 상담이나 신고가 필요하면 다음 기관에 문의할 수 있습니다.</p>
<ul>
<li>개인정보침해신고센터: 국번 없이 118 (privacy.kisa.or.kr)</li>
<li>개인정보분쟁조정위원회: 1833-6972 (www.kopico.go.kr)</li>
<li>대검찰청 사이버수사과: 국번 없이 1301</li>
<li>경찰청 사이버수사국: 국번 없이 182</li>
</ul>

<h2>13. 처리방침의 변경</h2>
<p>이 처리방침이 바뀌면 시행 7일 전부터 앱과 이 사이트에 알립니다. 회원에게 불리한 변경은 30일 전에 알립니다.</p>
</div></article>'''

# ── 계정 삭제 요청 ──────────────────────────────────
mail = f'mailto:{EMAIL}?subject=%5B%EB%B2%84%EB%B8%94%ED%86%A1%5D%20%EA%B3%84%EC%A0%95%20%EC%82%AD%EC%A0%9C%20%EC%9A%94%EC%B2%AD&body=%EB%B2%84%EB%B8%94%ED%86%A1%20%EC%95%84%EC%9D%B4%EB%94%94%3A%20%40%0A%EA%B0%80%EC%9E%85%ED%95%9C%20%EC%9D%B4%EB%A9%94%EC%9D%BC(%EB%98%90%EB%8A%94%20%EB%B3%B4%ED%98%B8%EC%9E%90%20%EC%9D%B4%EB%A9%94%EC%9D%BC)%3A%20%0A'
delete_main = f'''<article class="doc"><div class="wrap">
<h1>계정 삭제 요청</h1>
<p class="meta">버블톡 · 운영 {OPERATOR}</p>
<div class="summary">버블톡 계정과 개인정보를 지우는 방법이에요. 앱에서 바로 할 수 있고, 앱을 지웠다면 이메일로 요청할 수 있어요.</div>

<h2>앱에서 지우기</h2>
<ol class="steps">
<li>버블톡 앱을 열고 <strong>설정</strong>으로 가요.</li>
<li><strong>계정</strong> 아래의 <strong>탈퇴하기</strong>를 눌러요.</li>
<li>비밀번호를 다시 입력하면 탈퇴 신청이 끝나요.</li>
</ol>
<p>만 14세 미만 아이 계정은 아이 또는 보호자가 신청할 수 있어요.</p>

<h2>앱 없이 이메일로 요청하기</h2>
<p>앱을 이미 지웠거나 로그인할 수 없으면 아래 메일로 요청해 주세요. 본인 확인을 위해 <strong>가입한 이메일(아이 계정은 보호자 이메일)에서 보내 주세요.</strong></p>
<p><a class="mailbtn" href="{mail}">계정 삭제 메일 쓰기</a></p>
<p>받는 주소: <a href="mailto:{EMAIL}">{EMAIL}</a><br>적을 내용: 버블톡 아이디, 가입한 이메일(또는 보호자 이메일)</p>
<p>요청을 받으면 본인 확인 뒤 탈퇴 신청과 같은 방식으로 처리하고, 처리 결과를 메일로 알려 드려요.</p>

<h2>지워지는 것과 남는 것</h2>
<table class="plain">
<tr><th>바로 처리</th><td>탈퇴를 신청하면 다른 회원에게는 없는 계정처럼 보여요.</td></tr>
<tr><th>7일 뒤 삭제</th><td>이메일, 닉네임, 생년월일, 비밀번호, 프로필 사진·배경 사진·상태 메시지, 친구 관계, 대화방 참여 정보, 퀴즈 보관함(문제지·내가 만든 문제·결과), 알림 열쇠 등 계정 정보를 지워요. 7일 안에 다시 로그인하면 계정이 복구돼요.</td></tr>
<tr><th>남는 것</th><td>
<ul>
<li>버블톡 아이디: 누구도 같은 아이디를 다시 쓰지 못하도록, 원래 글자를 알아볼 수 없는 형태로 바꿔 보관해요.</li>
<li>신고 자료(신고에 첨부된 버블과 사유): 처리를 마친 뒤 90일 보관 후 삭제해요.</li>
<li>법령에서 보관하도록 정한 정보는 정해진 기간 동안 보관해요.</li>
</ul></td></tr>
<tr><th>원래 없는 것</th><td>대화 내용은 서버에 저장하지 않아서 지울 것도 남는 것도 없어요. 휴대폰 보관함에 담은 버블은 앱을 지우면 함께 지워져요.</td></tr>
</table>
</div></article>'''

notfound_main = '''<section class="block cta"><div class="wrap">
<h2>퐁! 이 페이지는 사라졌어요</h2>
<p class="sub">찾는 페이지가 없거나 주소가 바뀌었어요.</p>
<a class="ghost" href="index.html">첫 화면으로</a>
</div></section>'''

BOARD_HEAD = ('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.49.4/dist/umd/supabase.min.js"></script>\n'
              '<script src="assets/board.js"></script>\n')


def board(title, lead, call):
    return f'''<article class="doc"><div class="wrap">
<div class="account" id="account"></div>
<h1>{title}</h1>
<p class="meta">{lead}</p>
<div id="board"><p class="empty">불러오는 중…</p></div>
</div></article>
<script>document.addEventListener('DOMContentLoaded', function () {{ BubbleBoard.{call}(); }});</script>'''


DESC = '말하고, 보고, 퐁! 사라지는 대화. 아이도 안심하고 쓰는 메신저 버블톡.'
# ── 아동 안전 표준 ──────────────────────────
safety_main = f'''<article class="doc"><div class="wrap">
<h1>아동 안전 표준</h1>
<p class="meta">버블톡 · 운영 {OPERATOR}</p>
<div class="summary">버블톡은 아동 성착취·학대(CSAE)와 아동 성착취물(CSAM)을 어떤 형태로도 허용하지 않아요.</div>
<h2>금지하는 행위</h2>
<ul>
<li>아동을 성적으로 착취하거나 학대하는 모든 내용과 행위</li>
<li>아동에게 성적으로 접근하거나 길들이는 행위(그루밍), 나이를 속여 접근하는 행위</li>
<li>아동을 위협하거나 대화를 다른 앱·사이트로 유도해 해치려는 행위</li>
</ul>
<h2>앱을 만든 방식</h2>
<ul>
<li>대화로 사진·이미지·파일을 보낼 수 없어요. 링크는 글자로만 보이고 눌러도 열리지 않아요.</li>
<li>낯선 사람을 추천하거나 무작위로 연결하지 않아요.</li>
<li>만 14세 미만은 보호자 동의가 있어야 계정이 열려요.</li>
<li>만 14세 미만의 새 친구는 보호자가 승인해야 맺어지고, 보호자는 대화 기능을 끌 수 있어요.</li>
<li>아이가 처음 대화하기 전에 안전 안내를 보여 줘요.</li>
<li>전화번호처럼 보이는 내용을 쓰면 보내기 전에 경고해요.</li>
</ul>
<h2>신고와 조치</h2>
<ul>
<li>앱 안에서 버블과 프로필을 신고할 수 있고, 신고한 사람은 상대에게 알리지 않아요.</li>
<li>운영자가 신고를 확인해 경고, 이용 정지, 영구 정지로 조치해요. 아동에게 성적으로 접근하거나 위협한 경우는 바로 영구 정지해요.</li>
<li>아동 성착취물이나 아동에 대한 위험을 알게 되면 해당 내용을 삭제하고, 관련 법령에 따라 수사기관과 관계 기관에 알려요.</li>
<li>대한민국 법령을 포함해 적용되는 아동 보호 법령을 지켜요.</li>
</ul>
<h2>연락처</h2>
<p>아동 안전 담당 연락처: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p>아이가 지금 위험하다면 112(경찰)에 바로 신고해 주세요.</p>
<h2 lang="en">Child Safety Standards (English)</h2>
<div lang="en">
<p>Bubble Talk, operated by Maison de Moi, prohibits child sexual abuse and exploitation (CSAE) and child sexual abuse material (CSAM) in any form, including grooming and threats against children.</p>
<p>The app does not allow images or files in chats, does not connect strangers, and requires guardian consent for users under 14. Guardians approve new friends for those accounts.</p>
<p>Users can report bubbles and profiles inside the app. We review reports and warn, suspend, or permanently ban violators. We remove CSAM when we learn of it and report to law enforcement and relevant authorities as required by law.</p>
<p>Child safety contact: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
</div>
</div></article>'''

(OUT / 'index.html').write_text(page('index.html', '소개', DESC, index_main), encoding='utf-8')
(OUT / 'child-safety.html').write_text(
    page('child-safety.html', '아동 안전 표준', '버블톡 아동 안전 표준과 신고·조치 방법', safety_main), encoding='utf-8')
(OUT / 'admin.html').write_text(page('admin.html', '운영자 화면', '버블톡 운영자 화면',
    board('운영자 화면', '신고를 확인하고 이용을 제한해요', 'admin'),
    '<meta name="robots" content="noindex">\n' + BOARD_HEAD), encoding='utf-8')
(OUT / 'terms.html').write_text(page('terms.html', '서비스 이용약관', '버블톡 서비스 이용약관', terms_main), encoding='utf-8')
(OUT / 'privacy.html').write_text(page('privacy.html', '개인정보 처리방침', '버블톡 개인정보 처리방침', privacy_main), encoding='utf-8')
(OUT / 'delete-account.html').write_text(
    page('delete-account.html', '계정 삭제 요청', '버블톡 계정과 개인정보 삭제를 요청하는 방법', delete_main), encoding='utf-8')
(OUT / '404.html').write_text(
    re.sub(r'(href|src)="(?!https?:|mailto:|#|/)', r'\1="/', page('404.html', '페이지 없음', DESC, notfound_main)),
    encoding='utf-8')
(OUT / 'notice.html').write_text(page('notice.html', '공지사항', '버블톡 공지사항',
    board('공지사항', '버블톡 소식과 업데이트, 점검 안내', 'notice'), BOARD_HEAD), encoding='utf-8')
(OUT / 'inquiry.html').write_text(page('inquiry.html', '문의하기', '버블톡 문의하기',
    board('문의하기', '버블톡 계정으로 로그인해서 남겨요. 쓴 사람과 운영자만 볼 수 있어요.', 'inquiry'), BOARD_HEAD),
    encoding='utf-8')
print('ok', len(sections), 'terms sections')
