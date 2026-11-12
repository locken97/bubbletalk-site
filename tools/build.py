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


NAV = [('index.html', '소개'), ('guardian.html', '보호자 안내'), ('faq.html', '자주 묻는 질문'), ('notice.html', '공지사항'), ('inquiry.html', '문의하기')]


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
<link rel="stylesheet" href="assets/style.css?v=4">
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
      <p><strong>버블톡</strong> · 운영 {OPERATOR} · 대표 심자영</p>
      <p>문의 <a href="inquiry.html">문의하기</a> · <a href="mailto:{EMAIL}">{EMAIL}</a></p>
      <p>© 2026 버블톡. All rights reserved.</p>
    </div>
    <div class="links">
      <a href="guardian.html">보호자 안내</a>
      <a href="faq.html">자주 묻는 질문</a>
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
      <h1 id="headline">숙제처럼 미뤄 두고<br>읽는 글이 아니라,<br><em>지금 함께 나누고 싶은</em> 대화</h1>
      <script>
      // 대표 문구와 아래 문구: 들어올 때마다 하나 (직전 문구는 피함). 글자가 바뀌어 보이지 않게 제목 바로 뒤에서 처리
      (function () {
        var H = [
          ['숙제처럼 미뤄 두고<br>읽는 글이 아니라,<br><em>지금 함께 나누고 싶은</em> 대화', '아이부터 어른까지 함께 쓰는 버블 메신저'],
          ['남기지 않아도 되는 <em>말</em>이<br>더 많으니까요', '오늘 점심 메뉴, 잠깐의 농담, 가벼운 안부까지'],
          ['쌓이는 건 대화가 아니라<br><em>사이</em>니까요', '가족, 친구, 동료와 가볍게 나누는 메신저']
        ];
        var last = -1;
        try { last = parseInt(localStorage.getItem('bt-head'), 10); } catch (e) {}
        var i = Math.floor(Math.random() * H.length);
        if (i === last) i = (i + 1) % H.length;
        try { localStorage.setItem('bt-head', String(i)); } catch (e) {}
        document.getElementById('headline').innerHTML = H[i][0];
        document.write('<p class="hero-sub">' + H[i][1] + '</p>');
      })();
      </script>
      <noscript><p class="hero-sub">아이부터 어른까지 함께 쓰는 버블 메신저</p></noscript>
      <p class="lead">말하고, 보고, 퐁! 버블톡은 말풍선이 정해진 시간만 떠 있다가 사라지는 메신저예요.
        쌓이는 기록 대신, 지금 나누는 대화에 집중할 수 있어요.</p>
      <div class="badges">
        <span class="soon">구글 플레이 출시 준비 중</span>
        <a class="ghost" href="#features">어떻게 다른가요</a>
      </div>
    </div>
    <div class="chat" aria-label="버블톡 대화 예시">
      <div class="room"><span id="room-name">3팀 점심</span><small id="room-meta">6명 · 버블 수명 10분</small></div>
      <div class="strip" id="room-strip" hidden></div>
      <div class="lines">
        <div class="b them">오늘 12시 반에 내려갈게요</div>
        <div class="b mine">저는 10분만 늦을 것 같아요</div>
        <div class="b them2">먼저 가서 자리 잡아 둘게요</div>
      </div>
    </div>
  </div>
</section>

