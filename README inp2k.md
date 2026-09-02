# abaqus-to-dyna

Abaqus 입력 파일(`.inp`)을 LS-DYNA 키워드 파일(`.k`)로 변환합니다.
같은 변환 규칙을 두 가지 형태로 제공합니다.

| | 파일 | 실행 |
|---|---|---|
| 데스크톱 (권장) | `inp2k.py` + bat 2개 | `run.bat` 더블클릭 |
| 브라우저 | `inp2k_converter.html` | 파일을 열기만 하면 됨 |

## 변환 범위

- **요소** C3D8·C3D6·C3D4·C3D10·C3D20 / S4·S3·S8 / B31·T3D2 / MASS / SPRING·CONN3D2
- **구조** 파트·어셈블리 인스턴스 평탄화 (병진·회전, ID 충돌 시 자동 offset)
- **단면·재료** `*SOLID/SHELL/BEAM SECTION` → `*PART`+`*SECTION_*`,
  `*ELASTIC` → `*MAT_ELASTIC`, `*PLASTIC` → `*MAT_024`+`*DEFINE_CURVE`
- **세트** `*SET_NODE_LIST` / `*SET_SOLID` / `*SET_SHELL_LIST` / `*SET_BEAM`
- **표면** Abaqus 면 번호 S1~S6를 세그먼트로 전개 → `*SET_SEGMENT`
- **접촉** `*CONTACT PAIR`, `*TIE`, general contact
- **구속** `*MPC`, `*COUPLING`, `*EQUATION`, `*RIGID BODY` → `*CONSTRAINED_*`
- **경계** `*BOUNDARY` → `*BOUNDARY_SPC_SET`

하중과 스텝 정의는 변환하지 않고 로그에 미변환 키워드로 남깁니다.

## 성능

429MB / 절점 450만 / 요소 441만 덱 기준

| | 시간 | 피크 메모리 |
|---|---|---|
| 브라우저 (Web Worker) | 23.7 s | 약 2.2 GB |
| Python + numpy/pandas | 18.6 s | 1.35 GB |

## 설치와 사용

자세한 내용은 [USAGE.md](USAGE.md) 참고.

```bash
python inp2k.py                  # GUI
python inp2k.py model.inp        # CLI → model.k
python inp2k.py --check          # 실행이 안 될 때 진단
```

필요한 것: Python 3.8+ / numpy·pandas(권장) / tkinter(GUI만)

## 확인해야 할 것

- Abaqus 덱에는 단위 정보가 없습니다. 옵션에서 단위계를 맞춰 주세요.
- 접촉 카드의 마찰 외 파라미터(SOFT, 관통검사, 접촉두께)는 기본값입니다.
- `*MPC PIN`과 kinematic coupling은 강체 구속으로 바뀌어 회전까지 묶입니다.
- 변환 후 LS-PrePost에서 형상·PID·재료를 눈으로 확인하세요.
