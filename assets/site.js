// 첫 화면: 떠다니는 방울을 누르면 퐁 (앱의 퐁 소리 1번), 대화 흉내 버블은 차례로 떠올랐다 터짐
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

  // 떠다니는 방울
  var field = document.querySelector('.bubbles');
  if (field && !reduce) {
    var made = 0;
    function addBubble() {
      var b = document.createElement('button');
      b.type = 'button';
      b.className = 'bubble';
      b.setAttribute('aria-label', '방울 터뜨리기');
      var size = 18 + Math.random() * 46;
      b.style.width = b.style.height = size + 'px';
      b.style.left = (Math.random() * 96) + '%';
      b.style.bottom = '-80px';
      var dur = 14 + Math.random() * 16;
      b.style.animationDuration = dur + 's';
      b.style.animationDelay = (made < 8 ? -Math.random() * dur : 0) + 's';
      b.addEventListener('click', function () {
        pop();
        b.classList.add('popped');
        setTimeout(function () { b.remove(); }, 320);
      });
      b.addEventListener('animationiteration', function () { b.style.left = (Math.random() * 96) + '%'; });
      field.appendChild(b);
      made++;
    }
    for (var i = 0; i < 10; i++) addBubble();
    setInterval(function () { if (field.children.length < 10) addBubble(); }, 2500);
  }

  // 대화 흉내: 버블이 떠올랐다 옅어지고 퐁 하고 사라짐 → 다음 대화
  var chat = document.querySelector('.chat .lines');
  if (chat && !reduce) {
    var script = [
      ['them', '오늘 숙제 뭐였지?'],
      ['mine', '수학 익힘책 24쪽!'],
      ['them2', '나도 지금 하는 중 ㅋㅋ'],
      ['mine', '다 하면 퀴즈방에서 구구단 한 판?'],
      ['them', '좋아 🙌'],
    ];
    var i = 0;
    function next() {
      var item = script[i % script.length];
      var el = document.createElement('div');
      el.className = 'b ' + item[0];
      el.textContent = item[1];
      chat.appendChild(el);
      i++;
      // 오래된 버블부터 옅어지다 터짐
      var all = chat.querySelectorAll('.b:not(.pop)');
      if (all.length > 3) {
        all[0].classList.add('fade');
      }
      if (all.length > 4) {
        var old = all[0];
        old.classList.add('pop');
        setTimeout(function () { old.remove(); }, 400);
      }
      setTimeout(next, 1900);
    }
    chat.innerHTML = '';
    setTimeout(next, 500);
  }
})();