<section class="block" id="screens">
  <div class="wrap">
    <h2>앱 화면</h2>
    <p class="sub">개발 중인 실제 앱 화면이에요. 출시 전에 조금씩 바뀔 수 있어요.</p>
    <div class="shots">
      <figure class="shot"><img src="assets/screens/1_dm_pop.webp?v=2" width="540" height="1088" loading="lazy" alt="버블톡 앱 화면: 말하고 나면 퐁">
        <figcaption><b>말하고 나면 퐁</b>정한 시간이 지나면 버블이 사라져요</figcaption></figure>
      <figure class="shot"><img src="assets/screens/2_lifetime.webp?v=2" width="540" height="1088" loading="lazy" alt="버블톡 앱 화면: 버블 수명은 방마다">
        <figcaption><b>버블 수명은 방마다</b>30초부터 24시간까지 골라요</figcaption></figure>
      <figure class="shot"><img src="assets/screens/3_guardian.webp?v=2" width="540" height="1088" loading="lazy" alt="버블톡 앱 화면: 보호자가 함께">
        <figcaption><b>보호자가 함께</b>대화 기능, 쉬는 시간, 친구 승인을 정해요</figcaption></figure>
      <figure class="shot"><img src="assets/screens/4_qr.webp?v=2" width="540" height="1088" loading="lazy" alt="버블톡 앱 화면: QR로 친구 맺기">
        <figcaption><b>QR로 친구 맺기</b>전화번호 없이 아이디와 QR로 연결돼요</figcaption></figure>
      <figure class="shot"><img src="assets/screens/5_group.webp?v=2" width="540" height="1088" loading="lazy" alt="버블톡 앱 화면: 가족 단체방">
        <figcaption><b>가족 단체방</b>띠와 핀버블로 공지는 남기고, 공감으로 답해요</figcaption></figure>
      <figure class="shot"><img src="assets/screens/6_quiz.webp?v=2" width="540" height="1088" loading="lazy" alt="버블톡 앱 화면: 함께 푸는 퀴즈">
        <figcaption><b>함께 푸는 퀴즈</b>스피드 퀴즈로 누가 먼저 맞히는지 겨뤄요</figcaption></figure>
    </div>
  </div>
</section>

