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
