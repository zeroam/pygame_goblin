## PyGame Goblin

Source code from : https://github.com/techwithtim/Pygame-Tutorials/tree/master/Game

## Update Notes

### 2020/08/14
- bullet_sound, hit_sound 음원 파일 mp3 -> ogg 파일로 변경
- 고블린이 사라져도 고블린이 있던 자리를 공격하면 점수가 오르던 버그 수정
- 고블린, 플레이어의 공통 인터페이스 `Character` 구현
- 고블린 1마리에서 3마리까지 생성하도록 기능 구현
- 고블린 생성 시 랜덤으로 위치 및 가동범위 지정
- 고블린 사망 시 일정시간 후 랜덤한 위치에서 새로 추가
- 플레이어 사망 후 부활 시 일정시간 무적시간 추가

### 2020/08/17
- 게임 실행 클래스 `Game` 생성
  - widht, height 사이즈에 맞게 character 위치 조정
- 캐릭터 hit 시 랜덤으로 부활 위치 지정
- 코드 리팩토링 진행
  - 공통된 기능 함수로 묶음
  - 설정값 클래스 멤버 변수로 분리
  - 코드 분리 - game, character
- 설정 값 settings.py 로 분리
- 버그 수정
  - 총알이 나가다 빈 값을 삭제하려해 발생하는 에러 수정
- 타임 아웃 기능 추가