<section class="block alt" id="features">
  <div class="wrap">
    <h2>버블톡은 이렇게 달라요</h2>
    <p class="sub">기록을 남기는 메신저가 아니라, 대화하는 순간을 위한 메신저예요.</p>
    <div class="grid">
      <div class="card c-sky"><div class="dot">🫧</div><h3>사라지는 버블</h3>
        <p>버블은 방마다 정한 시간(30초~24시간)만 떠 있다가 퐁 하고 사라져요. 간직하고 싶은 버블만 길게 눌러 내 휴대폰에 보관해요.</p></div>
      <div class="card c-me"><div class="dot">🔒</div><h3>운영자도 못 읽는 버블</h3>
        <p>1:1 대화와 단체방의 버블은 종단간 암호화되어 대화 상대의 휴대폰에서만 열려요. 신고에 첨부한 버블과 퀴즈 답, 버블에 단 공감은 서버에 저장돼요.</p></div>
      <div class="card c-mint"><div class="dot">✉️</div><h3>메일 하나로 가볍게</h3>
        <p>전화번호도 실명도 묻지 않아요. 메일로 가입하고, 아이디를 알려 주거나 초대 링크를 보내 친구를 맺어요.</p></div>
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
    <h2>어린이도 안전하게 쓸 수 있도록</h2>
    <p class="sub">아이에게 처음 쥐여 주는 메신저가 될 수 있도록 만들고 있어요. 자세한 내용은 <a href="guardian.html">보호자 안내</a>에서 볼 수 있어요.</p>
    <ul class="promise">
      <li>일반 대화 내용은 운영자가 읽을 수 없고, 광고·분석에 쓰지 않아요.</li>
      <li>전화번호와 실명을 받지 않아요. 주소록은 읽지 않고, 초대할 사람만 직접 골라요.</li>
      <li>사진·이미지·파일 보내기가 없어요. 링크는 눌러도 열리지 않고 글자로만 보여요.</li>
      <li>만 14세 미만은 보호자 동의로 계정이 열리고, 어른과 친구가 될 때는 보호자가 승인해요.</li>
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
<script src="assets/site.js?v=3" defer></script>'''

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
<li>운영자는 일반 대화 내용을 읽을 수 있는 형태로 서버에 저장하거나 백업하지 않으며, 광고·추천·분석에 쓰지 않습니다.</li>
<li>1:1 대화와 단체방의 버블, 띠, 핀버블은 보내는 회원의 휴대폰에서 암호화(종단간 암호화)되어 그 대화의 회원 휴대폰에서만 열 수 있습니다.</li>
<li>1:1 버블은 상대 화면에 띄워질 때까지, 단체방 버블은 수명이 끝날 때까지 암호화된 상태로 서버에 머뭅니다. 아무도 보지 않은 버블은 24시간 뒤 지워지고, 띠와 핀버블은 게시되어 있는 동안 머뭅니다.</li>
<li>수명이 남은 1:1 버블은 앱을 다시 열 때 보여 주기 위해 휴대폰에 암호화되어 잠시 보관됩니다.</li>
<li>회원이 신고할 때 직접 첨부한 버블과 신고 사유는 신고 처리를 위해 저장됩니다.</li>
<li>퀴즈의 문제·정답·답은 서버가 채점해야 하므로 종단간 암호화하지 않고 서버에 저장됩니다(위 4번의 기간 동안).</li>
<li>버블에 단 공감(공감 종류와 공감한 회원)은 대화 내용이 아니어서 암호화하지 않고 서버에 저장되며, 그 버블이 사라질 때 함께 지워집니다.</li>
</ul>

<h2>6. 만 14세 미만 아동의 개인정보</h2>
<h3>동의 방법</h3>
{body_html(gs['동의 방법'])}
<h3>아이에게서 받는 정보</h3>
{body_html(gs['아이에게서 받는 정보'])}
<h3>보호자의 권리</h3>
{body_html(gs['보호자의 권리'])}

<h2>7. 처리 위탁과 국외 이전</h2>
<p>서비스 제공을 위해 다음 업체에 개인정보 처리를 맡기며, 일부는 국외로 이전됩니다. 국외 이전은 계약 이행에 필요한 처리위탁·보관으로서 「개인정보 보호법」 제28조의8 제1항 제3호 가목에 따라 이 처리방침에 공개합니다.</p>
<table class="plain">
<tr><th>Supabase Pte. Ltd.(싱가포르), Supabase, Inc.(미국)</th><td><b>맡기는 일:</b> 회원 정보·친구·대화방 정보·프로필 사진 저장<br><b>이전 항목:</b> 위 1번의 서비스 정보<br><b>국가:</b> 저장은 대한민국 서울. 기술 지원·운영에 필요할 때 싱가포르·미국 등에서 접근할 수 있고, 프로필 사진은 전 세계 전송망을 거칠 수 있습니다<br><b>연락처:</b> supabase.com/contact-us</td></tr>
<tr><th>Google LLC(미국) Firebase</th><td><b>맡기는 일:</b> 휴대폰 알림 전송, 앱 오류 수집<br><b>이전 항목:</b> 알림 열쇠, 방 번호, 보낸 사람 닉네임, 앱 오류 정보(버블 내용 없음)<br><b>국가:</b> 미국 등 구글 서버 소재지<br><b>연락처:</b> support.google.com/policies/contact/general_privacy_form</td></tr>
<tr><th>Google LLC(미국) Gmail</th><td><b>맡기는 일:</b> 가입 확인 코드, 비밀번호 찾기, 보호자 동의·안내 메일 보내기와 받기<br><b>이전 항목:</b> 이메일, 메일 내용, 보호자 이름<br><b>국가:</b> 미국 등 구글 서버 소재지<br><b>연락처:</b> support.google.com/policies/contact/general_privacy_form</td></tr>
</table>
<p>이전 시기와 방법은 서비스를 쓰는 동안 네트워크로 전송하는 것입니다. 보유 기간은 위 4번과 같거나 위탁 계약이 끝날 때까지입니다. 국외 이전을 거부하려면 탈퇴하면 되고, 거부하면 서비스를 쓸 수 없습니다.</p>

<h2>8. 정보주체의 권리와 행사 방법</h2>
<p>회원(만 14세 미만은 보호자)은 언제든 개인정보 열람, 정정, 삭제, 처리 정지를 요청하고 동의를 철회할 수 있습니다.
앱의 설정에서 직접 하거나 <a href="mailto:{EMAIL}">{EMAIL}</a>으로 요청하면 지체 없이 처리합니다.
계정 삭제는 <a href="delete-account.html">계정 삭제 요청</a> 안내를 참고해 주세요.</p>

<h2>9. 안전성 확보 조치</h2>
<ul>
<li>비밀번호는 원래 글자를 알 수 없는 방식으로 암호화하여 저장합니다.</li>
<li>1:1 대화와 단체방은 종단간 암호화하며, 대화 암호화용 비밀 열쇠는 회원의 휴대폰에만 있습니다.</li>
<li>서버의 개인정보에는 꼭 필요한 기능만 접근할 수 있도록 권한을 나눠 둡니다.</li>
<li>휴대폰에 보관한 버블은 휴대폰의 보안 저장소에 암호화하여 저장합니다.</li>
</ul>

<h2>10. 자동으로 수집하는 장치</h2>
<p>버블톡 앱과 이 사이트는 광고나 행동 분석을 위한 쿠키·추적 도구를 쓰지 않습니다. 사이트에서 공지사항·문의하기에 로그인하면 로그인 상태를 기억하기 위해 그 브라우저의 저장소에 로그인 열쇠를 저장하며, 로그아웃하면 지워집니다.</p>

<h2>11. 개인정보 보호책임자</h2>
<table class="plain">
<tr><th>운영자</th><td>{OPERATOR}</td></tr>
<tr><th>개인정보 보호책임자</th><td>심자영 (대표)</td></tr>
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
<tr><th>원래 없는 것</th><td>일반 대화 내용은 운영자가 읽을 수 없고 수명이 끝나면 사라져서, 따로 지울 것이 남지 않아요. 휴대폰 보관함에 담은 버블은 앱을 지우면 함께 지워져요.</td></tr>
</table>
</div></article>'''

