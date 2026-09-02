# inp2k.py — Abaqus INP → LS-DYNA K 변환기 (Python)

## 실행

```
python inp2k.py                          # GUI
python inp2k.py model.inp                # CLI, model.k 로 저장
python inp2k.py model.inp -o out.k --no-sets --tet10
```

필요한 것: Python 3.8+ / numpy(권장) / pandas(있으면 읽기 2배 빠름) / tkinter(GUI만).
numpy·pandas가 없어도 순수 파이썬 경로로 동작합니다.
Linux에서 GUI가 안 열리면 `sudo apt install python3-tk`.

## 브라우저판과 달라진 점

- `*INCLUDE`를 디스크에서 직접 찾습니다. 상대경로 → 덱 폴더 → 하위 폴더 순으로 탐색하므로
  파일을 따로 모아 올릴 필요가 없습니다.
- 출력을 파일로 흘려쓰기 때문에 결과 크기에 메모리를 쓰지 않습니다.
- 입력 파일 크기 제한이 없습니다.

## 성능 (429MB, 절점 450만, 요소 441만)

| | 시간 | 피크 메모리 |
|---|---|---|
| 브라우저(Web Worker) | 23.7 s | ~2.2 GB |
| Python + numpy/pandas | 18.6 s | 1.35 GB |

읽기 10.1초 / 변환 7.7초 / 쓰기 0.8초.

## 변환 범위

요소: C3D8·C3D6·C3D4·C3D10·C3D20 / S4·S3·S8 / B31·T3D2 / MASS / SPRING·CONN3D2
구조: 파트·어셈블리 인스턴스 평탄화(병진·회전, ID 충돌 시 자동 offset)
단면·재료: `*SOLID/SHELL/BEAM SECTION` → `*PART`+`*SECTION_*`,
`*ELASTIC` → `*MAT_ELASTIC`, `*PLASTIC` → `*MAT_024`+`*DEFINE_CURVE`
세트: `*SET_NODE_LIST` / `*SET_SOLID` / `*SET_SHELL_LIST` / `*SET_BEAM`
표면: 면 번호 S1~S6를 세그먼트로 전개 → `*SET_SEGMENT`
접촉: `*CONTACT PAIR`, `*TIE`, general contact
구속: `*MPC`, `*COUPLING`, `*EQUATION`, `*RIGID BODY` → `*CONSTRAINED_*`
경계: `*BOUNDARY` → `*BOUNDARY_SPC_SET`

하중과 스텝 정의는 변환하지 않고 로그에 미변환 키워드로 남깁니다.

## 확인해야 할 것

- 단위계를 옵션에서 맞춰 주세요. Abaqus 덱에는 단위 정보가 없습니다.
- 접촉 카드의 마찰 외 파라미터(SOFT, 관통검사, 접촉두께)는 기본값입니다.
- `*MPC PIN`과 kinematic coupling은 강체 구속으로 바뀌어 회전까지 묶입니다.
- 절점 좌표는 유효숫자 9자리 E 표기로 씁니다(최대 상대오차 5e-9).
