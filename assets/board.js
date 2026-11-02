// 버블톡 사이트 게시판 (서버 27단계): 공지사항(누구나 읽기, 운영자 쓰기) · 문의(버블톡 계정, 쓴 사람과 운영자만)
// 운영자 화면 (서버 32단계): 신고 확인 · 이용 제한
// 로그인은 앱과 같은 방식: 아이디 또는 이메일 + 비밀번호 → resolve_login → 비밀번호 로그인
(function () {
  var SUPABASE_URL = 'https://lfiaqxbjadmefibiegvi.supabase.co';
  var SUPABASE_KEY = 'sb_publishable_closkDl2GlOanNTuvghRyQ_KzZcyC1X';
  var db = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY, {
    auth: { persistSession: true, storageKey: 'bubbletalk-site-auth' },
  });

  var CATEGORIES = { use: '사용 방법', account: '계정', report: '신고·안전', idea: '제안', etc: '기타' };

  function $(sel, root) { return (root || document).querySelector(sel); }
  function esc(s) {
    return String(s == null ? '' : s).replace(/[&<>"']/g, function (c) {
      return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c];
    });
  }
  function date(s, withTime) {
    var d = new Date(s);
    var t = d.getFullYear() + '.' + String(d.getMonth() + 1).padStart(2, '0') + '.' + String(d.getDate()).padStart(2, '0');
    if (withTime) t += ' ' + String(d.getHours()).padStart(2, '0') + ':' + String(d.getMinutes()).padStart(2, '0');
    return t;
  }
  function param(name) { return new URLSearchParams(location.search).get(name); }
  function go(query) { location.search = query; }
  function say(el, msg, bad) {
    el.innerHTML = '<p class="notice ' + (bad ? 'bad' : '') + '">' + esc(msg) + '</p>';
  }
  async function rpc(fn, args) {
    var r = await db.rpc(fn, args || {});
    if (r.error) throw r.error;
    return r.data;
  }

  // ── 로그인 ──
  var me = null;
  async function loadMe() {
    var s = await db.auth.getSession();
    if (!s.data.session) { me = null; return null; }
    try { me = await rpc('site_me'); } catch (e) { me = null; }
    return me;
  }

  function renderAccountBar(el, onChange) {
    if (!el) return;
    if (me) {
      el.innerHTML = '<span><strong>' + esc(me.nickname) + '</strong> @' + esc(me.handle) +
        (me.admin ? ' <a class="tag" href="admin.html">운영자 화면</a>' : '') + '</span>' +
        '<button type="button" class="linkish" id="logout">로그아웃</button>';
      $('#logout', el).onclick = async function () { await db.auth.signOut(); me = null; onChange(); };
    } else {
      el.innerHTML = '';
    }
  }

  function loginForm(el, onDone, why) {
    el.innerHTML =
      '<form class="form card-form" id="login-form">' +
      '<h2>버블톡 계정으로 로그인</h2>' +
      '<p class="hint">' + esc(why || '앱에서 쓰는 아이디(또는 이메일)와 비밀번호로 로그인해요.') + '</p>' +
      '<label>아이디 또는 이메일<input name="id" autocomplete="username" required></label>' +
      '<label>비밀번호<input name="pw" type="password" autocomplete="current-password" required></label>' +
      '<div id="login-msg"></div>' +
      '<button type="submit" class="btn">로그인</button>' +
      '</form>';
    $('#login-form', el).onsubmit = async function (ev) {
      ev.preventDefault();
      var f = ev.target;
      var msg = $('#login-msg', el);
      var id = f.id.value.trim();
      var pw = f.pw.value;
      f.querySelector('button').disabled = true;
      try {
        var r = await rpc('resolve_login', { p_identifier: id, p_password: pw });
        if (!r || r.status !== 'ok') {
          if (r && r.status === 'locked') {
            say(msg, '비밀번호를 여러 번 틀려서 잠시 잠겼어요. ' + date(r.until, true) + ' 이후에 다시 해 주세요.', true);
          } else {
            say(msg, '아이디·이메일 또는 비밀번호가 맞지 않아요.', true);
          }
          return;
        }
        var a = await db.auth.signInWithPassword({ email: r.email, password: pw });
        if (a.error) {
          var m = (a.error.message || '').toLowerCase();
          say(msg, m.indexOf('banned') >= 0
            ? '보호자 동의 전이거나 이용이 멈춘 계정이에요. 앱에서 확인해 주세요.'
            : '로그인하지 못했어요. 잠시 뒤에 다시 해 주세요.', true);
          return;
        }
        await loadMe();
        if (!me) {
          await db.auth.signOut();
          say(msg, '가입을 마치지 않은 계정이에요. 앱에서 가입을 이어서 해 주세요.', true);
          return;
        }
        onDone();
      } catch (e) {
        say(msg, '서버에 연결하지 못했어요. 잠시 뒤에 다시 해 주세요.', true);
      } finally {
        f.querySelector('button').disabled = false;
      }
    };
  }

  function text(s) { return '<div class="post-body">' + esc(s) + '</div>'; }

  // ── 공지사항 ──
  async function noticePage() {
    var root = $('#board');
    var bar = $('#account');
    await loadMe();
    function refresh() { noticePage(); }
    renderAccountBar(bar, refresh);
    var id = param('id');
    var mode = param('write');
    try {
      if (mode !== null && me && me.admin) return noticeEditor(root, mode ? Number(mode) : null);
      if (id) return noticeDetail(root, Number(id));
      var page = Number(param('page') || 0);
      var data = await rpc('site_notices', { p_page: page });
      var html = '';
      if (me && me.admin) html += '<p class="actions"><a class="btn" href="?write=">공지 쓰기</a></p>';
      if (!data.items.length) {
        html += '<p class="empty">아직 공지가 없어요.</p>';
      } else {
        html += '<ul class="list">' + data.items.map(function (n) {
          return '<li><a href="?id=' + n.id + '">' + (n.pinned ? '<span class="tag">고정</span> ' : '') +
            '<span class="t">' + esc(n.title) + '</span><span class="d">' + date(n.created_at) + '</span></a></li>';
        }).join('') + '</ul>';
        html += pager(page, data.total);
      }
      if (!me) html += '<p class="hint small">운영자는 <a href="#" id="admin-login">로그인</a>해서 공지를 쓸 수 있어요.</p>';
      root.innerHTML = html;
      var al = $('#admin-login');
      if (al) al.onclick = function (e) { e.preventDefault(); loginForm(root, refresh, '운영자 계정으로 로그인해요.'); };
    } catch (e) {
      say(root, '공지를 불러오지 못했어요. 잠시 뒤에 다시 해 주세요.', true);
    }
  }

  async function noticeDetail(root, id) {
    var n = await rpc('site_notice', { p_id: id });
    if (!n) { say(root, '없는 공지예요.', true); return; }
    root.innerHTML = '<article class="post"><h2>' + (n.pinned ? '<span class="tag">고정</span> ' : '') + esc(n.title) + '</h2>' +
      '<p class="meta">' + date(n.created_at) + (n.updated_at && n.updated_at.slice(0, 16) !== n.created_at.slice(0, 16) ? ' · 고침 ' + date(n.updated_at) : '') + '</p>' +
      text(n.body) + '</article>' +
      '<p class="actions"><a class="ghost" href="notice.html">목록</a>' +
      (me && me.admin ? ' <a class="ghost" href="?write=' + n.id + '">고치기</a> <button type="button" class="ghost danger" id="del">지우기</button>' : '') + '</p>';
    var del = $('#del');
    if (del) del.onclick = async function () {
      if (!confirm('이 공지를 지울까요? 되살릴 수 없어요.')) return;
      await rpc('site_notice_delete', { p_id: id });
      location.href = 'notice.html';
    };
  }

  async function noticeEditor(root, id) {
    var n = id ? await rpc('site_notice', { p_id: id }) : null;
    root.innerHTML = '<form class="form" id="nf"><h2>' + (id ? '공지 고치기' : '공지 쓰기') + '</h2>' +
      '<label>제목 (100자까지)<input name="title" maxlength="100" required value="' + esc(n ? n.title : '') + '"></label>' +
      '<label>내용 (5000자까지)<textarea name="body" maxlength="5000" rows="12" required>' + esc(n ? n.body : '') + '</textarea></label>' +
      '<label class="check"><input type="checkbox" name="pinned"' + (n && n.pinned ? ' checked' : '') + '> 맨 위에 고정</label>' +
      '<div id="nf-msg"></div>' +
      '<p class="actions"><button class="btn" type="submit">저장</button> <a class="ghost" href="notice.html' + (id ? '?id=' + id : '') + '">취소</a></p></form>';
    $('#nf').onsubmit = async function (ev) {
      ev.preventDefault();
      var f = ev.target;
      try {
        var nid = await rpc('site_notice_save', { p_id: id, p_title: f.title.value, p_body: f.body.value, p_pinned: f.pinned.checked });
        if (!nid) { say($('#nf-msg'), '저장하지 못했어요. 제목과 내용을 확인해 주세요.', true); return; }
        go('id=' + nid);
      } catch (e) {
        say($('#nf-msg'), '저장하지 못했어요. 잠시 뒤에 다시 해 주세요.', true);
      }
    };
  }

  function pager(page, total) {
    var pages = Math.ceil(total / 20);
    if (pages <= 1) return '';
    var keep = new URLSearchParams(location.search);
    function link(p, label) { keep.set('page', p); return '<a class="ghost" href="?' + keep.toString() + '">' + label + '</a>'; }
    return '<p class="actions pager">' + (page > 0 ? link(page - 1, '← 이전') : '') +
      ' <span>' + (page + 1) + ' / ' + pages + '</span> ' + (page < pages - 1 ? link(page + 1, '다음 →') : '') + '</p>';
  }

  // ── 문의 ──
  async function inquiryPage() {
    var root = $('#board');
    var bar = $('#account');
    await loadMe();
    function refresh() { inquiryPage(); }
    renderAccountBar(bar, refresh);
    if (!me) {
      loginForm(root, refresh, '문의는 버블톡 계정으로 로그인해서 남겨요. 쓴 사람과 운영자만 볼 수 있어요.');
      return;
    }
    var id = param('id');
    try {
      if (param('write') !== null) return inquiryEditor(root);
      if (id) return inquiryDetail(root, Number(id));
      var all = me.admin && param('all') === '1';
      var page = Number(param('page') || 0);
      var data = await rpc('site_inquiries', { p_all: all, p_page: page });
      var html = '<p class="actions"><a class="btn" href="?write=">문의 쓰기</a>' +
        (me.admin ? ' <a class="ghost' + (all ? '' : ' on') + '" href="inquiry.html">내 문의</a> <a class="ghost' + (all ? ' on' : '') + '" href="?all=1">모든 문의 (운영자)</a>' : '') + '</p>';
      if (!data.items.length) {
        html += '<p class="empty">' + (all ? '들어온 문의가 없어요.' : '아직 남긴 문의가 없어요.') + '</p>';
      } else {
        html += '<ul class="list">' + data.items.map(function (q) {
          return '<li><a href="?id=' + q.id + '"><span class="tag ' + (q.answered_at ? 'done' : '') + '">' + (q.answered_at ? '답변 완료' : '답변 대기') + '</span> ' +
            '<span class="t">' + esc(q.title) + '</span><span class="d">' +
            (all && q.author ? esc(q.author.nickname) + ' @' + esc(q.author.handle) + ' · ' : '') + date(q.created_at) + '</span></a></li>';
        }).join('') + '</ul>' + pager(page, data.total);
      }
      root.innerHTML = html;
    } catch (e) {
      say(root, '문의를 불러오지 못했어요. 잠시 뒤에 다시 해 주세요.', true);
    }
  }

  async function inquiryDetail(root, id) {
    var q = await rpc('site_inquiry', { p_id: id });
    if (!q) { say(root, '없거나 볼 수 없는 문의예요.', true); return; }
    var html = '<article class="post"><h2>' + esc(q.title) + '</h2>' +
      '<p class="meta">' + esc(CATEGORIES[q.category] || '기타') + ' · ' + date(q.created_at, true) +
      (me.admin && q.author ? ' · ' + esc(q.author.nickname) + ' @' + esc(q.author.handle) : '') + '</p>' +
      text(q.body) + '</article>';
    if (q.replies.length) {
      html += q.replies.map(function (r) {
        return '<article class="post reply"><p class="meta"><span class="tag done">버블톡 답변</span> ' + date(r.created_at, true) + '</p>' + text(r.body) + '</article>';
      }).join('');
    } else {
      html += '<p class="empty">아직 답변을 기다리고 있어요. 보통 2~3일 안에 답해 드려요.</p>';
    }
    if (me.admin) {
      html += '<form class="form" id="rf"><label>답변 쓰기 (3000자까지)<textarea name="body" maxlength="3000" rows="6" required></textarea></label>' +
        '<div id="rf-msg"></div><p class="actions"><button class="btn" type="submit">답변 올리기</button></p></form>';
    }
    html += '<p class="actions"><a class="ghost" href="inquiry.html' + (me.admin ? '?all=1' : '') + '">목록</a></p>';
    root.innerHTML = html;
    var rf = $('#rf');
    if (rf) rf.onsubmit = async function (ev) {
      ev.preventDefault();
      var ok = await rpc('site_inquiry_reply', { p_id: id, p_body: ev.target.body.value }).catch(function () { return false; });
      if (!ok) { say($('#rf-msg'), '올리지 못했어요.', true); return; }
      inquiryDetail(root, id);
    };
  }

  function inquiryEditor(root) {
    root.innerHTML = '<form class="form" id="qf"><h2>문의 쓰기</h2>' +
      '<p class="hint">쓴 사람과 운영자만 볼 수 있어요. 비밀번호·전화번호 같은 개인정보는 적지 말아 주세요.</p>' +
      '<label>종류<select name="category">' + Object.keys(CATEGORIES).map(function (k) {
        return '<option value="' + k + '">' + CATEGORIES[k] + '</option>';
      }).join('') + '</select></label>' +
      '<label>제목 (100자까지)<input name="title" maxlength="100" required></label>' +
      '<label>내용 (2000자까지)<textarea name="body" maxlength="2000" rows="10" required></textarea></label>' +
      '<div id="qf-msg"></div>' +
      '<p class="actions"><button class="btn" type="submit">보내기</button> <a class="ghost" href="inquiry.html">취소</a></p></form>';
    $('#qf').onsubmit = async function (ev) {
      ev.preventDefault();
      var f = ev.target;
      f.querySelector('button').disabled = true;
      try {
        var r = await rpc('site_inquiry_create', { p_category: f.category.value, p_title: f.title.value, p_body: f.body.value });
        if (r && r.id) { go('id=' + r.id); return; }
        var why = {
          title: '제목을 1~100자로 써 주세요.', body: '내용을 1~2000자로 써 주세요.',
          banned: '제목에 쓸 수 없는 말이 들어 있어요.', limit: '문의는 하루에 5개까지 남길 수 있어요.',
          login: '다시 로그인해 주세요.',
        }[r && r.error] || '보내지 못했어요.';
        say($('#qf-msg'), why, true);
      } catch (e) {
        say($('#qf-msg'), '보내지 못했어요. 잠시 뒤에 다시 해 주세요.', true);
      } finally {
        f.querySelector('button').disabled = false;
      }
    };
  }

  // ── 운영자 화면 ──
  var KINDS = { warning: '경고', suspend7: '7일 정지', suspend30: '30일 정지', permanent: '영구 정지' };
  var REPORT_KINDS = { dm: '1:1 대화', group: '단체방', profile: '프로필' };

  function who(p) {
    if (!p) return '알 수 없음';
    return esc(p.nickname) + ' @' + esc(p.handle) + (p.under14 ? ' <span class="tag">만 14세 미만</span>' : '');
  }

  // 지금까지 받은 제재로 다음 단계를 고름 (풀린 제재는 세지 않음)
  function nextKind(p) {
    var n = p.sanctions.filter(function (s) { return !s.lifted_at; }).length;
    return ['warning', 'suspend7', 'suspend30', 'permanent'][Math.min(n, 3)];
  }

  async function adminPage() {
    var root = $('#board');
    await loadMe();
    renderAccountBar($('#account'), adminPage);
    if (!me) {
      loginForm(root, adminPage, '운영자 계정으로 로그인해 주세요.');
      return;
    }
    if (!me.admin) {
      say(root, '운영자만 볼 수 있어요.', true);
      return;
    }
    try {
      var id = param('id');
      if (id) return await adminDetail(root, Number(id));
      var open = param('done') === null;
      var page = Number(param('page') || 0);
      var data = await rpc('admin_reports', { p_open: open, p_page: page });
      var html = '<p class="actions"><a class="ghost' + (open ? ' on' : '') + '" href="admin.html">처리 전</a> ' +
        '<a class="ghost' + (open ? '' : ' on') + '" href="?done=1">처리 완료</a></p>';
      if (!data.items.length) {
        html += '<p class="empty">' + (open ? '처리할 신고가 없어요.' : '처리한 신고가 없어요.') + '</p>';
      } else {
        html += '<ul class="list">' + data.items.map(function (r) {
          return '<li><a href="?id=' + r.id + '"><span class="tag">' + esc(REPORT_KINDS[r.kind] || r.kind) + '</span> ' +
            '<span class="t">' + esc(r.reason) + '</span><span class="d">' +
            (r.target ? esc(r.target.nickname) + ' · ' : '') + date(r.created_at, true) + '</span></a></li>';
        }).join('') + '</ul>' + pager(page, data.total);
      }
      root.innerHTML = html;
    } catch (e) {
      say(root, '신고를 불러오지 못했어요. 잠시 뒤에 다시 해 주세요.', true);
    }
  }

  async function adminDetail(root, id) {
    var r = await rpc('admin_report', { p_id: id });
    if (!r) { say(root, '없는 신고예요.', true); return; }
    var html = '<article class="post"><h2>' + esc(r.reason) + '</h2>' +
      '<p class="meta">' + esc(REPORT_KINDS[r.kind] || r.kind) + (r.room_name ? ' · ' + esc(r.room_name) : '') +
      ' · ' + date(r.created_at, true) + '</p>' +
      '<p>신고한 사람: ' + who(r.reporter) + '<br>신고 대상: ' + who(r.target) + '</p>';
    html += r.items.length ? '<ul>' + r.items.map(function (b) {
      return '<li><strong>' + esc(b.nickname || '알 수 없음') + '</strong> ' +
        (b.hidden ? '<span class="tag">가림</span> ' : '') + esc(b.text) + '</li>';
    }).join('') + '</ul>' : '<p class="meta">첨부한 버블이 없어요.</p>';
    html += r.handled_at
      ? '<p class="notice">처리 완료 · ' + date(r.handled_at, true) + (r.handled_note ? ' · ' + esc(KINDS[r.handled_note] || r.handled_note) : '') + '</p>'
      : '';
    html += '</article>';

    r.people.forEach(function (p, i) {
      html += '<article class="post"><p><strong>' + who(p) + '</strong> · 받은 신고 ' + p.reports + '건</p>';
      if (p.sanctions.length) {
        html += '<ul>' + p.sanctions.map(function (s) {
          var active = !s.lifted_at && (s.kind === 'permanent' || (s.until && new Date(s.until) > new Date()));
          return '<li>' + esc(KINDS[s.kind] || s.kind) + ' · ' + esc(s.reason) + ' · ' + date(s.started_at) +
            (s.lifted_at ? ' (풀림)' : '') +
            (active ? ' <button type="button" class="ghost danger" data-lift="' + s.id + '">풀기</button>' : '') + '</li>';
        }).join('') + '</ul>';
      }
      if (!r.handled_at) {
        var next = nextKind(p);
        html += '<form class="form" data-user="' + esc(p.id) + '" data-i="' + i + '">' +
          '<label>제재 단계<select name="kind">' + Object.keys(KINDS).map(function (k) {
            return '<option value="' + k + '"' + (k === next ? ' selected' : '') + '>' + KINDS[k] + '</option>';
          }).join('') + '</select></label>' +
          '<label>사유 (본인에게 보여요, 200자까지)<input name="reason" maxlength="200" value="' + esc(r.reason) + '" required></label>' +
          '<p class="actions"><button class="btn" type="submit">제재하기</button></p></form>';
      }
      html += '</article>';
    });

    if (!r.handled_at) {
      html += '<form class="form" id="close"><label>제재 없이 처리 (메모, 500자까지)<input name="note" maxlength="500"></label>' +
        '<p class="actions"><button class="btn" type="submit">처리 완료</button></p></form>';
    }
    html += '<div id="admin-msg"></div><p class="actions"><a class="ghost" href="admin.html">목록</a></p>';
    root.innerHTML = html;

    var fail = function () { say($('#admin-msg'), '처리하지 못했어요.', true); };
    root.querySelectorAll('form[data-user]').forEach(function (f) {
      f.onsubmit = async function (ev) {
        ev.preventDefault();
        var label = KINDS[f.kind.value];
        var name = r.people[Number(f.dataset.i)].nickname;
        if (!window.confirm(name + '님을 ' + label + ' 처리할까요?')) return;
        var ok = await rpc('admin_sanction', {
          p_user: f.dataset.user, p_kind: f.kind.value, p_reason: f.reason.value, p_report: id,
        }).catch(function () { return false; });
        if (ok) adminDetail(root, id); else fail();
      };
    });
    root.querySelectorAll('[data-lift]').forEach(function (b) {
      b.onclick = async function () {
        if (!window.confirm('이 제재를 풀까요?')) return;
        var ok = await rpc('admin_sanction_lift', { p_id: Number(b.dataset.lift) }).catch(function () { return false; });
        if (ok) adminDetail(root, id); else fail();
      };
    });
    var close = $('#close');
    if (close) close.onsubmit = async function (ev) {
      ev.preventDefault();
      var ok = await rpc('admin_report_close', { p_id: id, p_note: close.note.value }).catch(function () { return false; });
      if (ok) adminDetail(root, id); else fail();
    };
  }

  window.BubbleBoard = { notice: noticePage, inquiry: inquiryPage, admin: adminPage };
})();