notfound_main = '''<section class="block cta"><div class="wrap">
<h2>퐁! 이 페이지는 사라졌어요</h2>
<p class="sub">찾는 페이지가 없거나 주소가 바뀌었어요.</p>
<a class="ghost" id="open-app" href="index.html">첫 화면으로</a>
</div></section>
<script>
(function () {
  var seg = location.pathname.split('/').filter(Boolean);
  if (seg.length > 2 || (seg[0] !== 'i' && seg[0] !== 'r')) return;
  var room = seg[0] === 'r';
  document.title = (room ? '단체방 초대' : '친구 초대') + ' · 버블톡';
  document.querySelector('.cta h2').textContent = room ? '버블톡 단체방에 초대받았어요' : '버블톡 친구 초대를 받았어요';
  document.querySelector('.cta .sub').textContent = room
    ? '앱이 있으면 아래 버튼으로 열어 주세요. 링크는 24시간 동안 쓸 수 있고, 만 14세 미만은 링크로 들어갈 수 없어요. 버블톡은 지금 출시 준비 중이에요.'
    : '앱이 있으면 아래 버튼으로 열어 주세요. 버블톡은 지금 출시 준비 중이에요.';
  var btn = document.getElementById('open-app');
  btn.textContent = '버블톡 앱에서 열기';
  btn.href = /Android/i.test(navigator.userAgent)
    ? 'intent://bubbletalk.kr' + location.pathname + location.search + '#Intent;scheme=https;package=kr.bubbletalk.app;end'
    : 'index.html';
})();
</script>'''

