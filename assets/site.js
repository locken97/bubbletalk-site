// 첫 화면: 들어올 때마다 예시 장면이 바뀜, 떠다니는 방울을 누르면 퐁 (앱의 퐁 소리 1번)
(function () {
  var reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var audio = null;
  function pop() {
    try {
      if (!audio) audio = new Audio('assets/pop.wav');
      var a = audio.cloneNode();
      a.volume = 0.5;
      a.play().catch(function () {});
    } catch (e) {}
  }

  // 떠다니는 방울: 수를 줄이고 천천히
  var field = document.querySelector('.bubbles');
  var MAX_BUBBLES = 4;
  if (field && !reduce) {
    var made = 0;
    function addBubble() {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'bubble';
      b.setAttribute('aria-label', '방울 터뜨리기');
      var size = 16 + Math.random() * 30;
      b.style.width = b.style.height = size + 'px';
      b.style.left = (Math.random() * 96) + '%';
      b.style.bottom = '-80px';
      var dur = 28 + Math.random() * 18;
      b.style.animationDuration = dur + 's';
      b.style.animationDelay = (made < MAX_BUBBLES ? -Math.random() * dur : 0) + 's';
      b.addEventListener('click', function () {
        pop();
        b.classList.add('popped');
        setTimeout(function () { b.remove(); }, 320);
      });
      b.addEventListener('animationiteration', function () { b.style.left = (Math.random() * 96) + '%'; });
      field.appendChild(b);
      made++;
    }
    for (var n = 0; n < MAX_BUBBLES; n++) addBubble();
    setInterval(function () { if (field.children.length < MAX_BUBBLES) addBubble(); }, 6000);
  }

  // 예시 장면: 들어올 때마다 하나 (직전 장면은 피함)
  var SCENES = [
    { room: '3팀 점심', meta: '6명 · 버블 수명 10분', line: '점심 메뉴까지 기록으로 남길 필요는 없으니까요.', talk: [
      ['them', '오늘 12시 반에 내려갈게요'],
      ['mine', '저는 10분만 늦을 것 같아요'],
      ['them2', '먼저 가서 자리 잡아 둘게요'],
      ['mine', '감사합니다 🙏'],
      ['them', '메뉴는 국밥으로 갑니다'],
    ] },
    { room: '우리 집', meta: '4명 · 버블 수명 1시간', line: '저녁 메뉴는 오늘만 알면 되니까요.', talk: [
      ['them', '엄마 저녁 뭐 사 갈까?'],
      ['mine', '두부만 사 와'],
      ['them2', '저는 오늘 조금 늦어요'],
      ['mine', '밥 남겨 둘게'],
      ['them', '네 😊'],
    ] },
    { room: '주말 러닝', meta: '12명 · 버블 수명 6시간', line: '약속만 잡히면, 나머지는 흘려보내도 괜찮아요.', talk: [
      ['them', '토요일 7시, 한강에서 봐요'],
      ['mine', '저 참석이요!'],
      ['them2', '비 오면 어떻게 해요?'],
      ['them', '그땐 일요일로 미뤄요'],
      ['mine', '좋아요 🙌'],
    ] },
    { room: '고등학교 동창', meta: '5명 · 버블 수명 30분', line: '시시콜콜한 얘기일수록 가볍게 나눠야 즐거우니까요.', talk: [
      ['them', '이번 주말 다들 시간 돼?'],
      ['mine', '토요일 저녁 좋아'],
      ['them2', '나도! 어디서 볼까'],
      ['mine', '지난번 그 집 어때'],
      ['them', 'ㅋㅋㅋ 거기 또?'],
    ] },
    { room: '2반 학부모', meta: '18명 · 버블 수명 1시간', strip: '내일 현장학습, 도시락 챙겨 주세요', line: '공지는 띠에 남기고, 잡담은 가볍게 흘려보내요.', talk: [
      ['them', '내일 준비물 공지 띠에 걸었어요'],
      ['mine', '감사합니다!'],
      ['them2', '간식도 보내도 되나요?'],
      ['them', '네, 간단한 것만요'],
      ['mine', '확인했어요 😊'],
    ] },
  ];

  var lines = document.querySelector('.chat .lines');
  if (!lines) return;
  var timer = null;
  var run = 0;

  function bubble(item) {
    var el = document.createElement('div');
    el.className = 'b ' + item[0];
    el.textContent = item[1];
    lines.appendChild(el);
  }

  function play(index) {
    var scene = SCENES[index];
    run++;
    clearTimeout(timer);
    document.getElementById('room-name').textContent = scene.room;
    document.getElementById('room-meta').textContent = scene.meta;
    document.getElementById('scene-line').textContent = scene.line;
    var strip = document.getElementById('room-strip');
    strip.hidden = !scene.strip;
    strip.textContent = scene.strip || '';
    lines.innerHTML = '';

    if (reduce) { scene.talk.slice(0, 3).forEach(bubble); return; }

    // 버블이 떠올랐다 옅어지고 퐁 하고 사라짐 → 다음 대화
    var mine = run;
    var i = 0;
    function next() {
      if (mine !== run) return;
      bubble(scene.talk[i % scene.talk.length]);
      i++;
      var all = lines.querySelectorAll('.b:not(.pop)');
      if (all.length > 3) all[0].classList.add('fade');
      if (all.length > 4) {
        var old = all[0];
        old.classList.add('pop');
        setTimeout(function () { old.remove(); }, 400);
      }
      timer = setTimeout(next, 2200);
    }
    timer = setTimeout(next, 500);
  }

  var last = -1;
  try { last = parseInt(localStorage.getItem('bt-scene'), 10); } catch (e) {}
  var pick = Math.floor(Math.random() * SCENES.length);
  if (pick === last) pick = (pick + 1) % SCENES.length;
  try { localStorage.setItem('bt-scene', String(pick)); } catch (e) {}
  play(pick);
})();
