# 버블톡 사이트 (bubbletalk.kr)

GitHub Pages로 올리는 정적 사이트. 소개 · 이용약관 · 개인정보 처리방침 · 계정 삭제 요청.

- 약관·처리방침 문구는 앱 저장소의 `lib/data/terms.dart`에서 만듦:
  `python3 tools/build.py <앱 저장소 경로> .`
- 색·글꼴은 앱과 같게 (하늘색 #8ECDF2, 크림 #FFF8EE, 남색 #2F3554, Jua · Pretendard)
- `CNAME` = bubbletalk.kr
- `.well-known/assetlinks.json`: 초대 링크로 앱 열기 (출시 키 지문. 구글 플레이 앱 서명을 쓰면 플레이 지문도 추가)
- `assets/screens/`: 첫 화면 "앱 화면" 사진 6장 (540px webp, 원본은 프로젝트 파일 screenshots/). 실제 아이디·QR·초대 링크는 가린 뒤 넣음
- `child-safety.html`: 아동 안전 표준 (구글 플레이 제출용 주소), `admin.html`: 운영자 화면 (서버 32단계, 메뉴에 없음, 운영자 로그인 시 계정 줄에 링크)