guardian_main = '''<article class="doc"><div class="wrap">
<h1>보호자 안내</h1>
<p class="meta">만 14세 미만 아이가 버블톡을 쓸 때 알아 두실 내용이에요.</p>
<div class="summary">버블톡은 대화 내용을 보호자에게 보여 주지 않아요. 대신 가입 동의, 어른 친구 승인, 대화 기능 끄기로 함께 지켜봐 주실 수 있어요.</div>

<h2>가입 방법</h2>
<ol>
<li>아이 휴대폰에서 가입을 시작하고 생년월일을 넣어요. 버블톡은 만 7세부터 쓸 수 있어요.</li>
<li>보호자 이메일을 적으면 동의 메일이 가요. 스팸함도 확인해 주세요.</li>
<li>메일을 읽고 <strong>동의</strong>라고 답장해 주세요. 그때부터 아이 계정을 쓸 수 있어요.</li>
<li>5일 안에 답장이 없으면 아이 계정과 받은 정보를 지워요.</li>
</ol>

<h2>보호자가 할 수 있는 것</h2>
<p>동의 메일을 받은 이메일로 버블톡에 가입하면, 앱의 <strong>내 아이 계정</strong> 화면을 쓸 수 있어요.</p>
<table class="plain">
<tr><th>어른과 친구 맺기</th><td>아이가 만 14세 이상과 친구가 되려면 보호자 승인이 필요해요. 메일이나 앱에서 상대의 닉네임과 아이디를 보고 정해요. 보호자 계정과 내 아이는 승인 없이 바로 친구가 돼요.</td></tr>
<tr><th>친구 관리</th><td>앱에서 아이의 어른(만 14세 이상) 친구를 모두 보고 끊을 수 있어요. 상대에게는 알리지 않고, 다시 친구가 되려면 보호자 승인이 필요해요.</td></tr>
<tr><th>아이끼리 친구</th><td>보호자 승인이나 안내 없이 아이들끼리 자연스럽게 친구가 돼요.</td></tr>
<tr><th>단체방 입장 승인</th><td>초대받은 방에 아이의 친구가 아닌 어른이 있으면 보호자가 승인해야 들어가요. 메일이나 앱에서 방 이름, 방장, 어른 수를 보고 정해요. 나중에 그런 어른이 방에 들어오면 메일로 알려 드려요.</td></tr>
<tr><th>대화 기능 끄기</th><td>끄면 아이는 버블을 보내거나 받지 못하고 친구도 추가할 수 없어요.</td></tr>
<tr><th>대화 쉬는 시간</th><td>매일 정한 시간에는 대화 기능을 끈 것과 같아져요. 아이가 직접 풀 수 없고, 보호자만 앱에서 바꿀 수 있어요. 기본은 꺼짐이에요.</td></tr>
<tr><th>알림 끄는 시간</th><td>정한 시간에는 휴대폰 알림만 울리지 않아요. 대화를 막는 기능은 아니에요. 기본은 밤 10시부터 아침 7시까지예요.</td></tr>
<tr><th>계정 관리</th><td>만 14세가 되는 날을 확인하고, 아이 계정 탈퇴를 신청할 수 있어요.</td></tr>
</table>

<h2>보호자도 볼 수 없는 것</h2>
<ul>
<li>아이의 대화 내용</li>
<li>아이끼리의 친구 관계 (어른 친구만 보여요)</li>
</ul>

<h2>아이를 위해 정해 둔 것</h2>
<ul>
<li>대화로 사진과 파일을 보낼 수 없어요. 링크는 글자로만 보이고 눌러도 열리지 않아요.</li>
<li>아이는 단체방 초대 링크로 들어갈 수 없고, 아이가 있는 방은 초대 링크를 쓸 수 없어요.</li>
<li>모르는 어른이 있는 단체방은 보호자가 승인해야 들어가요.</li>
<li>첫 대화 전에 온라인 안전 안내를 보여 줘요.</li>
<li>전화번호처럼 보이는 내용을 쓰면 보내기 전에 알려 줘요.</li>
<li>낯선 사람을 추천하거나 무작위로 연결하지 않아요.</li>
</ul>

<h2>꼭 알아 두세요</h2>
<ul>
<li>가입할 때 나이는 입력한 생년월일로 확인해요. 신분증이나 휴대폰 인증은 하지 않아서, 어른이 아이인 척할 수 있어요.</li>
<li>아이끼리 친구는 보호자에게 알리지 않아요. 아이와 친구 이야기를 자주 나눠 주세요. 이상한 상대는 아이가 직접 신고하고 차단할 수 있어요.</li>
<li>대화 상대가 화면을 캡처하거나 내용을 적어 둘 수 있어요.</li>
</ul>

<h2>아이와 함께 이야기해 주세요</h2>
<ul>
<li>모르는 사람의 친구 요청은 받지 않기</li>
<li>집 주소, 학교, 전화번호, 사진을 다른 앱으로 보내 달라는 말에 응하지 않기</li>
<li>불편한 대화는 바로 신고하고 어른에게 말하기</li>
</ul>

<h2>문제가 생겼을 때</h2>
<p>앱에서 버블이나 프로필을 신고해 주세요. 신고한 사람은 상대에게 알리지 않아요. <a href="child-safety.html">아동 안전 표준</a>도 함께 볼 수 있고, 보호자 문의는 <a href="inquiry.html">문의하기</a>나 <a href="mailto:{EMAIL}">{EMAIL}</a>으로 보내 주세요.</p>
<p><strong>아이가 지금 위험하다면 112에 바로 신고해 주세요.</strong></p>
</div></article>'''.replace('{EMAIL}', EMAIL)

FAQ = [
    ('버블톡', [
        ('버블톡은 어떤 앱인가요?', '말풍선(버블)이 정해진 시간만 떠 있다가 사라지는 메신저예요. 글과 이모티콘으로 대화해요.'),
        ('어디서 받을 수 있나요?', '지금은 출시 준비 중이에요. 안드로이드를 먼저 준비하고 있고, 아이폰 출시 일정은 아직 정해지지 않았어요.'),
        ('휴대폰 두 대에서 같은 아이디를 쓸 수 있나요?', '아니요. 먼저 로그인한 휴대폰 한 대에서만 쓸 수 있어요. 휴대폰을 바꿀 때는 쓰던 휴대폰에서 로그아웃해 주세요. 휴대폰을 잃어버렸다면 로그인 화면의 비밀번호 찾기로 새 비밀번호를 정하면 돼요.'),
    ]),
    ('대화', [
        ('버블은 언제 사라지나요?', '방마다 정한 수명이 지나면 사라져요. 수명은 30초부터 24시간까지 고를 수 있고, 새 방은 1분으로 시작해요. 다른 사람이 화면에서 본 때부터 수명이 시작돼요.'),
        ('사라진 버블을 되살릴 수 있나요?', '아니요, 운영자도 되살릴 수 없어요. 간직하고 싶은 버블은 사라지기 전에 보관함에 담아 주세요. 보관함은 내 휴대폰에만 있고, 휴대폰을 바꾸면 옮겨지지 않아요.'),
        ('운영자가 대화를 볼 수 있나요?', '일반 대화는 종단간 암호화되어 볼 수 없어요. 신고할 때 첨부한 버블은 처리를 위해 운영자에게 전달되고, 퀴즈의 문제와 답은 채점을 위해 서버에서 처리돼요.'),
        ('화면 캡처를 막아 주나요?', '막지 않고, 캡처했다는 알림도 없어요. 개인정보나 비밀번호는 대화로 보내지 마세요.'),
        ('사진을 보낼 수 있나요?', '대화로는 보낼 수 없어요. 프로필 사진과 배경 사진만 올릴 수 있고, 친구에게만 보여요.'),
    ]),
    ('친구와 단체방', [
        ('전화번호가 없어도 친구가 될 수 있나요?', '네. 아이디 찾기, QR, 초대 링크로 친구가 될 수 있어요. 전화번호는 받지 않아요.'),
        ('단체방에는 몇 명까지 들어갈 수 있나요?', '100명까지예요. 방장은 띠와 핀버블로 공지를 남길 수 있어요.'),
        ('단체방 초대 링크는 어떻게 쓰나요?', '방장이 메뉴에서 만들고 24시간 동안 쓸 수 있어요. 만 14세 미만은 링크로 들어갈 수 없고, 아이가 있는 방은 링크를 쓸 수 없어요.'),
        ('퀴즈방은 무엇인가요?', '방장이 문제를 내고 모두 함께 푸는 방이에요. 기본 문제나 직접 만든 문제로 객관식, 주관식, 스피드 퀴즈를 할 수 있어요.'),
    ]),
    ('계정과 안전', [
        ('몇 살부터 쓸 수 있나요?', '만 7세부터 쓸 수 있어요. 만 14세 미만은 보호자 동의가 필요해요. 자세한 내용은 보호자 안내를 봐 주세요.'),
        ('로그인이 안 돼요.', '비밀번호를 5번 틀리면 그 휴대폰에서 10분 동안 로그인할 수 없어요. 다른 휴대폰에 이미 로그인되어 있어도 막혀요. 쓰던 휴대폰에서 로그아웃하거나, 로그인 화면의 비밀번호 찾기로 새 비밀번호를 정해 주세요.'),
        ('내가 하지 않은 로그인 시도 알림을 받았어요.', '다른 휴대폰에서 내 아이디로 로그인을 시도했다는 뜻이에요. 그 로그인은 막혔어요. 본인이 한 일이 아니라면 설정에서 비밀번호를 바꿔 주세요.'),
        ('휴대폰을 바꾸면 대화는 어떻게 되나요?', '이전 휴대폰으로 받지 못한 1:1 버블은 지워지고, 보낸 사람에게 알림풍선으로 알려 줘요. 보관함도 옮겨지지 않아요.'),
        ('가입한 이메일을 쓸 수 없어요.', '로그인 화면의 비밀번호 찾기에서 가입 이메일을 쓸 수 없어요를 눌러 운영자에게 메일을 보내 주세요. 버블톡 아이디, 가입할 때 쓴 이메일, 새 이메일을 적어 주시면 확인한 뒤 바꿔 드려요. 만 14세 미만 아이 계정은 보호자가 보호자 이메일로 보내 주세요.'),
        ('보호자 동의 메일이 오지 않아요.', '스팸함을 먼저 확인해 주세요. 그래도 없으면 bubbletalk.service@gmail.com으로 알려 주세요.'),
        ('버블톡 아이디를 바꿀 수 있나요?', '가입한 뒤에는 바꿀 수 없어요. 실명이나 학교 이름 같은 개인정보가 들어간 경우처럼 꼭 필요할 때만 메일로 요청해 주세요. 운영자가 검토하고, 예전 아이디는 다시 쓸 수 없어요.'),
        ('생년월일을 잘못 넣었어요.', '앱에서는 바꿀 수 없어요. 문의하기로 알려 주시면 확인해 드려요.'),
        ('불쾌한 대화를 받았어요.', '앱에서 그 버블이나 프로필을 신고하고 상대를 차단해 주세요. 신고한 사람은 상대에게 알리지 않아요.'),
        ('탈퇴하면 어떻게 되나요?', '신청하고 7일 뒤 계정이 삭제되고, 7일 안에 다시 로그인하면 복구돼요. 자세한 내용은 계정 삭제 요청 페이지를 봐 주세요.'),
    ]),
]
faq_main = '<article class="doc"><div class="wrap">\n<h1>자주 묻는 질문</h1>\n'
for _group, _items in FAQ:
    faq_main += f'<h2>{html.escape(_group)}</h2>\n'
    for _q, _a in _items:
        faq_main += f'<details class="faq"><summary>{html.escape(_q)}</summary><p>{html.escape(_a)}</p></details>\n'
faq_main += '<p class="meta">찾는 내용이 없으면 <a href="inquiry.html">문의하기</a>로 알려 주세요.</p>\n</div></article>'

BOARD_HEAD = ('<script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2.49.4/dist/umd/supabase.min.js"></script>\n'
              '<script src="assets/board.js?v=2"></script>\n')


def board(title, lead, call):
    return f'''<article class="doc"><div class="wrap">
<div class="account" id="account"></div>
<h1>{title}</h1>
<p class="meta">{lead}</p>
<div id="board"><p class="empty">불러오는 중…</p></div>
</div></article>
<script>document.addEventListener('DOMContentLoaded', function () {{ BubbleBoard.{call}(); }});</script>'''


DESC = '숙제처럼 미뤄 두고 읽는 글이 아니라, 지금 함께 나누고 싶은 대화. 아이부터 어른까지 함께 쓰는 버블 메신저, 버블톡.'
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
<li>만 14세 미만이 만 14세 이상과 친구가 되려면 보호자가 승인해야 해요. 보호자는 아이의 어른 친구를 앱에서 보고 끊을 수 있고, 대화 기능도 끌 수 있어요.</li>
<li>만 14세 미만은 단체방 초대 링크로 들어갈 수 없고, 아이가 있는 단체방은 링크를 쓸 수 없어요.</li>
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
<p>아동 안전 담당: 심자영 (대표) · 연락처: <a href="mailto:{EMAIL}">{EMAIL}</a></p>
<p>아이가 지금 위험하다면 112(경찰)에 바로 신고해 주세요.</p>
<h2 lang="en">Child Safety Standards (English)</h2>
<div lang="en">
<p>Bubble Talk, operated by Maison de Moi, prohibits child sexual abuse and exploitation (CSAE) and child sexual abuse material (CSAM) in any form, including grooming and threats against children.</p>
<p>The app does not allow images or files in chats, does not connect strangers, and requires guardian consent for users under 14. Those accounts need guardian approval to become friends with users 14 or older. Guardians are told by email when two children become friends, can remove that friend, and can turn chat off. Users under 14 cannot join group rooms by link, rooms with a child cannot use invite links, and joining a room with adults they do not know needs guardian approval.</p>
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
(OUT / 'guardian.html').write_text(page('guardian.html', '보호자 안내', '만 14세 미만 아이가 버블톡을 쓸 때 보호자가 알아 둘 내용', guardian_main), encoding='utf-8')
(OUT / 'faq.html').write_text(page('faq.html', '자주 묻는 질문', '버블톡 자주 묻는 질문', faq_main), encoding='utf-8')
(OUT / 'notice.html').write_text(page('notice.html', '공지사항', '버블톡 공지사항',
    board('공지사항', '버블톡 소식과 업데이트, 점검 안내', 'notice'), BOARD_HEAD), encoding='utf-8')
(OUT / 'inquiry.html').write_text(page('inquiry.html', '문의하기', '버블톡 문의하기',
    board('문의하기', f'버블톡 계정으로 로그인해서 남겨요. 쓴 사람과 운영자만 볼 수 있어요.<br>로그인할 수 없거나 계정이 없으면 <a href="mailto:{EMAIL}">{EMAIL}</a>으로 보내 주세요. 메일에 비밀번호는 적지 마세요.', 'inquiry'), BOARD_HEAD),
    encoding='utf-8')
print('ok', len(sections), 'terms sections')
