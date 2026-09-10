#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abaqus INP -> LS-DYNA keyword (.k) 변환기

현재 버전: v2.10 — 방향 적용 그래프 / DEATH=0 / 전체 점 수
- 그래프와 속도 요약에 SFO를 적용하여 실제 가진 방향을 표시합니다.
- Shock Motion의 DEATH를 0.0으로 출력합니다.
- 입력 N은 전체 표 점 수입니다. 중앙 구간 N-2점 + 바깥 끝점 2개.

이전 버전: v2.9 — 중앙 구간 점 수 / 출력 폴더 / 6방향 일괄 저장
- 점 수는 T~2T 양 끝점 포함. 전후 선형 구간에는 추가 점 없이 0, 3T만 출력.
- 출력 폴더 입력/선택 후 출력 실행. 선택 방향 또는 6방향 일괄 저장 지원.
- 음수 방향 파일명 접두어/LCID=701, 양수 방향=702 (Motion 참조도 연동).

이전 버전: v2.8 — Dark UI / 점 수 / 소수점 표기 / 보상 Shock
- 검은색 커스텀 탭과 스크롤바, 전체 데이터점 개수 입력 추가.
- Shock 표: 시간 소수 5자리(s), 속도 소수 2자리(mm/s).
- 0~T 선형 0→-V, T~2T 가속도 적분 -V→+V, 2T~3T 선형 +V→0.
  V는 선택 파형의 속도 증분 절반. 표에 SFO를 곱해 실제 방향을 적용.
- Shock 파일 상단 생성기 주석 삭제. 기존 INP 변환 로직 유지.

이전 버전: v2.7 — Shock input 생성 탭 추가
- v2.6 변환 로직을 유지하고 별도 Shock 탭을 추가했습니다. INP 없이 사용 가능.
- 가속도(g), 펄스 시간(ms), 파형(Half-sine / Triangular / Rectangular),
  방향(±X/±Y/±Z)을 선택하면 속도 경계조건 include 파일을 생성합니다.
- 시간은 s, 속도는 mm/s. 초기속도 0에서 가속도를 해석적으로 적분하고,
  펄스 종료 뒤 최종 속도를 3T까지 유지합니다. 표는 601점(T당 200구간).
- NSID=100001, LCID=701, VAD=0, Motion SF=1.0. 방향 부호는 Curve SFO.
- CLI 예: python inp2k.py --shock --shock-g 25 --shock-ms 15 --shock-direction mx

이전 버전: v2.6 (by claude)
최신 수정사항 — 마운팅 판정에서 경계조건 조건 제거 / 체크박스 문구 축약 / 전체 접촉 별도 계수
- 마운팅: 노드 1개짜리 NSET이 *COUPLING 또는 *MPC의 기준절점이면 *BOUNDARY 유무와
  관계없이 마운팅으로 봅니다. 해당 COUPLING/MPC는 변환하지 않고 기준절점을 삭제하며,
  종속 절점으로 NSET_BC (SID 100001)를 만듭니다. BC가 있으면 NSET_BC로 옮기고,
  없으면 SET만 출력합니다. 후보가 여러 개이면 이름에 MOUNT가 들어간 SET만 쓰고,
  그런 SET이 없으면 모든 후보를 NSET_BC 하나로 묶고 경고합니다.
- 상세 설정의 PAD/TA/ADHESIVE 체크박스를 한 줄로 줄이고 부가 설명을 없앴습니다.
- 상세 설정에 "전체 접촉" 페이지를 추가해 ELSET_ALL 전체 접촉(ELSET_ALL_CONTACT,
  자동 SET OFF 시 GENERAL_CONTACT)의 FS/FD/VDC/SST/MST/SOFT/SBOPT/DEPTH/BSORT를
  따로 지정합니다. 공란이면 "개별 접촉" 값 → 기존 값 순서로 따릅니다.
  JSON 키: all_contact_fs 등 (schema_version 1 유지, 이전 JSON도 그대로 불러옴).

이전 버전: v2.5 (by claude)
최신 수정사항 — 상세 설정 창 크기 / SST·MST 음수 / PAD·TA·ADHESIVE ELFORM -1 / 마운팅 노드 → NSET_BC
- 상세 설정 창을 키우고, 내용의 실제 요구 크기에 맞춰 창 크기를 정합니다
  (화면보다 크면 화면 안으로 제한). 하단 버튼이 잘리지 않습니다.
- 접촉 SST/MST에 음수를 입력할 수 있습니다(LS-DYNA: 음수는 두께 절댓값으로 사용).
- Formulation 페이지에 "PAD / TA / ADHESIVE 이름 → Solid ELFORM -1" 체크박스를 추가.
  켜면 PART 이름(인스턴스_ELSET)에 PAD, TA, ADHESIVE(복수형 S 포함)가 단어로
  들어간 솔리드 프로퍼티를 ELFORM -1로 둡니다. 영문자와 붙은 경우(METAL, DATA,
  PADDING 등)는 제외하고 _, -, 공백, 숫자 경계만 인정합니다. 육면체 전용
  프로퍼티에만 적용하며 전역 Solid ELFORM 지정보다 우선합니다. JSON 키:
  neg_elform_names (true/false), 기본 OFF. CLI: --neg-elform-names
- 마운팅 노드 처리: 노드 1개짜리 NSET의 노드가 *COUPLING 기준절점 또는 *MPC
  기준절점이고 *BOUNDARY로 고정되어 있으면(보통 SET_NODES_MOUNTING),
  해당 COUPLING/MPC를 변환하지 않고 기준절점을 *NODE에서 삭제합니다.
  그 커플링/MPC에 속했던 노드는 *SET_NODE_LIST_TITLE NSET_BC (SID 100001)로 묶고,
  원래 1노드 SET에 걸린 *BOUNDARY는 NSET_BC의 *BOUNDARY_SPC_SET으로 옮깁니다.
  1노드 SET 자체는 출력하지 않습니다. 기준절점이 요소·*EQUATION·*RIGID BODY에서
  쓰이면 삭제하지 않고 경고 후 기존 변환을 유지합니다.
- 고정 ID(fixed_sid) SET의 번호는 일반 SET 순번 배정에서 자동으로 예약합니다.

이전 버전: v2.4
최신 수정사항 — 상세 설정 GUI 스타일 통일 / 메인 옵션 2×2 정렬
- 상세 설정에 메인 GUI의 다크 팔레트·글꼴·카드·버튼·입력 스타일을 적용합니다.
- 4개 페이지를 상단 버튼으로 전환하며, JSON 저장/불러오기와 적용/취소는 하단 고정.
- 메인 옵션 4개를 동일 너비의 2열 × 2행으로 배치합니다.
- 변환 규칙과 설정 JSON 형식은 v2.3과 동일합니다.

이전 버전: v2.3
최신 수정사항 — GUI 간소화 / 전체 접촉 종류 선택 / 상세 설정·JSON 프리셋
- GUI에서는 2차 사면체 유지·보 방향절점·자동 끝단 SET을 항상 ON,
  단위계는 mm·ton·s로 고정합니다(입력 수치 자동 환산 아님).
- ELSET_ALL(900001)을 참조하는 선택한 AUTOMATIC_SINGLE_SURFACE_ID 또는
  ERODING_SINGLE_SURFACE_ID 접촉을 추가합니다.
- 상세 설정: shell ELFORM(auto/2/16), solid ELFORM(auto/1/2), 접촉 FS/FD/VDC/
  SST/MST/SOFT/SBOPT/DEPTH/BSORT, shell/solid별 IHQ/QM/IBQ/Q1/Q2/QB/QW.
- 솔리드 지정은 육면체 전용 프로퍼티에 적용하며, 혼합·축약 요소는 기존
  호환 공식을 유지합니다. 순수 C3D10의 ELFORM=16 유지 규칙도 보존합니다.
- 접촉 공란은 기존 값을 유지합니다. SOFT/SBOPT/DEPTH/BSORT는 비-TIE 접촉에
  적용하고, TIE의 기존 공란 필드는 유지합니다. 상세 설정 창에서 JSON 저장/불러오기를 지원합니다.

이전 버전: v2.2
최신 수정사항 — 중앙 하부 PART 자동 탐색 / 평면 각도 배열 계산 / 완료 버튼
- 전체 구조 메시 XY 경계상자 중심의 수직선과 만나는 가장 낮은 면의 PART를
  자동 선택하여 RIGID_Z를 생성합니다. 이름/PID 입력은 필요하지 않습니다.
- 선택한 PART의 XY 평면 10도 이내 아랫면, 전체 모델의 XZ 평면 10도 이내
  +Y 끝단면을 사용합니다. 중심선이 빈 곳을 지나면 RIGID_Z를 생략하고 경고합니다.
- NumPy 사용 시 5만 요소씩 면을 추출하고 2만 면씩 평면 각도를 배열 계산하며
  외곽면 결과를 재사용합니다. 평면 각도와 기존 축-법선 각도 조건은 동등합니다.
- 변환 성공 후 활성화되는 완료 버튼을 누르면 창이 닫힙니다.

v2.1 변경 이력:
최신 수정사항 — 혼합 SET 통합 및 SEGMENT 명명/순서 정리
- Solid와 Shell이 함께 있는 ELSET은 원래 이름의 SET_PART_LIST 하나로 출력합니다.
  참조 PART의 모든 요소가 포함되므로, 부분 요소 SET의 범위가 확대되면 경고합니다.
- SEGMENT SET 이름에 _seg를 붙입니다. 이름 충돌 시 _2_seg 등의 번호를 붙입니다.
- 일반 원본 SET -> SEGMENT SET -> NODE SURFACE/SURF_COUPLING -> 추가 구속 SET
  순서로 배치하고 참조 ID를 함께 갱신합니다. 자동 SET의 고정 ID는 유지합니다.
- TYPE=NODE 면 탐색 생략 등 v2.0의 동작은 유지합니다.

v2.0 변경 이력:
최신 수정사항 — NODE SURFACE의 불필요한 면 탐색 제거
- TYPE=NODE SURFACE는 노드 목록을 그대로 SET_NODE_LIST로 보존합니다.
  SURF_COUPLING 등 커플링용 표면을 SEGMENT로 역추정하지 않습니다.
- NODE SURFACE가 있다는 이유로 전체 요소의 연결 정보를 수집하지 않습니다.
- KINEMATIC 커플링은 기존처럼 참여 노드와 기준 노드를 CNRB에 전달합니다.
  기존 구속 변환의 자유도 처리 규칙을 새로 변경하지는 않습니다.
- TYPE=ELEMENT SURFACE의 SEGMENT 변환, SET 순서, ID 중복 방지,
  자동 끝단 SET 옵션과 진단 로그 기능은 유지합니다.
- 자동 끝단 SET을 켠 경우 그 기능에 필요한 형상 탐색은 별도로 실행됩니다.

v1.9 변경 이력:
최신 수정사항 — 자동 끝단 SET OFF 상태의 75% 지연 대응
- ELSET 분류 시 전체 요소를 복사/정렬하던 v1.8 전역 색인 생성을 제거하고,
  이미 만들어진 인스턴스별 검색 정보를 재사용합니다.
- NODE SURFACE의 전체 외곽면 사전 생성을 제거하고, NumPy 경로에서는
  5만 요소씩 선택 노드에 닿는 후보를 검사합니다. 동일한 최근 선택은 재사용합니다.
- GUI 진행 통지를 제한하고 이벤트 처리를 시간/개수 단위로 나눠
  진행 메시지가 많아도 화면이 다시 그려질 수 있도록 합니다.
- SET/SURFACE 처리 이름과 경과 시간을 로그에 남기며,
  출력 경로 + .conversion.log 파일에 실행 기록과 오류를 실시간으로 추가합니다.
- 기존 SET 구성원/순서 및 자동 끝단 SET ON/OFF 동작을 유지합니다.
  실제 사용자 INP에서의 지연 원인은 미확정이며 진단 기록으로 추적할 수 있습니다.

v1.8 변경 이력 — 기존 SET/SURFACE 변환(75% 구간) 최적화
- NODE SURFACE: 전체 요소의 면을 세트마다 다시 검사하지 않고,
  공통 외곽면 색인을 한 번 생성한 뒤 재사용합니다.
- ELSET: 모든 인스턴스를 매번 순회하는 대신 전역 요소 종류 색인으로
  Solid/Shell/Beam을 분류합니다. 구성원과 출력 순서는 유지합니다.
- 기존 NODE/SEGMENT SET의 ID 조회와 인스턴스 접두어 목록을 재사용해
  반복 검색 비용을 줄였습니다.
- 현재 처리 중인 SET/SURFACE 이름, 처리 개수 및 긴 SURFACE의 행 진행을
  표시하고, 후처리 진행률이 뒤로 내려가지 않도록 했습니다.
- 기존 변환 규칙, SET 순서, 자동 SET의 고정 ID와 10도 선택 조건은 유지합니다.
- 검증: 회귀 테스트 63개 통과. 합성 모델의 2만 요소/100 NODE SURFACE
  조회에서 v1.7 10.65초 -> v1.8 0.35초, 선택된 면과 순서 일치.
  위 시간은 해당 조회 예제 기준이며 실제 모델 전체의 성능을 보장하지 않습니다.

GUI:  python inp2k.py
CLI:  python inp2k.py model.inp -o model.k --no-sets

numpy가 있으면 절점/요소 블록을 통째로 벡터 처리한다(수 배 빠름).
없으면 순수 파이썬 경로로 동작한다.

v1.1 (based on soranne2/Abaqus-to-dyna, b00caa28):
- Repeated ELSET chunks and part/instance/assembly section references resolve
  before PID assignment; missing INCLUDE files are explicit errors.
- HYPERFOAM -> MAT_LOW_DENSITY_FOAM (57): E=1, TC=0.55; UNIAXIAL TEST DATA
  supplies a compression nominal strain/stress DEFINE_CURVE linked by LCID.
  Coefficients alone or non-uniaxial tables cannot supply this curve.
- NSET, ELSET and SURFACE cards follow first appearance after INCLUDE expansion.
  Repeated definitions merge at their first position. Per-part sets/surfaces
  expand in instance order. Member order is preserved; derived constraint sets
  follow source sets. SET IDs are newly allocated in this order.
- Every mesh surface is exported, even without a contact. NODE surfaces only
  yield segments where all corner nodes of an exterior mesh face are present.
  Unsupported analytical/edge surfaces are reported, never replaced by S1.

v1.2:
- *ELEMENT, ELSET=... groups remain internal to property/surface resolution.
  They do not create extra output SET cards. Explicit *ELSET declarations are
  still exported at their first explicit declaration, including reused names.
- Source SURFACEs remain independent SETs in source order, reused by contacts.
  A NODE surface produces one segment set when mesh faces can be identified;
  any node set needed by a contact is appended after the source sets.
- TIED contact DC, VC, BT, DT, SFS, SFM, SFST, SFMT, FSF, VSF fields are blank.
- CONTROL and DATABASE templates are never emitted. Legacy ctrl arguments are
  accepted for compatibility only; there is no GUI control-generation option.

v1.3:
- Add per-PART *HOURGLASS / HGID for applicable shell/solid formulations.
  Defaults are initial settings for quasi-static / low-velocity structural
  simulations, not calibration against a solver run. No CONTROL is generated.
- Final SET order: explicit NSET/ELSET (source order), source SURFACE sets
  (source order), derived contact/constraint sets. Reassign SIDs and update
  all contact/SPC/NRB references after ordering. Member order is unchanged.

v1.4:
- One PART/SECTION per source property and instance, regardless of mesh shape.
  Mixed solid shapes use ELFORM 1; mixed shell shapes use one quad-compatible
  formulation. Original material, thickness and SET ordering are retained.
- Exactly two shared hourglass definitions: HGID 1 for shells, HGID 2 for solids.
  All shell/solid PARTs reference these, including fully integrated elements.
- Support C3D5 pyramids, repeat apex IDs in all eight solid node slots, correct
  tetrahedral degeneration, and check solid node references before writing.
- Use one installed Korean-capable sans-serif family throughout the GUI.

v1.5:
- Allocate CNRB PIDs after all output entities are known, starting above every
  emitted node/element/PART/SECTION/MAT/curve/SET/HG/contact/constraint ID.
  Recheck at write time; retain PART IDs, node-set links and source SET order.

v1.6:
- Append ELSET_ALL (900001, PART list), RIGID_Y (200001) and RIGID_Z
  (200002, NODE lists). These names/IDs are reserved when auto_sets is enabled.
- Global-coordinate exterior faces within 10 degrees are grown across shared
  edges from the global directional extreme. Shell faces are two-sided.
  Disconnected recessed surfaces are excluded. No BC/CNRB is added.
- No qualifying end face: warn and omit that NODE set, never write an empty one.

v1.7:
- Compact numeric face sorting removes internal faces before geometry work.
- Automatic-set geometry is separate from contact lookup data, so auto sets
  do not expand every existing surface/constraint search to the whole model.
- Visible post-mesh phases, periodic elapsed-time heartbeat, and GUI/CLI
  auto-set switch. Selection semantics, reserved IDs and original sets retained.
"""

import os
import re
import sys
import json
import math
import time
import shutil
import tempfile
import threading
import queue
import argparse

try:
    import numpy as np
    HAVE_NUMPY = True
except Exception:                                    # pragma: no cover
    np = None
    HAVE_NUMPY = False

try:                                                 # 있으면 C 파서를 쓴다(2배 빠름)
    import io as _io
    import pandas as pd
    HAVE_PANDAS = True
except Exception:                                    # pragma: no cover
    pd = None
    HAVE_PANDAS = False

# v1.8: index NODE SURFACEs and global ELSET categories; retain source order.
VERSION = "2.10"

# User-requested defaults. Values use the input deck's stress unit.
FOAM_DEFAULT_E = 1.0
FOAM_DEFAULT_TC = 0.55

# Shared initial hourglass settings: (IHQ, QM, QB/VDC, QW).
# None leaves the corresponding fixed-width field blank (solver default).
# Sources: https://lsdyna.ansys.com/hourglass/
# https://lsdyna.ansys.com/negative-volumes-in-brick-elements/
# Card layout: Ansys PyDYNA auto/hourglass/hourglass.py.
HOURGLASS_DEFAULTS = {
    "shell": (4, 0.03, 0.03, 0.03),
    "solid": (6, 0.10, None, None),
}
# IHQ 8 is specific to shell ELFORM 16. With one shared shell card, use IHQ 4
# for reduced-integration shells; fully integrated shells do not need it.
# HGID assignment does not force an inactive hourglass mode to become active.


# v2.5: PAD / TA / ADHESIVE property names -> solid ELFORM -1 (opt-in).
# A keyword must not touch another letter: THERMAL_PAD, TA-01, CELL TA2 match;
# METAL, DATA, PADDING do not. An optional plural S is accepted.
NEG_ELFORM_NAME_RE = re.compile(r"(?<![A-Z])(?:PAD|TA|ADHESIVE)S?(?![A-Z])")

# v2.5: nodes of a coupling/MPC whose reference node is a lone mounting node.
MOUNT_SET_ID = 100001
MOUNT_SET_NAME = "NSET_BC"


def neg_elform_name(title):
    return bool(NEG_ELFORM_NAME_RE.search(str(title or "").upper()))


def name_key(value):
    return str(value or "").strip().strip("\"'").upper()


def abaqus_float(value):
    return float(str(value).replace("D", "E").replace("d", "e"))


def ordered_unique(values):
    """Keep the first occurrence; never numerically sort an input set."""
    return list(dict.fromkeys(values))

# ============================================================
# 단위계 기본값 (재료 정보가 없을 때 채워 넣는 값)
# ============================================================
UNIT_DEFAULT = {
    "mmts":   dict(rho=7.85e-9, e=210000.0, nu=0.3, end=0.02, label="mm-ton-s-N"),
    "mkgs":   dict(rho=7850.0,  e=2.1e11,   nu=0.3, end=0.02, label="m-kg-s-N"),
    "mmkgms": dict(rho=7.85e-6, e=210.0,    nu=0.3, end=20.0, label="mm-kg-ms-kN"),
}

# ============================================================
# 요소 타입 분류
# ============================================================
_CLS_CACHE = {}


def classify(t):
    """Abaqus 요소 타입 -> dict(cat, sub, nn, red, truss) 또는 None"""
    if t in _CLS_CACHE:
        return _CLS_CACHE[t]
    u = (t or "").upper()
    r = None
    if u.startswith(("C3D20", "C3D27")):
        r = dict(cat="solid", sub="hex20", nn=20)
    elif u.startswith("C3D15"):
        r = dict(cat="solid", sub="wedge15", nn=15)
    elif u.startswith("C3D10"):
        r = dict(cat="solid", sub="tet10", nn=10)
    elif u.startswith(("C3D8", "SC8", "COH3D8", "DC3D8")):
        r = dict(cat="solid", sub="hex8", nn=8, red="8R" in u)
    elif u.startswith(("C3D6", "SC6", "COH3D6", "DC3D6")):
        r = dict(cat="solid", sub="wedge6", nn=6)
    elif u.startswith(("C3D5", "DC3D5")):
        r = dict(cat="solid", sub="pyramid5", nn=5)
    elif u.startswith(("C3D4", "DC3D4")):
        r = dict(cat="solid", sub="tet4", nn=4)
    elif u.startswith(("S8", "S9")):
        r = dict(cat="shell", sub="quad8", nn=8)
    elif u.startswith(("S6", "STRI65")):
        r = dict(cat="shell", sub="tri6", nn=6)
    elif u.startswith(("S4", "M3D4", "SFM3D4", "R3D4", "CPS4", "CPE4")):
        r = dict(cat="shell", sub="quad4", nn=4, red="4R" in u)
    elif u.startswith(("S3", "STRI3", "M3D3", "SFM3D3", "R3D3", "CPS3", "CPE3")):
        r = dict(cat="shell", sub="tri3", nn=3)
    elif u.startswith(("T3D2", "T2D2")):
        r = dict(cat="beam", sub="truss2", nn=2, truss=True)
    elif u.startswith("T3D3"):
        r = dict(cat="beam", sub="truss3", nn=3, truss=True)
    elif u.startswith(("B31", "B33", "B21", "B23")):
        r = dict(cat="beam", sub="beam2", nn=2)
    elif u.startswith(("B32", "B22")):
        r = dict(cat="beam", sub="beam3", nn=3)
    elif u == "MASS":
        r = dict(cat="mass", sub="mass", nn=1)
    elif u.startswith("ROTARYI"):
        r = dict(cat="inertia", sub="inertia", nn=1)
    elif u.startswith(("SPRING", "DASHPOT", "CONN3D2", "CONN2D2")):
        r = dict(cat="discrete", sub="discrete", nn=2)
    if r is not None:
        r.setdefault("red", False)
        r.setdefault("truss", False)
    _CLS_CACHE[t] = r
    return r


DYNA_KEYWORD = {
    "hex8": "*ELEMENT_SOLID (8절점)",
    "wedge6": "*ELEMENT_SOLID (축약 6면체)",
    "pyramid5": "*ELEMENT_SOLID (5절점 피라미드)",
    "tet4": "*ELEMENT_SOLID (축약 4면체)",
    "tet10": "*ELEMENT_SOLID (10절점 또는 코너 4절점)",
    "hex20": "*ELEMENT_SOLID (코너 8절점만)",
    "wedge15": "*ELEMENT_SOLID (코너 6절점만)",
    "quad4": "*ELEMENT_SHELL",
    "tri3": "*ELEMENT_SHELL (축약 삼각형)",
    "quad8": "*ELEMENT_SHELL (코너 4절점만)",
    "tri6": "*ELEMENT_SHELL (코너 3절점만)",
    "beam2": "*ELEMENT_BEAM",
    "beam3": "*ELEMENT_BEAM (2절점 축약)",
    "truss2": "*ELEMENT_BEAM (ELFORM 3)",
    "truss3": "*ELEMENT_BEAM (ELFORM 3)",
    "mass": "*ELEMENT_MASS",
    "discrete": "*ELEMENT_DISCRETE",
}

# Abaqus 면 번호 -> 로컬 절점 인덱스 (외향 법선)
FACE = {
    "hex8":   {"S1": (0, 1, 2, 3), "S2": (4, 7, 6, 5), "S3": (0, 4, 5, 1),
               "S4": (1, 5, 6, 2), "S5": (2, 6, 7, 3), "S6": (3, 7, 4, 0)},
    "wedge6": {"S1": (0, 1, 2), "S2": (3, 5, 4), "S3": (0, 1, 4, 3),
               "S4": (1, 2, 5, 4), "S5": (2, 0, 3, 5)},
    "tet4":   {"S1": (0, 1, 2), "S2": (0, 3, 1), "S3": (1, 3, 2), "S4": (2, 3, 0)},
}
FACE["hex20"] = FACE["hex8"]
FACE["tet10"] = FACE["tet4"]
FACE["wedge15"] = FACE["wedge6"]
# Abaqus C3D5 S1..S5 labels, with outward normals for positive volume.
FACE["pyramid5"] = {"S1": (0, 3, 2, 1), "S2": (0, 1, 4),
                    "S3": (1, 2, 4), "S4": (2, 3, 4), "S5": (3, 0, 4)}

# Segment connectivity uses outward normals for standard positive-volume
# Abaqus solid connectivity. Face labels themselves are unchanged.
FACE["hex8"].update(S1=(0, 3, 2, 1), S2=(4, 5, 6, 7), S3=(0, 1, 5, 4),
                    S4=(1, 2, 6, 5), S5=(2, 3, 7, 6), S6=(3, 0, 4, 7))
FACE["wedge6"].update(S1=(0, 2, 1), S2=(3, 4, 5))
FACE["tet4"].update(S1=(0, 2, 1), S2=(0, 1, 3), S3=(1, 2, 3), S4=(2, 0, 3))

UNSUPPORTED_QUIET = {
    "STEP", "END STEP", "DYNAMIC", "STATIC", "OUTPUT", "NODE OUTPUT",
    "ELEMENT OUTPUT", "RESTART", "PREPRINT", "SYSTEM", "ASSEMBLY",
    "END ASSEMBLY", "END PART", "END INSTANCE", "CONTACT OUTPUT",
    "ENERGY OUTPUT", "BULK VISCOSITY", "END LOAD CASE",
}

SECTION_KW = {"SOLID SECTION", "SHELL SECTION", "MEMBRANE SECTION",
              "BEAM SECTION", "BEAM GENERAL SECTION", "COHESIVE SECTION",
              "SHELL GENERAL SECTION", "TRUSS SECTION"}


# ============================================================
# 숫자 포맷
# ============================================================
def fnum(v, w):
    """폭 w의 고정 필드에 들어가는 실수 표기"""
    try:
        v = float(v)
    except (TypeError, ValueError):
        v = 0.0
    if v == 0.0:
        s = "0.0"
    else:
        a = abs(v)
        if 1e-3 <= a < 1e6:
            s = repr(round(v, max(1, w - 4)))
            if s.endswith(".0") and len(s) > w:
                s = s[:-2]
        else:
            s = ("%.*E" % (max(2, w - 9), v))
    if len(s) > w:
        s = "%.4E" % v
    if len(s) > w:
        s = "%.2E" % v
    return s[:w].rjust(w)


def f10(v):
    return fnum(v, 10)


def f16(v):
    return fnum(v, 16)


def f20(v):
    return fnum(v, 20)


def i8(v):
    return str(int(v)).rjust(8)


def i10(v):
    return str(int(v)).rjust(10)


# ---------- numpy 벡터 포맷 ----------
if HAVE_NUMPY:
    def np_int_cols(arr, w):
        """정수 배열 -> (N, w) uint8 (오른쪽 정렬)"""
        n = arr.shape[0]
        out = np.full((n, w), 32, np.uint8)
        v = np.abs(arr).astype(np.int64)
        neg = arr < 0
        p = 1
        for k in range(w):
            col = w - 1 - k
            d = (v // p) % 10
            if k == 0:
                out[:, col] = 48 + d
            else:
                mask = v >= p
                np.copyto(out[:, col], (48 + d).astype(np.uint8), where=mask)
            p *= 10
        if neg.any():                      # 음수 ID는 사실상 없지만 안전하게
            for r in np.nonzero(neg)[0]:
                out[r] = np.frombuffer(str(int(arr[r])).rjust(w).encode(), np.uint8)
        return out

    def np_f16_cols(arr):
        """실수 배열 -> (N,16) uint8, `-d.dddddddd E+ee` 고정 폭"""
        a = np.asarray(arr, dtype=np.float64)
        n = a.shape[0]
        out = np.full((n, 16), 32, np.uint8)
        neg = a < 0
        v = np.abs(a)
        zero = ~np.isfinite(v) | (v == 0)
        vv = np.where(zero, 1.0, v)
        exp = np.floor(np.log10(vv)).astype(np.int64)
        mant = vv / np.power(10.0, exp.astype(np.float64))
        dig = np.rint(mant * 1e8).astype(np.int64)
        over = dig >= 1000000000
        dig = np.where(over, dig // 10, dig)
        exp = np.where(over, exp + 1, exp)
        under = dig < 100000000
        dig = np.where(under, dig * 10, dig)
        exp = np.where(under, exp - 1, exp)
        dig = np.where(zero, 0, dig)
        exp = np.where(zero, 0, exp)
        big = np.abs(exp) > 99
        exp = np.where(big, 0, exp)
        dig = np.where(big, 0, dig)

        out[:, 1] = np.where(neg & ~zero, 45, 32)
        out[:, 2] = 48 + (dig // 100000000)
        out[:, 3] = 46
        r = dig % 100000000
        for k in range(8):
            out[:, 11 - k] = 48 + (r % 10)
            r = r // 10
        out[:, 12] = 69
        ae = np.abs(exp)
        out[:, 13] = np.where(exp < 0, 45, 43)
        out[:, 14] = 48 + (ae // 10)
        out[:, 15] = 48 + (ae % 10)
        if big.any():                      # 지수가 100 이상인 희귀 값은 파이썬 포맷으로
            for r_ in np.nonzero(big)[0]:
                out[r_] = np.frombuffer(f16(a[r_]).encode(), np.uint8)
        return out

    def np_rows_to_bytes(cols):
        """열 블록 리스트 -> 개행 붙인 bytes"""
        n = cols[0].shape[0]
        total = sum(c.shape[1] for c in cols)
        buf = np.empty((n, total + 1), np.uint8)
        o = 0
        for c in cols:
            buf[:, o:o + c.shape[1]] = c
            o += c.shape[1]
        buf[:, total] = 10
        return buf.tobytes()


# ============================================================
# 로그
# ============================================================
class Log:
    def __init__(self, sink=None):
        self.items = []
        self.sink = sink

    def _add(self, lv, m):
        self.items.append((lv, m))
        if self.sink:
            self.sink(lv, m)

    def info(self, m): self._add("info", m)
    def ok(self, m):   self._add("ok", m)
    def warn(self, m): self._add("warn", m)
    def err(self, m):  self._add("err", m)

    @property
    def n_warn(self): return sum(1 for lv, _ in self.items if lv == "warn")

    @property
    def n_err(self): return sum(1 for lv, _ in self.items if lv == "err")


# ============================================================
# 파일 스캐너 — 키워드 줄 위치만 찾고 데이터는 블록째 넘긴다
# ============================================================
CHUNK = 32 * 1024 * 1024


def scan_file(path):
    """('kw', str) / ('data', bytes) 이벤트를 순서대로 yield.
    데이터 블록은 바이트 그대로 넘겨 디코딩 비용을 없앤다."""
    carry = b""
    pending_kw = None
    with open(path, "rb") as fh:
        while True:
            raw = fh.read(CHUNK)
            if not raw:
                break
            if carry:
                raw = carry + raw
            cut = raw.rfind(b"\n")
            if cut < 0:
                carry = raw
                continue
            carry = raw[cut + 1:]
            for kind, payload in _scan_bytes(raw[:cut + 1]):
                if pending_kw is not None:
                    if kind == "kw" and payload.startswith("**"):
                        continue
                    if kind == "data":
                        while pending_kw.rstrip().endswith(",") and payload:
                            first, sep, rest = payload.partition(b"\n")
                            s = first.decode("latin-1").strip()
                            # Keyword continuations contain parameters, not the
                            # first numeric data row after a trailing comma.
                            if not re.match(r"^[A-Za-z][A-Za-z0-9 _-]*(?:\s*=|\s*,|\s*$)", s):
                                break
                            pending_kw += s
                            payload = rest if sep else b""
                        if not payload and pending_kw.rstrip().endswith(","):
                            continue
                    yield ("kw", pending_kw)
                    pending_kw = None
                if kind == "kw" and not payload.startswith("**") and payload.rstrip().endswith(","):
                    pending_kw = payload
                elif payload:
                    yield kind, payload
    if carry.strip():
        for kind, payload in _scan_bytes(carry + b"\n"):
            if pending_kw is not None:
                if kind == "data" and re.match(rb"^[ \t]*[A-Za-z][A-Za-z0-9 _-]*=", payload):
                    pending_kw += payload.decode("latin-1").strip()
                    payload = b""
                yield "kw", pending_kw
                pending_kw = None
            if payload:
                yield kind, payload
    if pending_kw is not None:
        yield "kw", pending_kw


def _scan_bytes(buf):
    pos = 0
    # Abaqus accepts leading whitespace before keyword lines.
    for match in re.finditer(rb"(?m)^[ \t]*\*[^\n]*(?:\n|$)", buf):
        if match.start() > pos:
            yield "data", buf[pos:match.start()]
        yield "kw", match.group().decode("latin-1").strip()
        pos = match.end()
    if pos < len(buf):
        yield "data", buf[pos:]


def parse_keyword(line):
    parts = line.split(",")
    kw = re.sub(r"\s+", " ", parts[0][1:].strip().upper())
    params = {}
    for p in parts[1:]:
        if not p.strip():
            continue
        if "=" in p:
            k, v = p.split("=", 1)
            params[re.sub(r"\s+", " ", k.strip().upper())] = v.strip().strip("\"'")
        else:
            params[re.sub(r"\s+", " ", p.strip().upper())] = True
    return kw, params


# ============================================================
# 수치 블록 파싱
# ============================================================
_TBL = {ord(" "): None, ord("\t"): None, ord("\r"): None,
        ord("D"): "E", ord("d"): "e"}


def piece_to_flat(b, hint=0):
    """데이터 조각(bytes) -> (1차원 값 배열, 열 수). 열 수 0이면 미상."""
    if not b or not b.strip():
        return None, 0
    if HAVE_PANDAS:
        try:
            a = pd.read_csv(_io.BytesIO(b), header=None, dtype=np.float64,
                            engine="c", skip_blank_lines=True).to_numpy()
            if a.size:
                keep = ~np.isnan(a).all(axis=0)
                a = a[:, keep]
                if a.size and not np.isnan(a).any():
                    return a.ravel(), a.shape[1]
        except Exception:
            pass
    # 정리 후 numpy / 파이썬 파싱
    c = b.decode("latin-1").translate(_TBL)
    c = c.replace(",\n", "\n").replace("\n", ",")
    while ",," in c:
        c = c.replace(",,", ",")
    c = c.strip(",")
    if not c:
        return None, 0
    if HAVE_NUMPY:
        try:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                arr = np.fromstring(c, dtype=np.float64, sep=",")
            if arr.size and arr.size == c.count(",") + 1:
                return arr, 0
        except Exception:
            pass
        return None, 0
    try:
        return [float(x) for x in c.split(",")], 0
    except ValueError:
        return None, 0


def bytes_first_width(b):
    head = b[:400].split(b"\n")
    for line in head:
        line = line.strip().rstrip(b",")
        if line:
            return line.count(b",") + 1
    return 0


# ============================================================
# 모델 자료구조
# ============================================================
class Part:
    __slots__ = ("name", "nblocks", "eblocks", "nsets", "elsets",
                 "sections", "massvals")

    def __init__(self, name):
        self.name = name
        self.nblocks = []          # [(ids, xyz)]  xyz: (N,3)
        self.eblocks = []          # [dict(type, ids, conn)]
        self.nsets = {}
        self.elsets = {}
        self.sections = []
        self.massvals = {}

    def empty(self):
        return not (self.nblocks or self.eblocks or self.nsets
                    or self.elsets or self.sections)

    def n_nodes(self):
        return sum(len(b[0]) for b in self.nblocks)

    def n_elems(self):
        return sum(len(b["ids"]) for b in self.eblocks)


class Model:
    def __init__(self):
        self.title = ""
        self.parts = {}
        self.instances = []
        self.materials = {}
        self.asm_nsets = []
        self.asm_elsets = []
        self.boundaries = []
        self.unsupported = {}
        self.surfaces = []
        self.interactions = {}
        self.contact_pairs = []
        self.ties = []
        self.mpcs = []
        self.couplings = []
        self.equations = []
        self.rigid_bodies = []
        self.general_contact = False
        self.el_types = set()
        self.set_defs = []  # Interleaved NSET/ELSET/SURFACE source order.


# ============================================================
# 파서
# ============================================================
class Parser:
    def __init__(self, log, progress=None):
        self.log = log
        self.progress = progress
        self.m = Model()
        self.root = Part("__ROOT__")
        self.m.parts["__ROOT__"] = self.root
        self.cur_part = self.root
        self.cur_inst = None
        self.mode = None
        self.pieces = []
        self.el_type = ""
        self.set_arr = None
        self.set_gen = False
        self.cur_mat = None
        self.cur_section = None
        self.bc_type = None
        self.mass_elset = None
        self.cur_surf = None
        self.cur_inter = None
        self.cur_cp = None
        self.cur_tie = None
        self.cur_coup = None
        self.cur_eq = None
        self.eq_need = 0
        self.heading_done = False
        self.n_lines = 0
        self.n_bytes = 0
        self.pend = []
        self.pend_kind = None
        self.pend_w0 = 0
        self.pend_part = self.root
        self.pend_type = ""
        self.pend_nset = None
        self.pend_elset = None
        self.in_assembly = False
        self.set_seen = set()
        self.cur_test = None

    def remember_set(self, kind, name, part=None, surface=None):
        key = (kind, id(part) if part is not None else None, name_key(name))
        if key not in self.set_seen:
            self.set_seen.add(key)
            self.m.set_defs.append(dict(kind=kind, name=name_key(name),
                                       part=part, surface=surface))

    # ---- 대상 파트 ----
    def tgt(self):
        return self.cur_inst["part"] if self.cur_inst else self.cur_part

    # ---- 데이터 조각 ----
    def data(self, piece):
        """스캐너가 넘긴 조각. 절점/요소는 즉시 수치로 바꿔 텍스트를 버린다."""
        self.n_bytes += len(piece)
        mode = self.mode
        if mode == "NODE":
            if self.pend_w0 == 0:
                self.pend_w0 = bytes_first_width(piece)
            arr, w = piece_to_flat(piece, 4)
            if arr is not None:
                self.pend.append((arr, w))
            self.pend_kind = "NODE"
        elif mode == "ELEMENT":
            cls = classify(self.el_type)
            hint = (cls["nn"] + 1) if cls else 0
            if self.pend_w0 == 0:
                self.pend_w0 = bytes_first_width(piece)
            arr, w = piece_to_flat(piece, hint)
            if arr is not None:
                self.pend.append((arr, w))
            self.pend_kind = "ELEMENT"
        else:
            self.pieces.append(piece.decode("latin-1"))

    def flush(self):
        if self.pend_kind == "NODE":
            self._finish_nodes()
        elif self.pend_kind == "ELEMENT":
            self._finish_elements()
        self.pend = []
        self.pend_kind = None
        self.pend_w0 = 0
        if not self.pieces:
            return
        txt = "".join(self.pieces)
        self.pieces = []
        if not txt.strip():
            return
        # A trailing comma is an empty field, not a continuation of the next
        # material/test/section record. Sets accept each physical line too.
        for line in txt.split("\n"):
            line = line.strip()
            if line:
                self.data_line(line)

    def _concat(self):
        parts = [a for a, _ in self.pend]
        if not parts:
            return None, 0
        ws = [w for _, w in self.pend if w]
        w = ws[0] if ws else 0
        if HAVE_NUMPY:
            flat = parts[0] if len(parts) == 1 else np.concatenate(parts)
        else:
            flat = parts[0] if len(parts) == 1 else [x for p in parts for x in p]
        return flat, w

    @staticmethod
    def _pick_width(n, w, cands):
        for cand in ([w] if w else []) + list(cands):
            if cand and n % cand == 0:
                return cand
        return 0

    def _finish_nodes(self):
        flat, w = self._concat()
        if flat is None:
            return
        w = self._pick_width(len(flat), w, [self.pend_w0, 4, 3])
        if w < 2:
            self.log.err("*NODE 블록의 열 수를 판단하지 못해 건너뜁니다.")
            return
        P = self.pend_part
        if HAVE_NUMPY:
            a = flat.reshape(-1, w)
            ids = a[:, 0].astype(np.int64)
            m = min(3, w - 1)
            xyz = np.zeros((a.shape[0], 3), np.float64)
            xyz[:, :m] = a[:, 1:1 + m]
        else:
            rows = [flat[i:i + w] for i in range(0, len(flat), w)]
            ids = [int(r[0]) for r in rows]
            xyz = [[(r[1] if w > 1 else 0.0), (r[2] if w > 2 else 0.0),
                    (r[3] if w > 3 else 0.0)] for r in rows]
        P.nblocks.append((ids, xyz))
        if self.pend_nset is not None:
            self.pend_nset.extend(int(v) for v in ids)

    def _finish_elements(self):
        flat, w = self._concat()
        if flat is None:
            return
        cls = classify(self.pend_type)
        cands = [(cls["nn"] + 1) if cls else 0, self.pend_w0]
        w = self._pick_width(len(flat), w, cands)
        if w < 2:
            self.log.err("*ELEMENT, type=%s 블록의 열 수를 판단하지 못해 건너뜁니다."
                         % self.pend_type)
            return
        P = self.pend_part
        if HAVE_NUMPY:
            a = flat.reshape(-1, w)
            ids = a[:, 0].astype(np.int64)
            conn = a[:, 1:].astype(np.int64)
        else:
            rows = [flat[i:i + w] for i in range(0, len(flat), w)]
            ids = [int(r[0]) for r in rows]
            conn = [[int(x) for x in r[1:]] for r in rows]
        P.eblocks.append(dict(type=self.pend_type, ids=ids, conn=conn))
        if self.pend_elset is not None:
            self.pend_elset.extend(int(v) for v in ids)

    # ---- 키워드 ----
    def keyword(self, line):
        if line.startswith("**"):
            return
        self.flush()
        kw, p = parse_keyword(line)
        m = self.m
        self.mode = None

        if kw == "ASSEMBLY":
            self.in_assembly = True
        elif kw == "END ASSEMBLY":
            self.in_assembly = False
        elif kw == "HEADING":
            self.mode = "HEADING"
        elif kw == "PART":
            nm = (p.get("NAME") or ("PART%d" % len(m.parts))).upper()
            self.cur_part = Part(nm)
            m.parts[nm] = self.cur_part
        elif kw == "END PART":
            self.cur_part = self.root
        elif kw == "INSTANCE":
            inst = dict(name=(p.get("NAME") or "INST%d" % len(m.instances)),
                        partName=(p.get("PART") or "").upper(),
                        t=[0.0, 0.0, 0.0], rot=None,
                        part=Part("LOCAL"), dataN=0)
            m.instances.append(inst)
            self.cur_inst = inst
            self.mode = "INSTANCE"
        elif kw == "END INSTANCE":
            self.cur_inst = None
        elif kw in ("NODE", "NODE INPUT"):
            self.mode = "NODE"
            self.pend_part = self.tgt()
            self.pend_nset = None
            if p.get("NSET"):
                nm = name_key(p["NSET"])
                self.pend_nset = self.pend_part.nsets.setdefault(nm, [])
                self.remember_set("nsets", nm, self.pend_part)
        elif kw == "ELEMENT":
            self.mode = "ELEMENT"
            self.el_type = (p.get("TYPE") or "").upper()
            self.pend_type = self.el_type
            self.pend_part = self.tgt()
            m.el_types.add(self.el_type)
            self.pend_elset = None
            if p.get("ELSET"):
                nm = name_key(p["ELSET"])
                self.pend_elset = self.pend_part.elsets.setdefault(nm, [])
                # Property membership is needed internally, but an implicit
                # element-block group is not an explicit user SET declaration.
        elif kw in ("NSET", "ELSET"):
            is_node = kw == "NSET"
            nm = ((p.get("NSET") if is_node else p.get("ELSET")) or "UNNAMED").upper()
            self.set_gen = bool(p.get("GENERATE"))
            self.set_arr = []
            if p.get("INSTANCE") or (self.in_assembly and not self.cur_inst):
                rec = dict(name=nm, instance=name_key(p.get("INSTANCE")), ids=self.set_arr)
                (m.asm_nsets if is_node else m.asm_elsets).append(rec)
                self.remember_set("nsets" if is_node else "elsets", nm)
            else:
                d = self.tgt().nsets if is_node else self.tgt().elsets
                if nm in d:
                    self.set_arr = d[nm]
                else:
                    d[nm] = self.set_arr
                self.remember_set("nsets" if is_node else "elsets", nm, self.tgt())
            self.mode = "SET"
        elif kw == "MATERIAL":
            nm = (p.get("NAME") or "MAT%d" % len(m.materials)).upper()
            self.cur_mat = dict(name=p.get("NAME") or nm, density=None,
                                e=None, nu=None, plastic=[], hyperfoam=False,
                                tests=[], hyperfoam_data=[])
            m.materials[nm] = self.cur_mat
        elif kw == "HYPERFOAM":
            if self.cur_mat is not None:
                self.cur_mat["hyperfoam"] = True
                self.cur_mat["hyperfoam_params"] = dict(p)
            self.mode = "HYPERFOAM"
        elif kw in ("UNIAXIAL TEST DATA", "BIAXIAL TEST DATA", "PLANAR TEST DATA",
                    "VOLUMETRIC TEST DATA", "SIMPLE SHEAR TEST DATA"):
            self.cur_test = dict(kind=kw, params=dict(p), rows=[])
            if self.cur_mat is not None:
                self.cur_mat["tests"].append(self.cur_test)
            self.mode = "TESTDATA"
        elif kw in ("DENSITY", "ELASTIC", "PLASTIC"):
            self.mode = kw
        elif kw in SECTION_KW:
            self.cur_section = dict(type=kw, elset=(p.get("ELSET") or "").upper(),
                                    material=(p.get("MATERIAL") or "").upper(),
                                    shape=(p.get("SECTION") or "").upper(), data=[])
            self.tgt().sections.append(self.cur_section)
            self.mode = "SECTION"
        elif kw == "MASS":
            self.mass_elset = (p.get("ELSET") or "").upper()
            self.mode = "MASSVAL"
        elif kw == "BOUNDARY":
            self.bc_type = (p.get("TYPE") or "").upper()
            self.mode = "BOUNDARY"
        elif kw == "SURFACE":
            owner = (self.cur_inst["partName"] if self.cur_inst
                     else (self.cur_part.name if self.cur_part is not self.root else "__ASM__"))
            self.cur_surf = dict(name=(p.get("NAME") or "SURF%d" % len(m.surfaces)).upper(),
                                 stype=(p.get("TYPE") or "ELEMENT").upper(),
                                 owner=owner, rows=[], part=(self.tgt() if
                                     self.cur_inst or self.cur_part is not self.root else None))
            m.surfaces.append(self.cur_surf)
            self.remember_set("surface", self.cur_surf["name"],
                              self.cur_surf["part"], self.cur_surf)
            self.mode = "SURFACE"
        elif kw == "SURFACE INTERACTION":
            self.cur_inter = dict(name=(p.get("NAME") or "").upper(), fs=None)
            m.interactions[self.cur_inter["name"]] = self.cur_inter
        elif kw == "FRICTION":
            self.mode = "FRICTION"
        elif kw == "CONTACT PAIR":
            self.cur_cp = dict(interaction=(p.get("INTERACTION") or "").upper(),
                               ctype=(p.get("TYPE") or "").upper(),
                               tied=bool(p.get("TIED")), rows=[])
            m.contact_pairs.append(self.cur_cp)
            self.mode = "CONTACTPAIR"
        elif kw == "TIE":
            self.cur_tie = dict(name=p.get("NAME") or "Tie-%d" % (len(m.ties) + 1), rows=[])
            m.ties.append(self.cur_tie)
            self.mode = "TIE"
        elif kw == "MPC":
            self.mode = "MPC"
        elif kw == "COUPLING":
            self.cur_coup = dict(name=p.get("CONSTRAINT NAME") or "Coupling-%d" % (len(m.couplings) + 1),
                                 ref=p.get("REF NODE") or "", surf=p.get("SURFACE") or "",
                                 kind="KINEMATIC")
            m.couplings.append(self.cur_coup)
        elif kw == "KINEMATIC":
            if self.cur_coup:
                self.cur_coup["kind"] = "KINEMATIC"
        elif kw in ("DISTRIBUTING", "DISTRIBUTING COUPLING"):
            if self.cur_coup:
                self.cur_coup["kind"] = "DISTRIBUTING"
        elif kw == "EQUATION":
            self.cur_eq = None
            self.eq_need = 0
            self.mode = "EQUATION"
        elif kw == "RIGID BODY":
            m.rigid_bodies.append(dict(ref=p.get("REF NODE") or "",
                                       elset=(p.get("ELSET") or "").upper(),
                                       pin=(p.get("PIN NSET") or "").upper(),
                                       tie=(p.get("TIE NSET") or "").upper()))
        elif kw == "CONTACT":
            m.general_contact = True
        elif kw in ("CONTACT INCLUSIONS", "CONTACT EXCLUSIONS",
                    "CONTACT PROPERTY ASSIGNMENT", "CONTACT CONTROLS",
                    "SURFACE BEHAVIOR", "CLEARANCE", "INCLUDE"):
            pass
        else:
            if kw not in UNSUPPORTED_QUIET:
                m.unsupported[kw] = m.unsupported.get(kw, 0) + 1

    # ---- 일반 데이터 줄 ----
    def data_line(self, line):
        F = [x.strip().strip("\"'") for x in line.split(",")]
        mode = self.mode
        m = self.m
        if mode == "HEADING":
            if not self.heading_done:
                m.title = line.strip()[:80]
                self.heading_done = True
        elif mode == "INSTANCE":
            inst = self.cur_inst
            try:
                nums = [float(x) for x in F if x != ""]
            except ValueError:
                nums = []
            if inst["dataN"] == 0 and len(nums) >= 3:
                inst["t"] = nums[:3]
            elif inst["dataN"] == 1 and len(nums) >= 7:
                inst["rot"] = nums[:7]
            inst["dataN"] += 1
        elif mode == "SET":
            if self.set_arr is None:
                return
            if self.set_gen:
                try:
                    a, b = int(F[0]), int(F[1])
                    c = int(F[2]) if len(F) > 2 and F[2] else 1
                except (ValueError, IndexError):
                    return
                self.set_arr.extend(range(a, b + 1, c or 1))
            else:
                for f in F:
                    if not f:
                        continue
                    try:
                        self.set_arr.append(int(f))
                    except ValueError:
                        self.set_arr.append(f.upper())
        elif mode == "DENSITY":
            if self.cur_mat:
                try:
                    self.cur_mat["density"] = abaqus_float(F[0])
                except (ValueError, IndexError):
                    pass
        elif mode == "ELASTIC":
            if self.cur_mat and self.cur_mat["e"] is None:
                try:
                    self.cur_mat["e"] = abaqus_float(F[0])
                    self.cur_mat["nu"] = abaqus_float(F[1])
                except (ValueError, IndexError):
                    pass
        elif mode == "PLASTIC":
            if self.cur_mat:
                try:
                    sy = abaqus_float(F[0])
                    ep = abaqus_float(F[1]) if len(F) > 1 and F[1] else 0.0
                    self.cur_mat["plastic"].append((ep, sy))
                except (ValueError, IndexError):
                    pass
        elif mode in ("TESTDATA", "HYPERFOAM"):
            try:
                row = [abaqus_float(x) for x in F if x]
            except ValueError:
                raise ValueError("잘못된 %s 수치 데이터: %s" % (mode, line))
            if mode == "TESTDATA" and self.cur_test is not None:
                self.cur_test["rows"].append(row)
            elif self.cur_mat is not None:
                self.cur_mat["hyperfoam_data"].append(row)
        elif mode == "SECTION":
            if self.cur_section is not None:
                self.cur_section["data"].append(F)
        elif mode == "MASSVAL":
            try:
                self.tgt().massvals[self.mass_elset] = abaqus_float(F[0])
            except (ValueError, IndexError):
                pass
        elif mode == "BOUNDARY":
            if F and F[0]:
                m.boundaries.append(dict(set=F[0].upper(), type=self.bc_type, f=F[1:]))
        elif mode == "SURFACE":
            if self.cur_surf and F and F[0]:
                self.cur_surf["rows"].append((F[0], (F[1] if len(F) > 1 else "").upper()))
        elif mode == "FRICTION":
            if self.cur_inter and self.cur_inter["fs"] is None:
                try:
                    self.cur_inter["fs"] = abaqus_float(F[0])
                except (ValueError, IndexError):
                    pass
        elif mode == "CONTACTPAIR":
            if self.cur_cp and len(F) >= 2 and F[0] and F[1]:
                self.cur_cp["rows"].append((F[0], F[1]))
        elif mode == "TIE":
            if self.cur_tie and len(F) >= 2 and F[0] and F[1]:
                self.cur_tie["rows"].append((F[0], F[1]))
        elif mode == "MPC":
            if len(F) >= 3 and F[0]:
                m.mpcs.append(dict(type=F[0].upper(), a=F[1], b=F[2]))
        elif mode == "EQUATION":
            if self.eq_need == 0:
                try:
                    self.eq_need = int(F[0])
                except (ValueError, IndexError):
                    self.eq_need = 0
                if self.eq_need:
                    self.cur_eq = dict(terms=[])
                    m.equations.append(self.cur_eq)
            elif self.cur_eq is not None:
                k = 0
                while k + 2 < len(F) and len(self.cur_eq["terms"]) < self.eq_need:
                    try:
                        self.cur_eq["terms"].append(
                            (F[k], int(F[k + 1]), abaqus_float(F[k + 2])))
                    except ValueError:
                        pass
                    k += 3
                if len(self.cur_eq["terms"]) >= self.eq_need:
                    self.eq_need = 0

    def finish(self):
        self.flush()
        return self.m


# ============================================================
# *INCLUDE 해석 (디스크에서 직접 찾는다)
# ============================================================
RE_INCLUDE = re.compile(r"^\*\s*INCLUDE\b", re.I)


def resolve_include(ref, base_dir, cache, log):
    ref = ref.strip().strip("\"'")
    cand = ref.replace("\\", os.sep).replace("/", os.sep)
    p1 = cand if os.path.isabs(cand) else os.path.join(base_dir, cand)
    if os.path.isfile(p1):
        return p1
    base = os.path.basename(cand)
    p2 = os.path.join(base_dir, base)
    if os.path.isfile(p2):
        return p2
    if cache.get("__walked__") is None:
        idx = {}
        for root, _dirs, files in os.walk(base_dir):
            for f in files:
                idx.setdefault(f.lower(), os.path.join(root, f))
        cache["__walked__"] = idx
    hit = cache["__walked__"].get(base.lower())
    return hit


def read_deck(path, parser, log, progress=None):
    """메인 덱과 *INCLUDE를 재귀적으로 읽어 parser에 흘려 넣는다"""
    base_dir = os.path.dirname(os.path.abspath(path))
    cache = {}
    stats = dict(files=0, missing=[], bytes=0, total=os.path.getsize(path))

    def feed(fp, stack, depth):
        stats["files"] += 1
        for kind, payload in scan_file(fp):
            if kind == "data":
                parser.data(payload)
                if progress:
                    progress(parser.n_bytes, stats["total"])
                continue
            if RE_INCLUDE.match(payload):
                _kw, p = parse_keyword(payload)
                ref = p.get("INPUT") or p.get("FILE") or ""
                if not ref:
                    log.warn("*INCLUDE 경로를 읽지 못했습니다.")
                    continue
                target = resolve_include(ref, os.path.dirname(os.path.abspath(fp)),
                                         cache.setdefault(os.path.dirname(os.path.abspath(fp)), {}), log)
                if not target:
                    target = resolve_include(ref, base_dir, cache, log)
                if not target:
                    stats["missing"].append(ref)
                    raise FileNotFoundError("*INCLUDE 파일을 찾지 못했습니다: %s (기준: %s)"
                                            % (ref, os.path.dirname(os.path.abspath(fp))))
                key = os.path.normcase(os.path.abspath(target))
                if key in stack or depth > 12:
                    raise ValueError("*INCLUDE 순환 참조 또는 중첩 한도 초과: " + ref)
                parser.flush()
                stats["total"] += os.path.getsize(target)
                log.ok("*INCLUDE 병합: %s (%.1f MB)"
                       % (os.path.basename(target), os.path.getsize(target) / 1048576.0))
                feed(target, stack | {key}, depth + 1)
                continue
            parser.keyword(payload)

    feed(path, {os.path.normcase(os.path.abspath(path))}, 0)
    parser.finish()
    stats["bytes"] = parser.n_bytes
    return stats


# ============================================================
# 좌표 변환
# ============================================================
def make_transform(inst):
    t = inst["t"] or [0.0, 0.0, 0.0]
    r = inst["rot"]
    ident = (r is None) and (t[0] == 0 and t[1] == 0 and t[2] == 0)
    if ident:
        return None
    if r is None:
        def tr(xyz):
            if HAVE_NUMPY:
                return xyz + np.asarray(t)
            return [[p[0] + t[0], p[1] + t[1], p[2] + t[2]] for p in xyz]
        return tr
    ax, ay, az, bx, by, bz, ang = r
    ux, uy, uz = bx - ax, by - ay, bz - az
    L = math.hypot(math.hypot(ux, uy), uz) or 1.0
    ux, uy, uz = ux / L, uy / L, uz / L
    th = math.radians(ang)
    c, s = math.cos(th), math.sin(th)
    C = 1 - c
    R = [[c + ux * ux * C, ux * uy * C - uz * s, ux * uz * C + uy * s],
         [uy * ux * C + uz * s, c + uy * uy * C, uy * uz * C - ux * s],
         [uz * ux * C - uy * s, uz * uy * C + ux * s, c + uz * uz * C]]

    def tr(xyz):
        if HAVE_NUMPY:
            M = np.asarray(R)
            q = (np.asarray(xyz) - np.array([ax, ay, az])) @ M.T
            return q + np.array([ax + t[0], ay + t[1], az + t[2]])
        out = []
        for p in xyz:
            x, y, z = p[0] - ax, p[1] - ay, p[2] - az
            out.append([R[0][0] * x + R[0][1] * y + R[0][2] * z + ax + t[0],
                        R[1][0] * x + R[1][1] * y + R[1][2] * z + ay + t[1],
                        R[2][0] * x + R[2][1] * y + R[2][2] * z + az + t[2]])
        return out
    return tr


# ============================================================
# 변환기
# ============================================================
class Converter:
    def __init__(self, model, opt, log, progress=None):
        self.m = model
        self.opt = opt
        self.log = log
        self.progress = progress
        self.UD = UNIT_DEFAULT[opt["unit"]]

        self.parts = []          # {pid, secid, mid, title}
        self.sections = []
        self.mats = []
        self.curves = []
        self.nsets = []          # {sid, name, ids}
        self.esets = []
        self.segsets = []
        self.spcs = []
        self.nrbs = []
        self.interps = []
        self.lineq = []
        self.imap = []
        self.type_count = {}

        self.mid_of = {}
        self.mid_seq = 0
        self.pid_seq = 0
        self.sec_seq = 0
        self.max_node = 0
        self.max_elem = 0
        self.counts = dict(node=0, solid=0, shell=0, beam=0, mass=0, disc=0)

        self.total_items = 0
        self.done_items = 0
        self._next_tick = 0
        self.inst_maps = {}
        self.inst_part_of = {}
        self.elem_info = {}
        self._auto_elem_info = {}
        self.node_coord = {}
        self.global_nsets = {}

        self.tmp = {}
        self.contexts = {}
        self.asm_defs = {"nsets": {}, "elsets": {}}
        self._resolved = {}
        self._resolve_warnings = set()
        self._surf_cache = {}
        self._surface_defs = {}
        self._seg_sid = {}
        self._node_sid = {}
        self._element_sid = {}
        self._sid = 0
        self.set_output = []
        self._sets_by_sid = {}
        self._set_source_order = None
        self.hourglasses = []
        self.contacts = []
        self.section_hits = {}
        self._part_pid_blocks = {}
        # v2.5 mounting node handling
        self._mount_nodes = set()        # deleted reference node IDs (output IDs)
        self._mount_couplings = set()    # id(coupling) not converted
        self._mount_mpcs = set()         # id(mpc row) not converted
        self._mount_sid = None
        self._mount_bc_hits = 0

    # ---------- 임시 파일 ----------
    def _tmp(self, key):
        f = self.tmp.get(key)
        if f is None:
            f = tempfile.TemporaryFile("w+b")
            self.tmp[key] = f
        return f

    # ---------- 재료 ----------
    def get_mid(self, name):
        key = (name or "").upper()
        if key in self.mid_of:
            return self.mid_of[key]
        self.mid_seq += 1
        mid = self.mid_seq
        UD = self.UD
        mat = self.m.materials.get(key)
        if mat is None:
            self.mats.append(dict(mid=mid, type="elastic",
                                  name=name or "DEFAULT_STEEL",
                                  rho=UD["rho"], e=UD["e"], nu=UD["nu"]))
            if name:
                self.log.warn('재료 "%s" 정의를 찾지 못해 기본 강재 물성으로 채웠습니다 (MID %d).'
                              % (name, mid))
        else:
            rho = UD["rho"] if mat["density"] is None else mat["density"]
            if mat["density"] is None:
                self.log.warn('재료 "%s"에 밀도가 없어 기본값을 넣었습니다.' % mat["name"])
            e = UD["e"] if mat["e"] is None else mat["e"]
            nu = UD["nu"] if mat["nu"] is None else mat["nu"]
            if mat.get("hyperfoam"):
                pts = self.foam_curve(mat)
                lcid = len(self.curves) + 1
                self.curves.append(dict(lcid=lcid,
                                        name=mat["name"] + "_COMPRESSION", pts=pts))
                self.mats.append(dict(mid=mid, type="foam57", name=mat["name"],
                                      rho=rho, e=FOAM_DEFAULT_E, tc=FOAM_DEFAULT_TC,
                                      lcid=lcid))
                self.log.ok('HYPERFOAM "%s" → MAT57, E=%g, TC=%g, LCID=%d (%d점)'
                            % (mat["name"], FOAM_DEFAULT_E, FOAM_DEFAULT_TC, lcid, len(pts)))
            elif mat["plastic"]:
                lcid = 0
                if len(mat["plastic"]) > 1:
                    lcid = len(self.curves) + 1
                    self.curves.append(dict(lcid=lcid,
                                            name=mat["name"] + "_STRESS_STRAIN",
                                            pts=list(mat["plastic"])))
                self.mats.append(dict(mid=mid, type="plastic", name=mat["name"],
                                      rho=rho, e=e, nu=nu,
                                      sigy=mat["plastic"][0][1], lcss=lcid))
            else:
                self.mats.append(dict(mid=mid, type="elastic", name=mat["name"],
                                      rho=rho, e=e, nu=nu))
        self.mid_of[key] = mid
        return mid

    def foam_curve(self, mat):
        """Abaqus nominal stress,strain -> MAT57 compression strain,stress.

        Abaqus: SIMACAEKEYRefMap/simakey-r-uniaxialtestdata.htm.
        MAT57: Ansys PyDYNA MatLowDensityFoam (LCID is nominal stress/strain).
        No coefficient fitting, true-stress conversion, or smoothing is done.
        """
        tests = [t for t in mat.get("tests", []) if t["kind"] == "UNIAXIAL TEST DATA"]
        rows = []
        for t in tests:
            if name_key(t["params"].get("DIRECTION")) == "TENSION":
                self.log.warn('HYPERFOAM "%s": 인장 시험표는 MAT57 압축 LCID에서 제외합니다.' % mat["name"])
                continue
            rows.extend(t["rows"])
        if not rows or any(len(r) < 2 for r in rows):
            raise ValueError('HYPERFOAM "%s": MAT57에 연결할 *UNIAXIAL TEST DATA '
                             '(nominal stress, nominal strain)가 필요합니다.' % mat["name"])
        if any(not math.isfinite(v) for r in rows for v in r[:2]):
            raise ValueError('HYPERFOAM "%s": 시험표에 비유한 수치가 있습니다.' % mat["name"])
        # Signed Abaqus compression is negative. Do not fold a tension branch
        # onto compression when both branches are supplied.
        has_negative_strain = any(r[1] < 0 for r in rows)
        if has_negative_strain:
            if any(r[1] > 0 for r in rows):
                self.log.warn('HYPERFOAM "%s": 압축 분기만 LCID에 연결합니다.' % mat["name"])
            rows = [r for r in rows if r[1] <= 0]
        else:
            self.log.warn('HYPERFOAM "%s": 양수 시험값을 압축 크기로 해석합니다. '
                          '입력 표가 압축 시험인지 확인하세요.' % mat["name"])
        pairs = {}
        for r in rows:
            stress, strain = r[:2]
            if strain * stress < 0:
                raise ValueError('HYPERFOAM "%s": 응력·변형률 부호가 서로 다릅니다.' % mat["name"])
            x, y = abs(strain), abs(stress)
            if not 0 <= x < 1:
                raise ValueError('HYPERFOAM "%s": 압축 nominal strain은 0 이상 1 미만이어야 합니다.' % mat["name"])
            if x in pairs and not math.isclose(pairs[x], y, rel_tol=1e-9, abs_tol=1e-12):
                raise ValueError('HYPERFOAM "%s": 같은 변형률에 다른 응력이 있습니다. '
                                 '단일 압축 loading curve가 필요합니다.' % mat["name"])
            pairs[x] = y
        if not any(x > 0 for x in pairs):
            raise ValueError('HYPERFOAM "%s": 유효한 압축 시험점이 없습니다.' % mat["name"])
        if 0.0 not in pairs:
            pairs[0.0] = 0.0
            self.log.info('HYPERFOAM "%s": LCID 원점 (0,0)을 추가했습니다.' % mat["name"])
        if any(t["kind"] != "UNIAXIAL TEST DATA" for t in mat.get("tests", [])):
            self.log.warn('HYPERFOAM "%s": 이축·체적·전단 시험표는 MAT57 단축 압축곡선에 합치지 않습니다.' % mat["name"])
        if any(len(r) > 2 and r[2] != 0 for r in rows):
            self.log.warn('HYPERFOAM "%s": 횡변형률은 MAT57 LCID에 포함되지 않습니다.' % mat["name"])
        return sorted(pairs.items())

    # ---------- 세트 해석 ----------
    @staticmethod
    def resolve_set(d, name, depth=0):
        arr = d.get((name or "").upper())
        if arr is None or depth > 6:
            return []
        out = []
        for v in arr:
            if isinstance(v, str):
                out.extend(Converter.resolve_set(d, v, depth + 1))
            else:
                out.append(v)
        return out

    def _tick(self, n, label):
        self.done_items += n
        if self.progress and self.done_items >= self._next_tick:
            self._next_tick = self.done_items + 100000
            self.progress(self.done_items, max(self.total_items, 1), label)

    def prepare_contexts(self, instances):
        """Resolve scopes before assigning sections or generating surface cards."""
        root = self.m.parts["__ROOT__"]
        if root.nblocks and not any(i["partName"] == "__ROOT__" for i in instances):
            instances.insert(0, dict(name="", partName="__ROOT__", t=[0, 0, 0],
                                     rot=None, part=Part("L"), dataN=0))
        for inst in instances:
            base = self.m.parts.get(inst["partName"])
            if base is None:
                self.log.warn('인스턴스 "%s"의 파트가 없습니다.' % inst["name"])
                continue
            P = merge_parts(base, inst["part"])
            key = name_key(inst["name"])
            if key in self.contexts:
                raise ValueError("중복 인스턴스 이름: " + key)
            ns = [b[0] for b in P.nblocks if len(b[0])]
            es = [b["ids"] for b in P.eblocks if len(b["ids"])]
            nmin = min((int(_amin(a)) for a in ns), default=1)
            emin = min((int(_amin(a)) for a in es), default=1)
            no = self.max_node if ns and nmin <= self.max_node else 0
            eo = self.max_elem if es and emin <= self.max_elem else 0
            self.max_node = max(self.max_node, max((int(_amax(a)) + no for a in ns), default=0))
            self.max_elem = max(self.max_elem, max((int(_amax(a)) + eo for a in es), default=0))
            self.contexts[key] = dict(inst=inst, base=base, P=P, index=EidIndex(P),
                                      nOff=no, eOff=eo)
            self.inst_maps[key] = dict(nOff=no, eOff=eo, nsets={}, elsets={})
            self.inst_part_of[key] = base.name
            if no or eo:
                self.log.info('인스턴스 "%s": 절점 +%d, 요소 +%d offset' % (key, no, eo))
        # Validate against nodes actually emitted, rather than a min/max range.
        if HAVE_NUMPY:
            node_blocks = [ids + ctx["nOff"] for ctx in self.contexts.values()
                           for ids, _ in ctx["P"].nblocks if len(ids)]
            self._solid_node_ids = (np.unique(np.concatenate(node_blocks))
                                    if node_blocks else np.empty(0, np.int64))
        else:
            self._solid_node_ids = {int(n) + ctx["nOff"] for ctx in self.contexts.values()
                                    for ids, _ in ctx["P"].nblocks for n in ids}
        for kind, records in (("nsets", self.m.asm_nsets), ("elsets", self.m.asm_elsets)):
            for rec in records:
                self.asm_defs[kind].setdefault(rec["name"], []).append(rec)
            # Flat/global definitions following an assembly can contain I.SET
            # or I.123 references, and may be used by root-level sections.
            if "" not in self.contexts:
                for nm, ids in getattr(root, kind).items():
                    self.asm_defs[kind].setdefault(nm, []).append(dict(name=nm, instance="", ids=ids))
        for surf in self.m.surfaces:
            for ref, pref in self.surface_bindings(surf):
                self._surface_defs[ref] = (surf, pref)
        self._needed_elements = set()
        self._need_all_surface_elements = False
        for ref, (surf, pref) in self._surface_defs.items():
            if surf["stype"] == "ELEMENT":
                for row, _ in surf["rows"]:
                    self._needed_elements.update(self.resolve_ids("elsets", row, pref))
        if self.opt["contact"]:
            for rb in self.m.rigid_bodies:
                self._needed_elements.update(self.resolve_ids("elsets", rb["elset"]))

    def surface_bindings(self, surf):
        part = surf.get("part")
        if part is None:
            return [(surf["name"], None)]
        return [((key + "." if key else "") + surf["name"], key)
                for key, ctx in self.contexts.items()
                if part is ctx["base"] or part is ctx["inst"]["part"]]

    def resolve_ids(self, kind, ref, pref=None, active=None):
        R = name_key(ref)
        pref = name_key(pref) if pref is not None else None
        local = self.contexts.get(pref)
        # Millions of node/element IDs must not each create a cache entry.
        try:
            numeric = int(R)
        except ValueError:
            numeric = None
        if numeric is not None:
            numeric_ctx = local if local is not None else self.contexts.get("")
            off = numeric_ctx["nOff" if kind == "nsets" else "eOff"] if numeric_ctx else 0
            return [numeric + off]
        token = (kind, pref, R)
        if token in self._resolved:
            return self._resolved[token]
        active = set() if active is None else active
        if token in active:
            raise ValueError("세트 순환 참조: %s / %s" % (pref or "ASSEMBLY", R))
        active = active | {token}
        values = []
        if local is not None and R in getattr(local["P"], kind):
            offset = local["nOff" if kind == "nsets" else "eOff"]
            for v in getattr(local["P"], kind)[R]:
                if isinstance(v, int):
                    values.append(v + offset)
                else:
                    values.extend(self.resolve_ids(kind, v, pref, active))
        elif R in self.asm_defs[kind]:
            for rec in self.asm_defs[kind][R]:
                owner = rec["instance"] or None
                if owner is not None and owner not in self.contexts:
                    if token not in self._resolve_warnings:
                        self._resolve_warnings.add(token)
                        self.log.warn('세트 "%s"가 없는 인스턴스 "%s"를 참조합니다.' % (R, owner))
                    continue
                owner_ctx = self.contexts.get(owner) or self.contexts.get("")
                off = owner_ctx["nOff" if kind == "nsets" else "eOff"] if owner_ctx else 0
                for v in rec["ids"]:
                    if isinstance(v, int):
                        values.append(v + off)
                    else:
                        values.extend(self.resolve_ids(kind, v, owner, active))
        else:
            if not hasattr(self, "_context_prefixes"):
                self._context_prefixes = sorted(self.contexts, key=len, reverse=True)
            prefix = next((key for key in self._context_prefixes
                           if key and R.startswith(key + ".")), None)
            if prefix is not None:
                values = self.resolve_ids(kind, R[len(prefix) + 1:], prefix, active)
            else:
                try:
                    n = int(R)
                except ValueError:
                    n = None
                if n is not None:
                    if local is not None:
                        values = [n + local["nOff" if kind == "nsets" else "eOff"]]
                    elif "" in self.contexts:
                        values = [n + self.contexts[""]["nOff" if kind == "nsets" else "eOff"]]
                    else:
                        values = [n]
                elif pref is None:
                    matches = [key for key, ctx in self.contexts.items() if R in getattr(ctx["P"], kind)]
                    if len(matches) == 1:
                        values = self.resolve_ids(kind, R, matches[0], active)
                    elif len(matches) > 1 and token not in self._resolve_warnings:
                        self._resolve_warnings.add(token)
                        self.log.warn('세트 "%s"가 여러 인스턴스에 있습니다. INSTANCE.SET 참조가 필요합니다.' % R)
        values = ordered_unique(values)
        self._resolved[token] = values
        return values

    def append_set(self, kind, record):
        self._sid += 1
        record["sid"] = self._sid
        record["kind"] = kind
        record["_sort_key"] = (self._set_source_order or (2, 0)) + (self._sid,)
        self.set_output.append(record)
        self._sets_by_sid[record["sid"]] = record
        (self.nsets if kind == "node" else self.segsets if kind == "segment" else self.esets).append(record)
        return record["sid"]

    def mark_source_set(self, record):
        if self._set_source_order is not None:
            key = self._set_source_order + (record["sid"],)
            record["_sort_key"] = min(record["_sort_key"], key)

    def finalize_set_order(self):
        """Make file order and numeric SID order agree, then fix references."""
        used = {name_key(s["name"][:80]) for s in self.set_output if s["kind"] != "segment"}
        for s in self.set_output:
            if s["kind"] == "segment":
                base = s.setdefault("_segment_base_name", s["name"])
                if base.lower().endswith("_seg"):
                    base = base[:-4]
                number = 1
                while True:
                    suffix = "_seg" if number == 1 else "_%d_seg" % number
                    title = base[:80-len(suffix)] + suffix
                    if name_key(title) not in used:
                        break
                    number += 1
                s["name"] = title
                used.add(name_key(title))
        def ordering(s):
            old = s["_sort_key"]
            if s.get("fixed_sid"):
                group = 4
            elif s["kind"] == "segment":
                group = 1
            elif s["kind"] == "node" and (old[0] == 1 or "SURF_COUPLING" in name_key(s["name"])):
                group = 2
            elif old[0] >= 2:
                group = 3
            else:
                group = 0
            return (group,) + old
        self.set_output.sort(key=ordering)
        reserved = {200001, 200002, 900001} if self.opt.get("auto_sets", True) else set()
        reserved |= {int(s["fixed_sid"]) for s in self.set_output if s.get("fixed_sid")}
        remap = {}
        next_id = 0
        for s in self.set_output:
            if s.get("fixed_sid"):
                remap[s["sid"]] = s["fixed_sid"]
                continue
            next_id += 1
            while next_id in reserved:
                next_id += 1
            remap[s["sid"]] = next_id
        for s in self.set_output:
            s["sid"] = remap[s["sid"]]
        self.nsets = [s for s in self.set_output if s["kind"] == "node"]
        self.esets = [s for s in self.set_output if s["kind"] == "element"]
        self.segsets = [s for s in self.set_output if s["kind"] == "segment"]
        for c in self.contacts:
            for field, type_field in (("ssid", "sstyp"), ("msid", "mstyp")):
                if c[type_field] in (0, 4) and c[field]:
                    c[field] = remap[c[field]]
        for b in self.spcs:
            b["sid"] = remap[b["sid"]]
        for rb in self.nrbs:
            rb["nsid"] = remap[rb["nsid"]]
        for mapping in (self._node_sid, self._seg_sid, self.global_nsets):
            for name, sid in list(mapping.items()):
                mapping[name] = remap[sid]
        self._sid = next_id
        self._sets_by_sid = {s["sid"]: s for s in self.set_output}

    def add_automatic_sets(self):
        """Append fixed-ID selection sets after all existing set references settle.

        A PART set covers mixed element families without mislabelling shell IDs
        as solid IDs. Only face-bearing structural elements define the extrema;
        reference nodes, point masses and generated beam nodes are excluded.
        """
        names = {"ELSET_ALL", "RIGID_Y", "RIGID_Z"}
        if any(name_key(s["name"]) in names for s in self.set_output):
            raise ValueError("자동 SET 이름 ELSET_ALL/RIGID_Y/RIGID_Z가 기존 SET과 겹칩니다. 기존 이름을 변경하세요.")

        def add(kind, sid, name, ids):
            if not ids:
                self.log.warn("자동 SET %s: 조건에 맞는 대상이 없어 출력하지 않습니다." % name)
                return
            if any(s["sid"] == sid for s in self.set_output):
                raise ValueError("자동 SET ID 충돌: %d" % sid)
            rec = dict(kind=kind, sid=sid, fixed_sid=sid, name=name, ids=ids,
                       _sort_key=(3, len(self.set_output), sid))
            self.set_output.append(rec)
            if kind == "node":
                self.nsets.append(rec)
            self.log.ok("자동 SET %s (ID=%d): %d개 %s" %
                        (name, sid, len(ids), "PART" if kind == "part" else "NODE"))

        add("part", 900001, "ELSET_ALL", [p["pid"] for p in self.parts])
        started = time.monotonic()
        if HAVE_NUMPY:
            records,nodes = self.automatic_exterior_numpy()
        else:
            records,nodes = self.automatic_exterior_python()
        add("node",200001,"RIGID_Y",self.select_plane_end(records,nodes,1,1,"RIGID_Y"))
        pid = self.center_bottom_part(records,nodes)
        if pid is None:
            self.log.warn("RIGID_Z: XY 중심선과 만나는 면이 없어 자동 선택을 생략합니다. 중앙 구멍/분리 형상을 확인하세요.")
        else:
            title = next((p["title"] for p in self.parts if p["pid"] == pid),str(pid))
            self.log.info("RIGID_Z 중앙 최하단 PART 자동 선택: %s (PID=%d)" % (title,pid))
            subset = [rec for rec,p in zip(records,self._exterior_pids) if p == pid]
            selected_nodes = {n for face,_,_ in subset for n in face}
            add("node",200002,"RIGID_Z",self.select_plane_end(subset,selected_nodes,2,-1,"RIGID_Z"))
        self._auto_elem_info.clear()
        self.post_stage(89.5,"자동 SET 생성 완료")
        self.log.ok("자동 SET 완료: %.2f초" % (time.monotonic()-started))

    def center_bottom_part(self, records, nodes):
        """Lowest face intersection of the vertical ray through structural XY center."""
        if not nodes:
            return None
        xyz = self.node_coord
        cx = (min(xyz[n][0] for n in nodes)+max(xyz[n][0] for n in nodes))/2
        cy = (min(xyz[n][1] for n in nodes)+max(xyz[n][1] for n in nodes))/2
        self.log.info("중앙 검색선: X=%.9g, Y=%.9g" % (cx,cy))
        best = None
        for i,(face,_,_) in enumerate(records):
            points = [xyz[n] for n in face]
            if not (min(p[0] for p in points)-1e-10 <= cx <= max(p[0] for p in points)+1e-10 and
                    min(p[1] for p in points)-1e-10 <= cy <= max(p[1] for p in points)+1e-10):
                continue
            for j in range(1,len(points)-1):
                a,b,c = points[0],points[j],points[j+1]
                bx,by = b[0]-a[0],b[1]-a[1]
                dx,dy = c[0]-a[0],c[1]-a[1]
                det = bx*dy-by*dx
                if abs(det) <= 1e-14*max(abs(bx*dy),abs(by*dx),1e-300):
                    continue
                px,py = cx-a[0],cy-a[1]
                u,v = (px*dy-py*dx)/det,(bx*py-by*px)/det
                if u >= -1e-9 and v >= -1e-9 and u+v <= 1+1e-9:
                    z = a[2]+u*(b[2]-a[2])+v*(c[2]-a[2])
                    candidate = (z,self._exterior_pids[i])
                    if best is None or candidate < best:
                        best = candidate
        return best[1] if best else None

    def select_plane_end(self, records, nodes, axis, sign, name):
        """Plane-angle filtering in vectorized chunks, with boundary connectivity.
        XY/10deg and XZ/10deg are the same geometric test as the respective
        axis-normal angles. Selection still excludes disconnected recessed faces.
        """
        if not nodes:
            return []
        xyz = self.node_coord
        projections = [sign*xyz[n][axis] for n in nodes]
        extreme = max(projections)
        tolerance = max((extreme-min(projections))*1e-8,
                        max(abs(x) for x in projections)*2e-15,1e-12)
        cosine = math.cos(math.radians(10))
        candidates = []
        for start in range(0,len(records),20000):
            chunk = records[start:start+20000]
            self.post_stage(85 if axis == 1 else 88,
                            "%s 평면 각도: %d/%d 면" % (name,start,len(records)))
            if HAVE_NUMPY:
                pts = np.asarray([[xyz[n] for n in (list(face)+[face[-1]]*(4-len(face)))]
                                  for face,_,_ in chunk],dtype=np.float64)
                relative = pts-pts[:,0:1,:]
                normal = np.cross(relative[:,1],relative[:,2])+np.cross(relative[:,2],relative[:,3])
                length = np.linalg.norm(normal,axis=1)
                centers = np.asarray([center if center is not True else (0,0,0)
                                      for _,center,_ in chunk],dtype=np.float64)
                two_sided = np.asarray([center is True for _,center,_ in chunk])
                inward = np.sum(normal*(pts.mean(axis=1)-centers),axis=1) < 0
                component = normal[:,axis]*sign
                component = np.where(two_sided,np.abs(component),
                                     np.where(inward,-component,component))
                keep = np.flatnonzero((length > 0) & (component >= (cosine-1e-12)*length))
            else:
                keep = []
                for i,(face,center,_) in enumerate(chunk):
                    p = [xyz[n] for n in face]
                    p += [p[-1]]*(4-len(p))
                    a,b,c = [[p[k][j]-p[0][j] for j in range(3)] for k in (1,2,3)]
                    cross = lambda u,v: (u[1]*v[2]-u[2]*v[1],u[2]*v[0]-u[0]*v[2],u[0]*v[1]-u[1]*v[0])
                    ab,bc = cross(a,b),cross(b,c)
                    normal = [ab[j]+bc[j] for j in range(3)]
                    length = math.sqrt(sum(v*v for v in normal))
                    dot = normal[axis]*sign
                    if center is True:
                        dot = abs(dot)
                    elif sum(normal[j]*(sum(v[j] for v in p)/4-center[j]) for j in range(3)) < 0:
                        dot = -dot
                    if length and dot >= (cosine-1e-12)*length:
                        keep.append(i)
            candidates.extend((chunk[i][0],chunk[i][2]) for i in keep)
        edges,seeds = {},[]
        for i,(face,_) in enumerate(candidates):
            if any(extreme-sign*xyz[n][axis] <= tolerance for n in face):
                seeds.append(i)
            for a,b in zip(face,face[1:]+face[:1]):
                edges.setdefault(tuple(sorted((a,b))),[]).append(i)
        selected,pending = set(seeds),list(seeds)
        while pending:
            face,_ = candidates[pending.pop()]
            for a,b in zip(face,face[1:]+face[:1]):
                for neighbor in edges.pop(tuple(sorted((a,b))),[]):
                    if neighbor not in selected:
                        selected.add(neighbor)
                        pending.append(neighbor)
        return sorted({n for i in selected for n in candidates[i][1]})

    def post_stage(self, pct, label):
        pct = max(pct, getattr(self, "_last_post_pct", 0))
        self._last_post_pct = pct
        callback = getattr(self, "stage_progress", None)
        if callback:
            callback(pct, label)

    def automatic_exterior_numpy(self):
        """Compact int64 face keys; centers/members built ONLY for exterior faces.

        No Python dictionary entry or center tuple is retained for each internal
        face. Sort adjacency removes every occurrence of multiply-owned faces.
        """
        infos = list(self._auto_elem_info.values())
        capacity = sum(len(FACE.get(v['sub'], {})) for v in infos if v['cat'] == 'solid')
        keys = np.zeros((capacity, 4), dtype=np.int32 if self.max_node <= 2147483647 else np.int64)
        owners = np.empty(capacity, dtype=np.int32 if len(infos) <= 2147483647 else np.int64)
        local_ids = np.empty(capacity, dtype=np.uint8)
        nodes = set()
        shells = []
        record_pids = []
        count = 0
        tables = {sub: list(table.values()) for sub, table in FACE.items()}
        groups = {}
        for owner,info in enumerate(infos):
            c = info["c"]
            if info["cat"] == "shell":
                face = tuple(ordered_unique(c[:4] if info["sub"].startswith("quad") else c[:3]))
                shells.append((face,True,face))
                record_pids.append(info.get("pid",0))
                nodes.update(face)
            elif info["sub"] in tables:
                groups.setdefault(info["sub"],[]).append(owner)
        processed = 0
        for sub,group in groups.items():
            table = tables[sub]
            nn = max(i for f in table for i in f)+1
            for start in range(0,len(group),50000):
                own = np.asarray(group[start:start+50000],dtype=owners.dtype)
                cn = np.asarray([infos[int(o)]["c"][:nn] for o in own],dtype=keys.dtype)
                nodes.update(np.unique(cn).tolist())
                ordered = np.sort(cn,axis=1)
                repeated = np.any(ordered[:,1:] == ordered[:,:-1],axis=1)
                regular = np.flatnonzero(~repeated)
                for fi,local in enumerate(table):
                    n = len(regular)
                    face = np.sort(cn[regular][:,local],axis=1)
                    keys[count:count+n,:len(local)] = face
                    owners[count:count+n] = own[regular]
                    local_ids[count:count+n] = fi
                    count += n
                for row in np.flatnonzero(repeated):
                    seen = set()
                    for fi,local in enumerate(table):
                        face = tuple(sorted(set(int(cn[row,i]) for i in local)))
                        if len(face)<3 or face in seen:
                            continue
                        seen.add(face)
                        keys[count,:len(face)] = face
                        owners[count] = own[row]
                        local_ids[count] = fi
                        count += 1
                processed += len(own)
                self.post_stage(80+2*processed/max(len(infos),1),
                                "자동 SET: 배열 면 추출 %d/%d" % (processed,len(infos)))
        self.post_stage(82, "자동 SET: %s개 면 정렬/내부면 제거" % f"{count:,}")
        keys = keys[:count]
        order = np.lexsort((keys[:,3],keys[:,2],keys[:,1],keys[:,0]))
        sorted_keys = keys[order]
        unique = np.ones(count, dtype=bool)
        duplicate = np.all(sorted_keys[1:] == sorted_keys[:-1], axis=1)
        unique[1:] &= ~duplicate
        unique[:-1] &= ~duplicate
        exterior = order[unique]
        del keys, sorted_keys, order, unique, duplicate
        self.post_stage(83, "자동 SET: 외곽면 %s개 구성" % f"{len(exterior):,}")
        records = shells
        xyz = self.node_coord
        for j, row in enumerate(exterior):
            if j % 10000 == 0:
                self.post_stage(83+2*j/max(len(exterior),1), "자동 SET: 외곽면 %d/%d" % (j,len(exterior)))
            info = infos[int(owners[row])]
            c = info['c']
            table = tables[info['sub']]
            face = tuple(ordered_unique(c[i] for i in table[int(local_ids[row])]))
            corners = ordered_unique(c[i] for f in table for i in f)
            center = tuple(sum(xyz[n][a] for n in corners)/len(corners) for a in range(3))
            members = list(face)
            if info.get('keep_tet10'):
                for a,b,mid in ((0,1,4),(1,2,5),(2,0,6),(0,3,7),(1,3,8),(2,3,9)):
                    if c[a] in face and c[b] in face:
                        members.append(c[mid])
            records.append((face,center,tuple(ordered_unique(members))))
            record_pids.append(info.get("pid",0))
        self._exterior_pids = record_pids
        return records,nodes

    def automatic_exterior_python(self):
        xyz = self.node_coord
        faces = {}
        shell_faces = []
        structural_nodes = set()
        for ei, info in enumerate(self._auto_elem_info.values()):
            if ei % 10000 == 0:
                self.post_stage(80+5*ei/max(len(self._auto_elem_info),1), "자동 SET: Python 면 추출 %d/%d" % (ei,len(self._auto_elem_info)))
            c = info["c"]
            if info["cat"] == "shell":
                face = tuple(ordered_unique(c[:4] if info["sub"].startswith("quad") else c[:3]))
                shell_faces.append((face, True, face, info.get("pid",0)))
                structural_nodes.update(face)
                continue
            local_faces = FACE.get(info["sub"], {})
            corner_ids = ordered_unique(c[i] for f in local_faces.values() for i in f)
            if not corner_ids:
                continue
            structural_nodes.update(corner_ids)
            center = tuple(sum(xyz[n][j] for n in corner_ids) / len(corner_ids) for j in range(3))
            seen = set()
            for local in local_faces.values():
                face = tuple(ordered_unique(c[i] for i in local))
                key = tuple(sorted(face))
                if len(face) < 3 or key in seen:
                    continue
                seen.add(key)
                members = list(face)
                if info.get("keep_tet10"):
                    for a, b, mid in ((0,1,4),(1,2,5),(2,0,6),(0,3,7),(1,3,8),(2,3,9)):
                        if c[a] in face and c[b] in face:
                            members.append(c[mid])
                if key in faces:
                    faces[key] = None  # Shared solid face is internal.
                else:
                    faces[key] = (face, center, tuple(ordered_unique(members)), info.get("pid",0))
        records = [v for v in faces.values() if v is not None] + shell_faces
        del faces
        self._exterior_pids = [r[3] for r in records]
        return [r[:3] for r in records], structural_nodes

    def assign_hourglasses(self):
        """Keep two stable shared IDs, independent of part count and ordering."""
        sections = {s["secid"]: s for s in self.sections}
        self.hourglasses = [dict(hgid=hgid, ihq=values[0], qm=values[1],
                                 qb=values[2], qw=values[3],
                                 title="HG_" + kind.upper(), rule=kind)
                            for hgid, kind in ((1, "shell"), (2, "solid"))
                            for values in [HOURGLASS_DEFAULTS[kind]]]
        for hg in self.hourglasses:
            for field in ("ihq", "qm", "ibq", "q1", "q2", "qb", "qw"):
                value = self.opt.get("hg_" + hg["rule"] + "_" + field)
                if value is not None:
                    hg[field] = value
        n = 0
        for p in self.parts:
            p["hgid"] = {"shell": 1, "solid": 2}.get(sections[p["secid"]].get("kind"), 0)
            n += bool(p["hgid"])
        self.log.ok("공통 *HOURGLASS 2개 생성: 쉘 HGID=1, 솔리드 HGID=2 · PART %d개 연결" % n)
        self.log.info("Hourglass는 준정적·저속 해석용 초기값이며, 실제 작동 여부는 요소 적분 공식에 따릅니다.")

    # ---------- v2.5 마운팅 노드 ----------
    def source_set_bindings(self, src):
        """(output title, instance prefix) pairs of one source NSET/ELSET."""
        part, nm = src["part"], src["name"]
        if part is None or (part is self.m.parts["__ROOT__"] and "" not in self.contexts):
            return [(nm, None)]
        return [((key + "_" if key else "") + nm, key)
                for key, ctx in self.contexts.items()
                if part is ctx["base"] or part is ctx["inst"]["part"]]

    def without_mount_nodes(self, ids, title=None):
        """Drop deleted mounting reference nodes from a node list."""
        if not self._mount_nodes:
            return ids
        kept = [n for n in ids if int(n) not in self._mount_nodes]
        if len(kept) != len(ids) and title is not None:
            if kept:
                self.log.warn('세트 "%s": 삭제한 마운팅 기준절점을 구성원에서 제외했습니다.' % title)
            else:
                self.log.info('세트 "%s": 마운팅 기준절점 1개뿐이라 출력하지 않습니다(→ %s).'
                              % (title, MOUNT_SET_NAME))
        return kept

    def _nodes_in_elements(self, nodes):
        """Subset of `nodes` referenced by any element connectivity."""
        used = set()
        if not nodes:
            return used
        for ctx in self.contexts.values():
            off = ctx["nOff"]
            for blk in ctx["P"].eblocks:
                conn = blk["conn"]
                if HAVE_NUMPY and isinstance(conn, np.ndarray):
                    # Only a few candidates: one linear scan each, no sort.
                    for n in nodes:
                        if n not in used and conn.size and (conn == n - off).any():
                            used.add(n)
                else:
                    for row in conn:
                        for v in row:
                            if int(v) + off in nodes:
                                used.add(int(v) + off)
        return used

    def detect_mounting(self):
        """Find a lone-node NSET that is the reference node of a COUPLING/MPC.

        Such a node only carries the mounting BC. The coupling/MPC is not
        converted, the reference node is removed from *NODE, and the coupled
        nodes become NSET_BC (SID 100001) carrying the original BC.
        """
        m = self.m
        if not (m.couplings or m.mpcs):
            return
        refs = {}                                 # node -> [("coupling"|"mpc", record)]
        for cp in m.couplings:
            rn = self.node_ref(cp["ref"]) if cp["ref"] else None
            if rn and len(set(rn)) == 1:
                refs.setdefault(int(rn[0]), []).append(("coupling", cp))
        for mp in m.mpcs:
            if mp["type"] not in ("BEAM", "TIE", "PIN", "LINK"):
                continue
            mi = self.node_ref(mp["b"])
            if mi and len(set(mi)) == 1:
                refs.setdefault(int(mi[0]), []).append(("mpc", mp))
        if not refs:
            return
        found = {}                                # node -> [set title]
        for src in m.set_defs:
            if src["kind"] != "nsets":
                continue
            for title, pref in self.source_set_bindings(src):
                ids = set(int(n) for n in self.resolve_ids("nsets", src["name"], pref))
                if len(ids) == 1:
                    node = next(iter(ids))
                    if node in refs:
                        found.setdefault(node, []).append(title)
        if not found:
            return
        # A BC is not required: a lone-node reference set is a mounting.
        # Several candidates -> prefer names containing MOUNT (v2.6).
        if len(found) > 1:
            named = {n: v for n, v in found.items()
                     if any("MOUNT" in name_key(x) for x in v)}
            if named:
                for node in [n for n in found if n not in named]:
                    self.log.info('1노드 기준절점 세트 %s: 이름에 MOUNT가 없어 마운팅에서 제외합니다.'
                                  % ", ".join(found[node]))
                found = named
        # Keep the node when anything else still needs it.
        blocked = self._nodes_in_elements(set(found))
        for eq in m.equations:
            for term in eq["terms"]:
                blocked.update(int(n) for n in (self.node_ref(term[0]) or []) if int(n) in found)
        for rb in m.rigid_bodies:
            if rb["ref"]:
                blocked.update(int(n) for n in (self.node_ref(rb["ref"]) or []) if int(n) in found)
        for node in sorted(blocked):
            self.log.warn('마운팅 후보 절점 %d(세트 %s)이 요소/EQUATION/RIGID BODY에서 쓰여 '
                          '삭제하지 않고 기존 변환을 유지합니다.' % (node, ", ".join(found[node])))
            found.pop(node)
        if not found:
            return
        for node, titles in found.items():
            self._mount_nodes.add(node)
            for kind, rec in refs[node]:
                (self._mount_couplings if kind == "coupling" else self._mount_mpcs).add(id(rec))
            self.log.info('마운팅 기준절점 %d (세트 %s): 연결된 COUPLING/MPC %d건을 변환하지 않고 '
                          '절점을 삭제합니다.' % (node, ", ".join(titles), len(refs[node])))
        if len(found) > 1:
            self.log.warn("마운팅 1노드 세트가 %d개입니다. 모든 종속 절점을 %s 하나로 묶습니다."
                          % (len(found), MOUNT_SET_NAME))

    def build_mounting_set(self):
        """Collect the coupled nodes of removed constraints into NSET_BC."""
        if not self._mount_nodes:
            return
        m = self.m
        ids = []
        for cp in m.couplings:
            if id(cp) not in self._mount_couplings:
                continue
            S = self.build_surf(cp["surf"])
            members = self.surf_nodes(S)
            if not members:
                self.log.warn('*COUPLING "%s"의 표면 "%s"에서 절점을 찾지 못했습니다.'
                              % (cp["name"], cp["surf"]))
            ids.extend(members)
            self.imap.append(("*COUPLING %s (mounting)" % cp["name"],
                              "삭제 → %s (SID %d)" % (MOUNT_SET_NAME, MOUNT_SET_ID)))
        n_mpc = 0
        for mp in m.mpcs:
            if id(mp) not in self._mount_mpcs:
                continue
            ids.extend(self.node_ref(mp["a"]) or [])
            n_mpc += 1
        if n_mpc:
            self.imap.append(("*MPC mounting (%d행)" % n_mpc,
                              "삭제 → %s (SID %d)" % (MOUNT_SET_NAME, MOUNT_SET_ID)))
        ids = [int(n) for n in ordered_unique(int(v) for v in ids)
               if int(n) not in self._mount_nodes and 0 < int(n) <= self.max_node]
        if not ids:
            self.log.warn("%s: 마운팅 COUPLING/MPC의 종속 절점이 없어 SET을 만들지 못했습니다."
                          % MOUNT_SET_NAME)
            return
        if name_key(MOUNT_SET_NAME) in {name_key(s["name"]) for s in self.set_output}:
            raise ValueError("SET 이름 %s가 원본에 이미 있습니다. 원본 이름을 변경하세요." % MOUNT_SET_NAME)
        if any(s.get("fixed_sid") == MOUNT_SET_ID for s in self.set_output):
            raise ValueError("SET ID %d가 이미 사용 중입니다." % MOUNT_SET_ID)
        self._mount_sid = self.append_set("node", dict(name=MOUNT_SET_NAME, ids=ids,
                                                       fixed_sid=MOUNT_SET_ID))
        self._node_sid[name_key(MOUNT_SET_NAME)] = self._mount_sid
        self.global_nsets[name_key(MOUNT_SET_NAME)] = self._mount_sid
        self.log.ok("%s (SID %d): 마운팅 COUPLING/MPC의 종속 절점 %d개"
                    % (MOUNT_SET_NAME, MOUNT_SET_ID, len(ids)))

    def emit_source_sets(self):
        """Emit first definitions in original interleaved order, including surfaces."""
        started = time.monotonic()
        last_report = started-5
        self.log.info("기존 SET/SURFACE 시작: %d개 정의 · 자동 끝단 SET %s" %
                      (len(self.m.set_defs), "ON" if self.opt.get("auto_sets", True) else "OFF"))
        for source_index, src in enumerate(self.m.set_defs):
            self._source_description = "%d/%d %s" % (source_index+1,len(self.m.set_defs),src["name"])
            now = time.monotonic()
            if now-last_report >= 2:
                self.log.info("SET/SURFACE 처리: %s · 누적 %.1f초" % (self._source_description,now-started))
                last_report = now
            self.post_stage(75+2*source_index/max(len(self.m.set_defs),1),
                            "SET/SURFACE %d/%d: %s" % (source_index+1,len(self.m.set_defs),src["name"]))
            self._set_source_order = (1 if src["kind"] == "surface" else 0, source_index)
            if src["kind"] == "surface":
                for ref, _ in self.surface_bindings(src["surface"]):
                    s = self.build_surf(ref)
                    if s and s["type"] == "seg" and s["segs"]:
                        self.seg_set_id(s)
                    elif s and s["type"] == "node":
                        ids = self.without_mount_nodes(s["ids"], ref)
                        if ids:
                            self.node_set_id(ref, ids)
                    else:
                        self.log.warn('표면 "%s": 변환할 유효한 세그먼트가 없습니다.' % ref)
                continue
            if not self.opt["sets"]:
                continue
            part, nm, kind = src["part"], src["name"], src["kind"]
            if part is None or (part is self.m.parts["__ROOT__"] and "" not in self.contexts):
                bindings = [(nm, None)]
            else:
                bindings = [((key + "_" if key else "") + nm, key)
                            for key, ctx in self.contexts.items()
                            if part is ctx["base"] or part is ctx["inst"]["part"]]
            for title, pref in bindings:
                self.post_stage(75+2*source_index/max(len(self.m.set_defs),1),
                                "SET %d/%d: %s" % (source_index+1,len(self.m.set_defs),title))
                ids = self.resolve_ids(kind, nm, pref)
                if not ids:
                    self.log.warn('세트 "%s"의 구성원을 찾지 못했습니다.' % title)
                    continue
                if kind == "nsets":
                    ids = self.without_mount_nodes(ids, title)
                    if not ids:
                        continue
                    sid = self.node_set_id(title, ids)
                    alias = ((pref + ".") if pref else "") + nm
                    self.global_nsets[alias] = sid
                    self.global_nsets.setdefault(nm, sid)
                else:
                    groups = self.element_set_groups(ids)
                    if "solid" in groups and "shell" in groups:
                        pids = self.part_ids_for_elements(ids)
                        key = ("part", title)
                        if key in self._element_sid:
                            existing = self._element_sid[key]
                            self.mark_source_set(existing)
                            existing["ids"] = ordered_unique(existing["ids"] + pids)
                        else:
                            record = dict(name=title, ids=pids)
                            self.append_set("part", record)
                            self._element_sid[key] = record
                        if not hasattr(self, "_part_element_counts"):
                            counts = {}
                            for values in self._part_pid_blocks.values():
                                if HAVE_NUMPY:
                                    keys, nums = np.unique(values, return_counts=True)
                                    for p, n in zip(keys, nums):
                                        counts[int(p)] = counts.get(int(p),0)+int(n)
                                else:
                                    for p in values:
                                        counts[p] = counts.get(p,0)+1
                            self._part_element_counts = counts
                        total = sum(self._part_element_counts.get(p,0) for p in pids)
                        selected = sum(len(v) for v in groups.values())
                        if total > selected:
                            self.log.warn('혼합 SET "%s": SET_PART 변환으로 선택 범위가 %d개에서 %d개 요소로 확대됩니다.' % (title,selected,total))
                        continue
                    for cat, members in groups.items():
                        title2 = title + ("_" + cat.upper() if len(groups) > 1 else "")
                        key = (cat, title2)
                        if key in self._element_sid:
                            existing = self._element_sid[key]
                            self.mark_source_set(existing)
                            existing["ids"] = ordered_unique(existing["ids"] + members)
                        else:
                            record = dict(cat=cat, name=title2, ids=members)
                            self.append_set("element", record)
                            self._element_sid[key] = record
        self._set_source_order = None
        self._source_description = ""
        self.log.ok("기존 SET/SURFACE 완료: %.2f초" % (time.monotonic()-started))

    def element_set_groups(self, ids):
        # Reuse the already-built per-instance EidIndex. No full-model copy,
        # concatenation, or global sort when the first ELSET is encountered.
        import bisect
        if not hasattr(self, "_element_ranges"):
            ranges = []
            for ctx in self.contexts.values():
                idx = ctx["index"]
                if not idx.total:
                    continue
                lo = int(idx.sorted[0]) if idx.np_mode else min(idx.d)
                hi = int(idx.sorted[-1]) if idx.np_mode else max(idx.d)
                codes = [{"solid":1,"shell":2,"beam":3}.get(
                    (classify(b["type"]) or {}).get("cat"),0) for b in ctx["P"].eblocks]
                ranges.append((lo+ctx["eOff"],hi+ctx["eOff"],ctx,codes))
            self._element_ranges = sorted(ranges,key=lambda r:r[0])
            self._element_starts = [r[0] for r in self._element_ranges]
        ranges = self._element_ranges
        names = {1:"solid",2:"shell",3:"beam"}
        if HAVE_NUMPY:
            src = np.asarray(ids,dtype=np.int64)
            cats = np.zeros(len(src),dtype=np.uint8)
            owners = np.searchsorted(self._element_starts,src,side="right")-1
            for owner in np.unique(owners):
                if owner < 0:
                    continue
                lo,hi,ctx,codes = ranges[int(owner)]
                rows = np.flatnonzero((owners == owner) & (src <= hi))
                if not len(rows):
                    continue
                idx = ctx["index"]
                if not idx.np_mode:
                    for row in rows:
                        loc = idx.one(int(src[row])-ctx["eOff"])
                        if loc is not None:
                            cats[row] = codes[loc[0]]
                    continue
                local = src[rows]-ctx["eOff"]
                pos = np.searchsorted(idx.sorted,local)
                valid = pos < idx.total
                rows,local,pos = rows[valid],local[valid],pos[valid]
                valid = idx.sorted[pos] == local
                rows,pos = rows[valid],pos[valid]
                block = np.searchsorted(idx.starts,idx.order[pos],side="right")-1
                cats[rows] = np.asarray(codes,dtype=np.uint8)[block]
            return {names[c]:src[cats==c].tolist() for c in ordered_unique(cats.tolist()) if c}
        groups = {}
        for eid in ids:
            owner = bisect.bisect_right(self._element_starts,eid)-1
            if owner < 0:
                continue
            lo,hi,ctx,codes = ranges[owner]
            if eid > hi:
                continue
            loc = ctx["index"].one(eid-ctx["eOff"])
            cat = codes[loc[0]] if loc is not None else 0
            if cat:
                groups.setdefault(names[cat],[]).append(eid)
        return groups

    def part_ids_for_elements(self, ids):
        if not HAVE_NUMPY:
            found = []
            for eid in ids:
                loc = self.element_location(eid)
                if loc:
                    ctx, bi, row = loc
                    arr = self._part_pid_blocks.get((ctx["eOff"], id(ctx["P"].eblocks[bi])))
                    if arr is not None and arr[row]:
                        found.append(int(arr[row]))
            return ordered_unique(found)
        src = np.asarray(ids,dtype=np.int64)
        pids = np.zeros(len(src),dtype=np.int64)
        owners = np.searchsorted(self._element_starts,src,side="right")-1
        for owner in np.unique(owners):
            if owner < 0:
                continue
            lo,hi,ctx,_ = self._element_ranges[int(owner)]
            rows = np.flatnonzero((owners == owner) & (src <= hi))
            idx = ctx["index"]
            if not idx.np_mode:
                for row in rows:
                    loc = idx.one(int(src[row])-ctx["eOff"])
                    if loc:
                        bi,k = loc
                        pids[row] = self._part_pid_blocks[(ctx["eOff"],id(ctx["P"].eblocks[bi]))][k]
                continue
            local = src[rows]-ctx["eOff"]
            pos = np.searchsorted(idx.sorted,local)
            valid = pos < idx.total
            rows,local,pos = rows[valid],local[valid],pos[valid]
            valid = idx.sorted[pos] == local
            rows,pos = rows[valid],pos[valid]
            flat = idx.order[pos]
            blocks = np.searchsorted(idx.starts,flat,side="right")-1
            for bi in np.unique(blocks):
                mask = blocks == bi
                arr = self._part_pid_blocks[(ctx["eOff"],id(ctx["P"].eblocks[int(bi)]))]
                pids[rows[mask]] = np.asarray(arr)[flat[mask]-idx.starts[int(bi)]]
        return ordered_unique(int(p) for p in pids if p)

    def element_location(self, eid):
        for ctx in self.contexts.values():
            loc = ctx["index"].one(eid - ctx["eOff"])
            if loc is not None:
                return ctx, loc[0], loc[1]
        return None

    def faces_for_nodes(self, ids):
        # Inspect only elements containing >=3 selected corner slots, in bounded
        # chunks. Do not construct the entire mesh's exterior face dictionary.
        selected = set(ids)
        if len(selected) < 3:
            return []
        previous = getattr(self, "_last_node_surface", None)
        if previous is not None and previous[0] == selected:
            return [face[:] for face in previous[1]]
        candidates = []
        def collect(eid):
            info = self.elem_info.get(eid)
            if info is None:
                return
            labels = ("SPOS",) if info["cat"] == "shell" else FACE.get(info["sub"], {})
            for label in labels:
                face = self.seg_of(eid,label)
                if face and all(n in selected for n in face):
                    candidates.append(face)

        if HAVE_NUMPY and self.contexts:
            selected_array = np.asarray(sorted(selected),dtype=np.int64)
            checked = 0
            for ctx in self.contexts.values():
                local_nodes = selected_array-ctx["nOff"]
                for blk in ctx["P"].eblocks:
                    cls = classify(blk["type"])
                    if not cls or cls["cat"] not in ("solid","shell"):
                        continue
                    corners = {"hex8":8,"hex20":8,"wedge6":6,"wedge15":6,
                               "pyramid5":5,"tet4":4,"tet10":4,
                               "quad4":4,"quad8":4,"tri3":3,"tri6":3}[cls["sub"]]
                    for start in range(0,len(blk["ids"]),50000):
                        conn = np.asarray(blk["conn"][start:start+50000],dtype=np.int64)[:,:corners]
                        pos = np.searchsorted(local_nodes,conn)
                        np.minimum(pos,len(local_nodes)-1,out=pos)
                        hits = (local_nodes[pos] == conn).sum(axis=1) >= 3
                        for row in np.flatnonzero(hits):
                            collect(int(blk["ids"][start+row])+ctx["eOff"])
                        checked += len(conn)
                        self.post_stage(getattr(self,"_last_post_pct",75),
                                        "NODE SURFACE: %d개 요소 검사 / 후보면 %d개" % (checked,len(candidates)))
        else:
            for i,(eid,info) in enumerate(self.elem_info.items()):
                if sum(n in selected for n in info["c"]) >= 3:
                    collect(eid)
                if i % 50000 == 0:
                    self.post_stage(getattr(self,"_last_post_pct",75),
                                    "NODE SURFACE: %d/%d 요소 검사" % (i,len(self.elem_info)))
        result = self.exterior_faces(candidates)
        # Only one cached selection, bounded by one query, not number of surfaces.
        self._last_node_surface = (selected,result)
        return [face[:] for face in result]

    @staticmethod
    def exterior_faces(candidates):
        count = {}
        for s in candidates:
            k = tuple(sorted(set(s)))
            count[k] = count.get(k, 0) + 1
        return [s for s in candidates if count[tuple(sorted(set(s)))] == 1]

    # ---------- 실행 ----------
    def run(self):
        m = self.m
        instances = list(m.instances)
        if not instances:
            root = m.parts["__ROOT__"]
            if root.nblocks:
                instances = [dict(name="", partName="__ROOT__", t=[0, 0, 0],
                                  rot=None, part=Part("L"), dataN=0)]
            else:
                for k, p in m.parts.items():
                    if k == "__ROOT__":
                        continue
                    instances.append(dict(name=p.name, partName=k, t=[0, 0, 0],
                                          rot=None, part=Part("L"), dataN=0))
                if instances:
                    self.log.warn("어셈블리 정의가 없어 파트를 원위치에 한 번씩 배치했습니다.")
        if not instances:
            self.log.err("절점을 찾지 못했습니다. Abaqus INP 파일이 맞는지 확인해 주세요.")
            return

        self.prepare_contexts(instances)
        self.detect_mounting()
        need_info = bool(m.surfaces or (self.opt["contact"] and m.rigid_bodies))
        need_coord = False
        if self.opt.get("auto_sets", True):
            need_coord = True
        if self.opt["beamNode"]:
            for t in m.el_types:
                c = classify(t)
                if c and c["cat"] == "beam" and not c["truss"]:
                    need_coord = True
                    break

        for inst in instances:
            b = m.parts.get(inst["partName"])
            if b is not None:
                self.total_items += b.n_nodes() + b.n_elems()

        for inst in instances:
            base = m.parts.get(inst["partName"])
            if base is None:
                self.log.warn('인스턴스 "%s"가 참조한 파트 %s를 찾을 수 없습니다.'
                              % (inst["name"], inst["partName"]))
                continue
            self.do_instance(inst, base, need_info, need_coord)

        for P in m.parts.values():
            for sec in P.sections:
                if not self.section_hits.get(id(sec)):
                    self.log.warn('단면 "%s"에 매칭되는 요소가 없습니다. ELSET 참조/요소 종류를 확인하세요.' % sec["elset"])
        self.post_stage(75, "기존 SET / SURFACE 변환")
        self.emit_source_sets()
        self.build_mounting_set()
        self.assign_hourglasses()

        if self.opt["contact"]:
            self.post_stage(78, "접촉 / 구속 변환")
            self.do_interactions()
        if self.opt["bc"]:
            self.do_boundaries()
        self.finalize_set_order()
        if self.opt.get("auto_sets", True):
            self.post_stage(80, "자동 SET 생성 시작")
            self.add_automatic_sets()
        if any(s["sid"] == 900001 and s["kind"] == "part" for s in self.set_output):
            if m.general_contact:
                self.log.warn("원본 General Contact는 선택한 ELSET_ALL 접촉으로 대체합니다. 제외 조건은 옮기지 않습니다.")
            self.contacts.append(dict(cid=max([c["cid"] for c in self.contacts] or [0])+1,
                kind=self.opt.get("all_contact", "ERODING_SINGLE_SURFACE")+"_ID",
                title="ELSET_ALL_CONTACT", whole=True,
                ssid=900001, msid=0, sstyp=2, mstyp=0,
                fs=self.opt.get("mu", .2), fd=self.opt.get("mu", .2)))
            self.log.ok("전체 접촉 추가: %s → ELSET_ALL (900001)" % self.contacts[-1]["kind"])
        self.finalize_nrb_ids()

        if m.unsupported:
            items = sorted(m.unsupported.items(), key=lambda kv: -kv[1])[:14]
            self.log.warn("변환하지 않은 키워드: "
                          + ", ".join("*%s(%d)" % (k, v) for k, v in items)
                          + (" 외" if len(m.unsupported) > 14 else ""))

    # ---------- 인스턴스 ----------
    def do_instance(self, inst, base, need_info, need_coord):
        ctx = self.contexts[name_key(inst["name"])]
        P = ctx["P"]
        opt = self.opt
        n_off, e_off = ctx["nOff"], ctx["eOff"]

        # ----- 절점 -----
        tr = make_transform(inst)
        fnode = self._tmp("node")
        for ids, xyz in P.nblocks:
            if tr is not None:
                xyz = tr(xyz)
            self.counts["node"] += self.write_nodes(fnode, ids, xyz, n_off, need_coord)
            self._tick(len(ids), "절점 %s" % f"{self.counts['node']:,}")

        # ----- 단면 -> PART (part / instance / assembly references) -----
        eid_index = ctx["index"]
        pid_all = _zeros_int(eid_index.total)
        sec_of_pid = {}
        root = self.m.parts["__ROOT__"]
        sections = [(sec, name_key(inst["name"])) for sec in P.sections]
        if base is not root:
            sections.extend((sec, None) for sec in root.sections)
        for sec, pref in sections:
            eids = self.resolve_ids("elsets", sec["elset"], pref)
            gi = eid_index.positions([e - e_off for e in eids])
            if gi is None or not len(gi):
                continue
            # A source ELSET can span several blocks/formulations. Select
            # compatible elements from every block, not just its first ID.
            wanted = ("shell" if sec["type"] in ("SHELL SECTION", "SHELL GENERAL SECTION", "MEMBRANE SECTION")
                      else "beam" if sec["type"] in ("BEAM SECTION", "BEAM GENERAL SECTION", "TRUSS SECTION")
                      else "solid")
            classes, hit_all = [], []
            for bi, blk in enumerate(P.eblocks):
                cls = classify(blk["type"])
                if not cls or cls["cat"] != wanted:
                    continue
                start, end = eid_index.starts[bi], eid_index.starts[bi] + eid_index.sizes[bi]
                hit = gi[(gi >= start) & (gi < end)] if HAVE_NUMPY and isinstance(gi, np.ndarray) else [g for g in gi if start <= g < end]
                if not len(hit):
                    continue
                classes.append(cls)
                hit_all.extend(int(g) for g in hit)
            if hit_all:
                self.sec_seq += 1
                self.pid_seq += 1
                secid, pid = self.sec_seq, self.pid_seq
                mid = self.get_mid(sec["material"]) if opt["mat"] else self.get_mid("")
                title = (inst["name"] + "_" if inst["name"] else "") + sec["elset"]
                S = self.make_property_section(secid, classes, sec, title)
                self.sections.append(S)
                sec_of_pid[pid] = S
                self.parts.append(dict(pid=pid, secid=secid, mid=mid, title=title))
                self.section_hits[id(sec)] = self.section_hits.get(id(sec), 0) + len(hit_all)
                if HAVE_NUMPY and isinstance(pid_all, np.ndarray):
                    pid_all[hit_all] = pid
                else:
                    for g in hit_all:
                        pid_all[g] = pid

        seg_eids = set()
        if need_info:
            for blk in P.eblocks:
                seg_eids.update(int(e) for e in blk["ids"]
                                if self._need_all_surface_elements or int(e) + e_off in self._needed_elements)

        # ----- 요소 -----
        fallback = {}
        pid_arrays = eid_index.split(pid_all)
        for bi, blk in enumerate(P.eblocks):
            self.write_block(blk, pid_arrays[bi], sec_of_pid, fallback,
                             n_off, e_off, seg_eids, P)
            tot = (self.counts["solid"] + self.counts["shell"]
                   + self.counts["beam"] + self.counts["mass"] + self.counts["disc"])
            self._tick(len(blk["ids"]), "요소 %s" % f"{tot:,}")

    def make_property_section(self, secid, classes, sec, title=None):
        """Select one compatible section for all shapes in a source property."""
        cat = classes[0]["cat"]
        cls = classes[0]
        if cat == "shell":
            quads = [c for c in classes if c["sub"] in ("quad4", "quad8")]
            # A triangle encountered first must not choose the quad formulation.
            cls = next((c for c in quads if c["red"]), quads[0] if quads else cls)
        S = self.make_section(secid, cls, sec)
        if cat == "solid":
            subs = {c["sub"] for c in classes}
            keep_tet10 = self.opt["tet10"] and subs == {"tet10"}
            forms = {self.make_section(secid, c, sec)["elform"] for c in classes}
            S["elform"] = 16 if keep_tet10 else (next(iter(forms)) if len(forms) == 1 else 1)
            if len(subs) > 1:
                S["elform"] = 1
            if self.opt["tet10"] and "tet10" in subs and not keep_tet10:
                self.log.warn('프로퍼티 "%s": 다른 솔리드 형상과 공통 PART를 유지하기 위해 '
                              'C3D10을 코너 4절점으로 축약합니다.' % sec["elset"])
        if cat == "solid" and self.opt.get("solid", "auto") != "auto":
            if {c["sub"] for c in classes} <= {"hex8", "hex20"}:
                S["elform"] = int(self.opt["solid"])
            else:
                self.log.info('프로퍼티 "%s": 요소 연결 호환성을 위해 ELFORM=%s 유지'
                              % (sec["elset"], S["elform"]))
        if (cat == "solid" and self.opt.get("neg_elform_names")
                and neg_elform_name(title or sec["elset"])):
            # Name rule overrides the global solid ELFORM choice (hexa only).
            if {c["sub"] for c in classes} <= {"hex8", "hex20"}:
                S["elform"] = -1
                self.log.info('프로퍼티 "%s": PAD/TA/ADHESIVE 이름 규칙으로 ELFORM=-1'
                              % (title or sec["elset"]))
            else:
                self.log.warn('프로퍼티 "%s": PAD/TA/ADHESIVE 이름이지만 육면체 외 요소가 있어 '
                              'ELFORM=%s 유지' % (title or sec["elset"], S["elform"]))
        if len({(c["sub"], c["red"]) for c in classes}) > 1:
            self.log.info('프로퍼티 "%s": 혼합 요소를 하나의 PART/SECTION(ELFORM=%s)에 연결합니다.'
                          % (sec["elset"], S.get("elform", "-")))
        return S

    def make_section(self, secid, cls, sec):
        opt = self.opt
        S = dict(secid=secid, cat=cls["cat"])
        if cls["cat"] == "solid":
            S["kind"] = "solid"
            if cls["sub"] == "tet10" and opt["tet10"]:
                S["elform"] = 16
            elif cls["sub"] in ("tet4", "tet10", "pyramid5", "wedge6", "wedge15"):
                S["elform"] = 1
            else:
                S["elform"] = 1 if cls["red"] else 2
        elif cls["cat"] == "shell":
            S["kind"] = "shell"
            if opt["shell"] == "auto":
                S["elform"] = 2 if cls["red"] else 16
            else:
                S["elform"] = int(opt["shell"])
            th = 0.0
            if sec["data"] and sec["data"][0]:
                try:
                    th = float(sec["data"][0][0])
                except (ValueError, IndexError):
                    th = 0.0
            if not th:
                th = 1.0
                self.log.warn('쉘 단면 "%s" 두께를 못 읽어 1.0으로 넣었습니다.' % sec["elset"])
            S["t"] = th
            nip = 5
            try:
                if sec["data"] and len(sec["data"][0]) > 1 and sec["data"][0][1]:
                    nip = int(float(sec["data"][0][1])) or 5
            except ValueError:
                pass
            S["nip"] = nip
        elif cls["cat"] == "beam":
            S["kind"] = "beam"
            S["truss"] = cls["truss"]
            S["elform"] = 3 if cls["truss"] else 1
            dims = []
            if sec["data"]:
                for x in sec["data"][0]:
                    try:
                        dims.append(float(x))
                    except ValueError:
                        pass
            S["shape"] = sec["shape"]
            n1 = []
            if len(sec["data"]) > 1:
                for x in sec["data"][1]:
                    try:
                        n1.append(float(x))
                    except ValueError:
                        pass
            S["n1"] = n1[:3] if len(n1) >= 3 else None
            if sec["shape"] == "CIRC" and dims:
                S["a"] = math.pi * dims[0] ** 2
                S["d1"] = 2 * dims[0]
                S["d2"] = 0.0
            elif sec["shape"] == "RECT" and len(dims) >= 2:
                S["a"] = dims[0] * dims[1]
                S["d1"], S["d2"] = dims[0], dims[1]
            else:
                S["a"] = dims[0] if dims else 1.0
                S["d1"] = math.sqrt(abs(S["a"])) or 1.0
                S["d2"] = S["d1"]
                if not sec["shape"]:
                    self.log.warn('보 단면 "%s" 형상을 해석하지 못해 단면적을 근사했습니다.'
                                  % sec["elset"])
        return S

    def fallback_pid(self, cat, fallback, sec_of_pid):
        if cat in fallback:
            return fallback[cat]
        self.sec_seq += 1
        self.pid_seq += 1
        secid, pid = self.sec_seq, self.pid_seq
        mid = self.get_mid("")
        S = dict(secid=secid, cat=cat)
        if cat == "solid":
            S.update(kind="solid", elform=1)
        elif cat == "shell":
            S.update(kind="shell", elform=2 if self.opt["shell"] == "auto"
                     else int(self.opt["shell"]), t=1.0, nip=5)
        elif cat == "beam":
            S.update(kind="beam", elform=1, a=1.0, d1=1.0, d2=1.0, n1=None, truss=False)
        elif cat == "discrete":
            S.update(kind="discrete")
        self.sections.append(S)
        sec_of_pid[pid] = S
        self.parts.append(dict(pid=pid, secid=secid, mid=mid,
                               title="UNASSIGNED_" + cat.upper()))
        self.log.warn("단면이 지정되지 않은 %s 요소가 있어 임시 PART %d에 모았습니다."
                      % (cat, pid))
        fallback[cat] = pid
        return pid

    # ---------- 절점 쓰기 ----------
    def write_nodes(self, fh, ids, xyz, n_off, need_coord):
        """Write one node block; deleted mounting reference nodes are skipped."""
        if self._mount_nodes:
            if HAVE_NUMPY and isinstance(ids, np.ndarray):
                keep = ~np.isin(ids + n_off, np.fromiter(self._mount_nodes, np.int64))
                if not keep.all():
                    ids, xyz = ids[keep], np.asarray(xyz)[keep]
            else:
                keep = [k for k in range(len(ids)) if int(ids[k]) + n_off not in self._mount_nodes]
                if len(keep) != len(ids):
                    ids = [ids[k] for k in keep]
                    xyz = [xyz[k] for k in keep]
        if not len(ids):
            return 0
        if HAVE_NUMPY and isinstance(ids, np.ndarray):
            nid = ids + n_off
            step = 400000
            for s in range(0, nid.shape[0], step):
                sl = slice(s, min(s + step, nid.shape[0]))
                cols = [np_int_cols(nid[sl], 8),
                        np_f16_cols(xyz[sl, 0]),
                        np_f16_cols(xyz[sl, 1]),
                        np_f16_cols(xyz[sl, 2]),
                        np.full((sl.stop - sl.start, 16), 32, np.uint8)]
                cols[4][:, 7] = 48
                cols[4][:, 15] = 48
                fh.write(np_rows_to_bytes(cols))
            if need_coord:
                for k in range(nid.shape[0]):
                    self.node_coord[int(nid[k])] = (float(xyz[k, 0]), float(xyz[k, 1]),
                                                    float(xyz[k, 2]))
        else:
            out = []
            for k in range(len(ids)):
                n = int(ids[k]) + n_off
                p = xyz[k]
                out.append(i8(n) + f16(p[0]) + f16(p[1]) + f16(p[2]) + "       0       0")
                if need_coord:
                    self.node_coord[n] = (p[0], p[1], p[2])
            fh.write(("\n".join(out) + "\n").encode("latin-1"))
        return len(ids)

    def normalize_solid_conn(self, blk):
        """Normalize only recognizable collapsed-brick padding, before offsets.

        A zero placeholder must never become a seemingly real node after adding
        an instance offset. Missing base/corner nodes are errors, not padding.
        """
        cls = classify(blk["type"])
        sub, conn, ids = cls["sub"], blk["conn"], blk["ids"]
        required = {"hex20": 8, "wedge15": 6,
                    "tet10": 10 if self.opt["tet10"] else 4}.get(sub, cls["nn"])
        is_array = HAVE_NUMPY and isinstance(conn, np.ndarray)
        widths = {conn.shape[1]} if is_array else {len(row) for row in conn}
        if sub == "hex8" and widths == {5}:
            # Some preprocessors export a collapsed C3D8 using five entries.
            conn = (np.column_stack([conn] + [conn[:, 4]] * 3) if is_array
                    else [list(row) + [row[4]] * 3 for row in conn])
            widths = {8}
        if any(w < required for w in widths):
            k = 0 if is_array else next(k for k, row in enumerate(conn) if len(row) < required)
            raise ValueError("*ELEMENT %s EID=%s: 코너/필수 절점 %d개가 필요합니다."
                             % (blk["type"], int(ids[k]), required))
        # Only output corners are needed for higher-order shapes being reduced.
        conn = conn[:, :required] if is_array else [row[:required] for row in conn]
        if sub == "hex8":
            repaired = 0
            if is_array:
                candidates = np.flatnonzero((conn[:, 5:] == 0).any(axis=1))
                if len(candidates):
                    conn = conn.copy()
                for k in candidates:
                    row = conn[k]
                    if (all(x > 0 for x in row[:5]) and len(set(row[:5])) == 5
                            and all(x in (0, row[4]) for x in row[5:])):
                        conn[k, 5:] = row[4]
                        repaired += 1
            else:
                for row in conn:
                    if (0 in row[5:] and all(x > 0 for x in row[:5])
                            and len(set(row[:5])) == 5
                            and all(x in (0, row[4]) for x in row[5:])):
                        row[5:] = [row[4]] * 3
                        repaired += 1
            if repaired:
                self.log.info("피라미드형 C3D8 %d개: 빈 N6~N8을 apex N5로 연결했습니다." % repaired)
        # Check zero/negative IDs locally, before any instance offset is applied.
        if is_array:
            bad = conn <= 0
            if bad.any():
                k, j = np.unravel_index(bad.argmax(), bad.shape)
                raise ValueError("*ELEMENT %s EID=%s: invalid node id %s (N%d)."
                                 % (blk["type"], int(ids[k]), int(conn[k, j]), j + 1))
        else:
            for k, row in enumerate(conn):
                for j, value in enumerate(row):
                    if value <= 0:
                        raise ValueError("*ELEMENT %s EID=%s: invalid node id %s (N%d)."
                                         % (blk["type"], ids[k], value, j + 1))
        return conn

    def validate_solid_nodes(self, eid, cn, elem_type):
        """Reject unresolved node references with an actionable element ID."""
        if HAVE_NUMPY and isinstance(cn, np.ndarray):
            for start in range(0, len(eid), 200000):
                block = cn[start:start + 200000]
                bad = ~np.isin(block, self._solid_node_ids)
                if bad.any():
                    k, j = np.unravel_index(bad.argmax(), bad.shape)
                    raise ValueError("*ELEMENT %s EID=%s: invalid node id %s (N%d), *NODE 정의 없음."
                                     % (elem_type, int(eid[start + k]), int(block[k, j]), j + 1))
        else:
            for k, row in enumerate(cn):
                for j, value in enumerate(row):
                    if value not in self._solid_node_ids:
                        raise ValueError("*ELEMENT %s EID=%s: invalid node id %s (N%d), *NODE 정의 없음."
                                         % (elem_type, eid[k], value, j + 1))

    # ---------- 요소 블록 쓰기 ----------
    def write_block(self, blk, pid_arr, sec_of_pid, fallback, n_off, e_off,
                    seg_eids, P):
        t = blk["type"]
        cls = classify(t)
        ids = blk["ids"]
        conn = blk["conn"]
        n = len(ids)
        key = "%s|%s" % (t, cls["sub"] if cls else "?")
        self.type_count[key] = self.type_count.get(key, 0) + n
        if cls is None:
            return
        cat, sub = cls["cat"], cls["sub"]
        if cat == "solid":
            conn = self.normalize_solid_conn(blk)

        # PID 결정
        if cat in ("mass", "inertia"):
            pid_arr = _zeros_int(n)
        else:
            need_fb = _any_zero(pid_arr)
            if need_fb:
                fb = self.fallback_pid(cat, fallback, sec_of_pid)
                pid_arr = _fill_zero(pid_arr, fb)

        self._part_pid_blocks[(e_off, id(blk))] = pid_arr

        # 접촉면용 연결 정보
        if (seg_eids or self.opt.get("auto_sets", True)) and cat in ("solid", "shell"):
            for k in range(n):
                eid0 = int(ids[k])
                if eid0 in seg_eids or self.opt.get("auto_sets", True):
                    row = conn[k]
                    info = dict(
                        cat=cat, sub=sub,
                        pid=int(_at(pid_arr,k)),
                        keep_tet10=(sub == "tet10" and self.opt["tet10"] and
                                    sec_of_pid[int(_at(pid_arr, k))]["elform"] == 16),
                        c=[int(x) + n_off for x in row])
                    if eid0 in seg_eids:
                        self.elem_info[eid0 + e_off] = info
                    if self.opt.get("auto_sets", True):
                        self._auto_elem_info[eid0 + e_off] = info

        eid = _add(ids, e_off)
        cn = _add(conn, n_off)

        if cat == "solid":
            self.validate_solid_nodes(eid, cn, t)
            f = self._tmp("solid")
            if sub in ("hex8", "hex20"):
                cols = [0, 1, 2, 3, 4, 5, 6, 7]
            elif sub == "pyramid5":
                cols = [0, 1, 2, 3, 4, 4, 4, 4]
            elif sub in ("wedge6", "wedge15"):
                cols = [0, 1, 2, 2, 3, 4, 5, 5]
            elif sub == "tet4":
                cols = [0, 1, 2, 3, 3, 3, 3, 3]
            elif sub == "tet10":
                if self.opt["tet10"]:
                    self.write_tet10(eid, pid_arr, cn, sec_of_pid)
                    self.counts["solid"] += n
                    return
                cols = [0, 1, 2, 3, 3, 3, 3, 3]
            else:
                return
            self.write_ints(f, [eid, pid_arr] + [_col(cn, c) for c in cols], 8)
            self.counts["solid"] += n
        elif cat == "shell":
            f = self._tmp("shell")
            cols = [0, 1, 2, 3] if sub in ("quad4", "quad8") else [0, 1, 2, 2]
            self.write_ints(f, [eid, pid_arr] + [_col(cn, c) for c in cols], 8)
            self.counts["shell"] += n
        elif cat == "beam":
            self.write_beams(eid, pid_arr, cn, cls, sec_of_pid)
            self.counts["beam"] += n
        elif cat == "mass":
            self.write_mass(blk, eid, cn, P)
            self.counts["mass"] += n
        elif cat == "discrete":
            f = self._tmp("disc")
            out = []
            for k in range(n):
                out.append(i8(int(_at(eid, k))) + i8(int(_at(pid_arr, k)))
                           + i8(int(_at2(cn, k, 0))) + i8(int(_at2(cn, k, 1)))
                           + i8(0) + f16(1.0) + i8(0) + f16(0))
            f.write(("\n".join(out) + "\n").encode("latin-1"))
            self.counts["disc"] += n

    def write_ints(self, fh, cols, w):
        if HAVE_NUMPY and isinstance(cols[0], np.ndarray):
            n = cols[0].shape[0]
            step = 300000
            for s in range(0, n, step):
                sl = slice(s, min(s + step, n))
                fh.write(np_rows_to_bytes([np_int_cols(c[sl], w) for c in cols]))
        else:
            out = []
            for k in range(len(cols[0])):
                out.append("".join(str(int(c[k])).rjust(w) for c in cols))
            fh.write(("\n".join(out) + "\n").encode("latin-1"))

    def write_tet10(self, eid, pid, cn, sec_of_pid):
        f = self._tmp("tet10")
        out, linear = [], []
        for k in range(len(eid)):
            p = int(_at(pid, k))
            header = i8(int(_at(eid, k))) + i8(p)
            if sec_of_pid[p]["elform"] == 16:
                out.append(header)
                # Abaqus edge 3-1 is node 7; LS-DYNA puts it in slot 10.
                out.append("".join(i8(int(_at2(cn, k, j)))
                                   for j in (0, 1, 2, 3, 4, 5, 7, 8, 9, 6)))
            else:
                linear.append(header + "".join(i8(int(_at2(cn, k, j)))
                                               for j in (0, 1, 2, 3, 3, 3, 3, 3)))
        if out:
            f.write(("\n".join(out) + "\n").encode("latin-1"))
        if linear:
            self._tmp("solid").write(("\n".join(linear) + "\n").encode("latin-1"))

    def write_beams(self, eid, pid, cn, cls, sec_of_pid):
        f = self._tmp("beam")
        out = []
        orient = 0
        for k in range(len(eid)):
            n1 = int(_at2(cn, k, 0))
            n2 = int(_at2(cn, k, 1))
            n3 = 0
            S = sec_of_pid.get(int(_at(pid, k)))
            if (not cls["truss"]) and self.opt["beamNode"] and S and S.get("n1"):
                p1 = self.node_coord.get(n1)
                p2 = self.node_coord.get(n2)
                if p1 and p2:
                    L = math.dist(p1, p2) or 1.0
                    v = S["n1"]
                    vl = math.hypot(math.hypot(v[0], v[1]), v[2]) or 1.0
                    mx = (p1[0] + p2[0]) / 2 + v[0] / vl * L
                    my = (p1[1] + p2[1]) / 2 + v[1] / vl * L
                    mz = (p1[2] + p2[2]) / 2 + v[2] / vl * L
                    self.max_node += 1
                    n3 = self.max_node
                    self._tmp("node").write(
                        (i8(n3) + f16(mx) + f16(my) + f16(mz)
                         + "       0       0\n").encode("latin-1"))
                    self.counts["node"] += 1
                    self.node_coord[n3] = (mx, my, mz)
                    orient += 1
            out.append(i8(int(_at(eid, k))) + i8(int(_at(pid, k))) + i8(n1) + i8(n2)
                       + i8(n3) + "       0       0       0       0       2")
        f.write(("\n".join(out) + "\n").encode("latin-1"))
        if orient:
            self.log.ok("보 요소 방향절점 %d개를 생성했습니다." % orient)

    def write_mass(self, blk, eid, cn, P):
        f = self._tmp("mass")
        mass_sets = [(v, set(int(x) for x in self.resolve_set(P.elsets, en)))
                     for en, v in P.massvals.items()]
        out = []
        miss = 0
        for k in range(len(eid)):
            orig = int(_at(blk["ids"], k))
            mv = 0.0
            for v, s in mass_sets:
                if orig in s:
                    mv = v
                    break
            if not mv:
                miss += 1
            out.append(i8(int(_at(eid, k))) + i8(int(_at2(cn, k, 0))) + f16(mv) + i8(0))
        f.write(("\n".join(out) + "\n").encode("latin-1"))
        if miss:
            self.log.warn("질량 요소 %d개의 값을 찾지 못해 0으로 두었습니다." % miss)

    # ---------- 세트 ----------
    def look(self, kind, ref, pref=None):
        return self.resolve_ids(kind, ref, pref) or None

    def seg_of(self, eid, face):
        info = self.elem_info.get(eid)
        if not info:
            return None
        c = info["c"]
        if info["cat"] == "shell":
            if face not in ("SPOS", "SNEG", "S1", "S2"):
                return None
            if info["sub"] in ("quad4", "quad8"):
                s = [c[0], c[1], c[2], c[3]]
                if face in ("SNEG", "S2"):
                    s = [s[3], s[2], s[1], s[0]]
            else:
                s = [c[0], c[1], c[2], c[2]]
                if face in ("SNEG", "S2"):
                    s = [c[2], c[1], c[0], c[0]]
            return s
        tab = FACE.get(info["sub"])
        if not tab:
            return None
        idx = tab.get(face)
        if idx is None:
            return None
        try:
            s = [c[i] for i in idx]
        except IndexError:
            return None
        # A collapsed brick has triangular faces and may have a zero-area face.
        # Preserve face labels and orientation, but never emit line/point sets.
        s = ordered_unique(s)
        if len(s) < 3:
            return None
        if len(s) == 3:
            s.append(s[2])
        return s

    def find_surf_def(self, R):
        R = name_key(R)
        if R in self._surface_defs:
            return self._surface_defs[R]
        matches = [(d, pref) for ref, (d, pref) in self._surface_defs.items()
                   if d["name"] == R]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            self.log.warn('표면 "%s"가 여러 인스턴스에 있습니다. INSTANCE.SURFACE를 지정하세요.' % R)
        return None, None

    def build_surf(self, ref, depth=0, cache=None):
        cache = self._surf_cache if cache is None else cache
        R = name_key(ref)
        if R in cache:
            return cache[R]
        if depth > 32:
            raise ValueError("표면 순환 참조 또는 과도한 중첩: " + R)
        d, pref = self.find_surf_def(R)
        if d is None:
            ids = self.resolve_ids("nsets", R)
            return dict(type="node", ids=ids, name=R) if ids else None
        canonical = ((pref + ".") if pref else "") + d["name"]
        if canonical in cache:
            cache[R] = cache[canonical]
            return cache[R]
        if d["stype"] == "NODE":
            ids = []
            for r, _ in d["rows"]:
                ids.extend(self.resolve_ids("nsets", r, pref))
            result = dict(type="node", ids=ordered_unique(ids), name=canonical)
        elif d["stype"] == "ELEMENT":
            segs, automatic = [], []
            for row_index, (row, face) in enumerate(d["rows"]):
                if row_index % 10000 == 0:
                    self.post_stage(getattr(self, "_last_post_pct", 75),
                                    "SURFACE %s: 행 %d/%d" % (canonical,row_index,len(d["rows"])))
                es = self.resolve_ids("elsets", row, pref)
                if es:
                    missing = 0
                    for eid in es:
                        if face:
                            seg = self.seg_of(eid, face)
                            if seg:
                                segs.append(seg)
                            else:
                                missing += 1
                        else:
                            info = self.elem_info.get(eid)
                            if not info:
                                missing += 1
                                continue
                            faces = ["SPOS"] if info["cat"] == "shell" else FACE.get(info["sub"], {})
                            automatic.extend(g for f in faces for g in [self.seg_of(eid, f)] if g)
                    if missing:
                        self.log.warn('표면 "%s": %s / %s에서 %d개 면을 매칭하지 못했습니다.'
                                      % (canonical, row, face or "외부면", missing))
                else:
                    nested = ((pref + ".") if pref else "") + name_key(row)
                    if nested not in self._surface_defs:
                        nested = name_key(row)
                    if nested in self._surface_defs:
                        sub = self.build_surf(nested, depth + 1, cache)
                        if sub and sub["type"] == "seg":
                            segs.extend(sub["segs"])
                    else:
                        self.log.warn('표면 "%s"의 참조 "%s"를 찾지 못했습니다.' % (canonical, row))
            segs.extend(self.exterior_faces(automatic))
            result = dict(type="seg", segs=[list(g) for g in ordered_unique(tuple(g) for g in segs)], name=canonical)
        else:
            self.log.warn('표면 "%s"의 TYPE=%s는 메시 SEGMENT로 변환할 수 없습니다.' % (canonical, d["stype"]))
            result = None
        cache[R] = cache[canonical] = result
        return result

    def seg_set_id(self, s):
        key = name_key(s["name"])
        if key in self._seg_sid:
            sid = self._seg_sid[key]
            self.mark_source_set(self._sets_by_sid[sid])
            return sid
        sid = self.append_set("segment", dict(name=s["name"], segs=s["segs"]))
        self._seg_sid[key] = sid
        return sid

    def node_set_id(self, name, ids):
        key = name_key(name)
        ids = ordered_unique(ids)
        if key in self._node_sid:
            sid = self._node_sid[key]
            existing = self._sets_by_sid[sid]
            self.mark_source_set(existing)
            existing["ids"] = ordered_unique(existing["ids"] + ids)
            return sid
        sid = self.append_set("node", dict(name=name, ids=ids))
        self._node_sid[key] = sid
        self.global_nsets[key] = sid
        return sid

    @staticmethod
    def surf_nodes(s):
        if not s:
            return []
        if s["type"] == "node":
            return list(s["ids"])
        out = set()
        for g in s["segs"]:
            out.update(g)
        return ordered_unique(n for g in s["segs"] for n in g)

    def add_contact(self, kind, title, S, M, fs):
        c = dict(cid=len(self.contacts) + 1, kind=kind, title=title, fs=fs, fd=fs)
        if S["type"] == "node":
            c["ssid"] = self.node_set_id(S["name"], S["ids"])
            c["sstyp"] = 4
        else:
            c["ssid"] = self.seg_set_id(S)
            c["sstyp"] = 0
        if M:
            if M["type"] == "node":
                c["msid"] = self.node_set_id(M["name"], M["ids"])
                c["mstyp"] = 4
            else:
                c["msid"] = self.seg_set_id(M)
                c["mstyp"] = 0
        else:
            c["msid"] = 0
            c["mstyp"] = 0
        self.contacts.append(c)
        self.imap.append((title, "*CONTACT_" + kind))
        return c

    def node_ref(self, ref):
        R = str(ref or "").strip().upper()
        v = self.look("nsets", R)
        if v:
            return v
        if "." in R:
            pre, loc = R.split(".", 1)
            im = self.inst_maps.get(pre)
            if im:
                try:
                    return [int(loc) + im["nOff"]]
                except ValueError:
                    pass
        try:
            n = int(R)
        except ValueError:
            return None
        if len(self.inst_maps) == 1:
            off = list(self.inst_maps.values())[0]["nOff"]
            return [n + off]
        return [n]

    def add_nrb(self, title, ids, pnode=0):
        uniq = sorted({int(v) for v in ids if 0 < int(v) <= self.max_node})
        if len(uniq) < 2:
            return False
        nsid = self.node_set_id("NRB_" + title, uniq)
        # No other converted keyword refers to a CNRB by PID. Assign it once
        # all parts, sets, contacts and constraints have been collected.
        self.nrbs.append(dict(pid=0, nsid=nsid, pnode=pnode, title=title))
        return True

    def finalize_nrb_ids(self):
        """Give CNRBs a disjoint range based on actual output IDs, not counters.

        CNRB PID shares the PART namespace. A higher common bound also keeps
        its numeric IDs distinct from the other generated entity namespaces.
        Existing CNRB PIDs are excluded so repeated finalization is stable.
        NSID and PNODE remain explicit and do not depend on the assigned PID.
        """
        if not self.nrbs:
            return
        highest = max(self.max_node, self.max_elem, 0)
        for records, key in ((self.parts, "pid"), (self.sections, "secid"),
                             (self.mats, "mid"), (self.curves, "lcid"),
                             (self.nsets, "sid"), (self.esets, "sid"),
                             (self.segsets, "sid"), (self.set_output, "sid"), (self.hourglasses, "hgid"),
                             (self.contacts, "cid"), (self.interps, "icid"),
                             (self.lineq, "lcid")):
            highest = max(highest, max((int(r[key]) for r in records), default=0))
        last = highest + len(self.nrbs)
        if last > 9999999999:
            raise ValueError("CNRB PID를 위한 10자리 ID 공간이 부족합니다.")
        changed = False
        for i, rb in enumerate(self.nrbs, 1):
            pid = highest + i
            changed = changed or rb["pid"] != pid
            rb["pid"] = pid
        if changed:
            self.log.ok("CNRB PID %d개를 중복 없는 범위 %d~%d에 배정했습니다."
                        % (len(self.nrbs), highest + 1, last))

    def do_interactions(self):
        m = self.m
        opt = self.opt

        for cp in m.contact_pairs:
            inter = m.interactions.get(cp["interaction"])
            fs = inter["fs"] if (inter and inter["fs"] is not None) else opt["mu"]
            for sl, ma in cp["rows"]:
                S = self.build_surf(sl)
                M = self.build_surf(ma)
                if (not S or not M
                        or (S["type"] == "seg" and not S["segs"])
                        or (M["type"] == "seg" and not M["segs"])):
                    self.log.warn('접촉쌍 "%s / %s"의 표면을 만들지 못해 건너뜁니다.' % (sl, ma))
                    continue
                tied = cp["tied"] or cp["ctype"] == "TIED"
                if tied:
                    kind = ("TIED_NODES_TO_SURFACE_OFFSET_ID" if S["type"] == "node"
                            else "TIED_SURFACE_TO_SURFACE_OFFSET_ID")
                else:
                    kind = ("AUTOMATIC_NODES_TO_SURFACE_ID" if S["type"] == "node"
                            else "AUTOMATIC_SURFACE_TO_SURFACE_ID")
                self.add_contact(kind, (cp["interaction"] or "CONTACT") + "_"
                                 + S["name"] + "_" + M["name"], S, M, 0.0 if tied else fs)

        for tie in m.ties:
            for sl, ma in tie["rows"]:
                S = self.build_surf(sl)
                M = self.build_surf(ma)
                if not S or not M:
                    self.log.warn('*TIE "%s"의 표면을 찾지 못했습니다.' % tie["name"])
                    continue
                kind = ("TIED_NODES_TO_SURFACE_OFFSET_ID" if S["type"] == "node"
                        else "TIED_SURFACE_TO_SURFACE_OFFSET_ID")
                self.add_contact(kind, tie["name"], S, M, 0.0)

        if m.general_contact and not opt.get("auto_sets", True):
            self.contacts.append(dict(cid=len(self.contacts) + 1,
                                      kind="AUTOMATIC_SINGLE_SURFACE_ID",
                                      title="GENERAL_CONTACT", whole=True, ssid=0, msid=0,
                                      sstyp=2, mstyp=0, fs=opt["mu"], fd=opt["mu"]))
            self.imap.append(("*CONTACT (general contact)",
                              "*CONTACT_AUTOMATIC_SINGLE_SURFACE"))
            self.log.warn("일반 접촉은 전체 파트 단일 표면 접촉 하나로 대체했습니다. "
                          "제외 조건은 옮기지 않았습니다.")

        # MPC
        if m.mpcs:
            groups = {}
            for mp in m.mpcs:
                if id(mp) in self._mount_mpcs:
                    continue
                if mp["type"] not in ("BEAM", "TIE", "PIN", "LINK"):
                    self.log.warn("*MPC %s 형식은 변환하지 않았습니다." % mp["type"])
                    continue
                k = mp["type"] + "|" + str(mp["b"]).upper()
                groups.setdefault(k, dict(type=mp["type"], master=mp["b"], slaves=[]))
                groups[k]["slaves"].append(mp["a"])
            n = 0
            for g in groups.values():
                mi = self.node_ref(g["master"])
                if not mi:
                    self.log.warn('*MPC 기준절점 "%s"을 찾지 못했습니다.' % g["master"])
                    continue
                ids = list(mi)
                for s in g["slaves"]:
                    v = self.node_ref(s)
                    if v:
                        ids.extend(v)
                n += 1
                if self.add_nrb("MPC_%s_%d" % (g["type"], n), ids, mi[0]):
                    if g["type"] in ("PIN", "LINK"):
                        self.log.warn("*MPC %s는 병진만 구속하지만 강체 구속으로 바뀌어 "
                                      "회전까지 묶입니다." % g["type"])
            if n:
                self.imap.append(("*MPC (%d행)" % (len(m.mpcs) - len(self._mount_mpcs)),
                                  "*CONSTRAINED_NODAL_RIGID_BODY"))

        # COUPLING
        for cp in m.couplings:
            if id(cp) in self._mount_couplings:
                continue
            rn = self.node_ref(cp["ref"])
            S = self.build_surf(cp["surf"])
            ids = self.surf_nodes(S)
            if not rn or not ids:
                self.log.warn('*COUPLING "%s"의 기준절점 또는 표면을 찾지 못했습니다.'
                              % cp["name"])
                continue
            if cp["kind"] == "DISTRIBUTING":
                self.interps.append(dict(icid=len(self.interps) + 1, dnid=rn[0],
                                         nodes=ids, title=cp["name"]))
                self.imap.append(("*COUPLING %s (distributing)" % cp["name"],
                                  "*CONSTRAINED_INTERPOLATION"))
            else:
                if self.add_nrb("CPL_" + cp["name"].replace(" ", "_"), ids + rn, rn[0]):
                    self.imap.append(("*COUPLING %s (kinematic)" % cp["name"],
                                      "*CONSTRAINED_NODAL_RIGID_BODY"))

        # RIGID BODY
        for rb in m.rigid_bodies:
            ids = []
            if rb["elset"]:
                es = self.look("elsets", rb["elset"])
                if es:
                    for e in es:
                        info = self.elem_info.get(int(e))
                        if info:
                            ids.extend(info["c"])
            for k in ("pin", "tie"):
                if rb[k]:
                    v = self.look("nsets", rb[k])
                    if v:
                        ids.extend(v)
            rn = self.node_ref(rb["ref"]) if rb["ref"] else None
            if rn:
                ids.extend(rn)
            if self.add_nrb("RIGID_" + (rb["elset"] or rb["pin"] or rb["tie"] or "BODY"),
                            ids, rn[0] if rn else 0):
                self.imap.append(("*RIGID BODY " + (rb["elset"] or ""),
                                  "*CONSTRAINED_NODAL_RIGID_BODY"))
                self.log.info("*RIGID BODY를 절점 강체로 바꿨습니다. "
                              "파트 전체가 강체라면 *MAT_RIGID가 더 낫습니다.")

        # EQUATION
        for eq in m.equations:
            res = [(self.node_ref(t[0]), t[1], t[2]) for t in eq["terms"]]
            if any(r[0] is None for r in res):
                self.log.warn("*EQUATION의 절점 참조를 찾지 못해 건너뜁니다.")
                continue
            nmax = max(len(r[0]) for r in res)
            if any(len(r[0]) not in (1, nmax) for r in res):
                self.log.warn("*EQUATION의 절점집합 크기가 서로 달라 일부만 변환했습니다.")
            for k in range(nmax):
                terms = []
                for ids, dof, coef in res:
                    if len(ids) == 1:
                        terms.append((ids[0], dof, coef))
                    elif k < len(ids):
                        terms.append((ids[k], dof, coef))
                if len(terms) >= 2:
                    self.lineq.append(dict(lcid=len(self.lineq) + 1, terms=terms))
        if self.lineq:
            self.imap.append(("*EQUATION (%d개)" % len(self.lineq),
                              "*CONSTRAINED_LINEAR_GLOBAL"))

        if self.segsets:
            self.log.ok("표면 %d개를 *SET_SEGMENT로 만들었습니다." % len(self.segsets))
        if self.contacts:
            self.log.ok("접촉 정의 %d건을 변환했습니다." % len(self.contacts))
        nc = len(self.nrbs) + len(self.interps) + len(self.lineq)
        if nc:
            self.log.ok("구속 %d건을 변환했습니다." % nc)

    def do_boundaries(self):
        DOFMAP = {"ENCASTRE": [1, 1, 1, 1, 1, 1], "PINNED": [1, 1, 1, 0, 0, 0],
                  "XSYMM": [1, 0, 0, 0, 1, 1], "YSYMM": [0, 1, 0, 1, 0, 1],
                  "ZSYMM": [0, 0, 1, 1, 1, 0], "XASYMM": [0, 1, 1, 1, 0, 0],
                  "YASYMM": [1, 0, 1, 0, 1, 0], "ZASYMM": [1, 1, 0, 0, 0, 1]}
        agg = {}
        for b in self.m.boundaries:
            ids = self.resolve_ids("nsets", b["set"])
            sid = None
            if self._mount_nodes and any(int(n) in self._mount_nodes for n in ids):
                rest = [n for n in ids if int(n) not in self._mount_nodes]
                if not rest:
                    # Lone mounting reference node: its BC moves to NSET_BC.
                    if not self._mount_sid:
                        self.log.warn('경계조건 "%s": 마운팅 절점을 삭제했지만 %s가 없어 '
                                      '건너뜁니다.' % (b["set"], MOUNT_SET_NAME))
                        continue
                    sid = self._mount_sid
                    self._mount_bc_hits += 1
                    self.log.info('경계조건 "%s" → %s (SID %d)로 옮겼습니다.'
                                  % (b["set"], MOUNT_SET_NAME, MOUNT_SET_ID))
                else:
                    self.log.warn('경계조건 "%s": 삭제한 마운팅 기준절점은 제외합니다.' % b["set"])
                    ids = rest
            if sid is None:
                sid = self.global_nsets.get(b["set"])
                if not sid and ids:
                    sid = self.node_set_id(b["set"], ids)
            if not sid:
                self.log.warn('경계조건이 참조한 절점집합 "%s"을 세트 목록에서 '
                              '찾지 못했습니다.' % b["set"])
                continue
            dof = agg.get(sid, [0] * 6)
            t = (b["f"][0] if b["f"] else "").upper()
            if t in DOFMAP:
                for i, v in enumerate(DOFMAP[t]):
                    if v:
                        dof[i] = 1
            elif b["type"] in DOFMAP:
                for i, v in enumerate(DOFMAP[b["type"]]):
                    if v:
                        dof[i] = 1
            else:
                try:
                    d1 = int(b["f"][0])
                    d2 = int(b["f"][1]) if len(b["f"]) > 1 and b["f"][1] else d1
                    mag = float(b["f"][2]) if len(b["f"]) > 2 and b["f"][2] else 0.0
                    for d in range(d1, min(d2, 6) + 1):
                        dof[d - 1] = 1
                    if mag:
                        self.log.warn('"%s"의 강제변위(%g)는 SPC로 옮길 수 없어 '
                                      '고정 조건으로만 넣었습니다.' % (b["set"], mag))
                except (ValueError, IndexError):
                    pass
            agg[sid] = dof
        for sid, dof in agg.items():
            self.spcs.append(dict(sid=sid, dof=dof))
        if self._mount_sid and not self._mount_bc_hits:
            self.log.info("%s (SID %d): 마운팅 경계조건이 없어 SPC 없이 SET만 출력합니다."
                          % (MOUNT_SET_NAME, MOUNT_SET_ID))
        if self.spcs:
            self.log.ok("경계조건 %d건을 *BOUNDARY_SPC_SET으로 변환했습니다." % len(self.spcs))


# ---------- 배열 헬퍼 (numpy / list 공용) ----------
def _amin(a):
    return a.min() if (HAVE_NUMPY and isinstance(a, np.ndarray)) else min(a)


def _amax(a):
    return a.max() if (HAVE_NUMPY and isinstance(a, np.ndarray)) else max(a)


def _zeros_int(n):
    return np.zeros(n, np.int64) if HAVE_NUMPY else [0] * n


def _any_zero(a):
    if HAVE_NUMPY and isinstance(a, np.ndarray):
        return bool((a == 0).any())
    return any(v == 0 for v in a)


def _fill_zero(a, v):
    if HAVE_NUMPY and isinstance(a, np.ndarray):
        a = a.copy()
        a[a == 0] = v
        return a
    return [v if x == 0 else x for x in a]


def _add(a, off):
    if not off:
        return a
    if HAVE_NUMPY and isinstance(a, np.ndarray):
        return a + off
    if a and isinstance(a[0], list):
        return [[x + off for x in r] for r in a]
    return [x + off for x in a]


def _col(conn, j):
    if HAVE_NUMPY and isinstance(conn, np.ndarray):
        return conn[:, j] if j < conn.shape[1] else conn[:, -1]
    return [r[j] if j < len(r) else r[-1] for r in conn]


def _at(a, k):
    return a[k]


def _at2(a, k, j):
    row = a[k]
    return row[j] if j < len(row) else row[-1]


def merge_parts(a, b):
    if b.empty():
        return a
    P = Part(a.name)
    P.nblocks = a.nblocks + b.nblocks
    P.eblocks = a.eblocks + b.eblocks
    P.nsets = dict(a.nsets)
    for nm, ids in b.nsets.items():
        P.nsets[nm] = P.nsets.get(nm, []) + ids
    P.elsets = dict(a.elsets)
    for nm, ids in b.elsets.items():
        P.elsets[nm] = P.elsets.get(nm, []) + ids
    P.sections = a.sections + b.sections
    P.massvals = dict(a.massvals)
    P.massvals.update(b.massvals)
    return P


class EidIndex:
    """요소 ID -> 전역 인덱스. numpy가 있으면 정렬+searchsorted로 처리한다."""

    def __init__(self, P):
        self.blocks = P.eblocks
        self.sizes = [len(b["ids"]) for b in P.eblocks]
        self.starts = []
        acc = 0
        for n in self.sizes:
            self.starts.append(acc)
            acc += n
        self.total = acc
        self.np_mode = (HAVE_NUMPY and P.eblocks
                        and isinstance(P.eblocks[0]["ids"], np.ndarray))
        if self.np_mode:
            allid = (P.eblocks[0]["ids"] if len(P.eblocks) == 1
                     else np.concatenate([b["ids"] for b in P.eblocks]))
            self.order = np.argsort(allid, kind="stable")
            self.sorted = allid[self.order]
        else:
            self.d = {}
            for bi, blk in enumerate(P.eblocks):
                st = self.starts[bi]
                for k, e in enumerate(blk["ids"]):
                    self.d[int(e)] = st + k

    def positions(self, eids):
        """요소 ID 목록 -> 전역 인덱스 배열(없는 것은 제외)"""
        if not len(eids) or not self.total:
            return None
        if self.np_mode:
            e = np.asarray(eids, np.int64)
            pos = np.searchsorted(self.sorted, e)
            np.clip(pos, 0, max(0, self.sorted.size - 1), out=pos)
            ok = self.sorted[pos] == e
            return self.order[pos[ok]]
        return [self.d[int(x)] for x in eids if int(x) in self.d]

    def one(self, eid):
        """전역 인덱스 -> (블록, 행). 없으면 None"""
        if self.np_mode:
            p = int(np.searchsorted(self.sorted, int(eid)))
            if p >= self.sorted.size or int(self.sorted[p]) != int(eid):
                return None
            g = int(self.order[p])
        else:
            g = self.d.get(int(eid))
            if g is None:
                return None
        for bi in range(len(self.sizes) - 1, -1, -1):
            if g >= self.starts[bi]:
                return (bi, g - self.starts[bi])
        return None

    def split(self, arr):
        """전역 배열 -> 블록별 조각"""
        return [arr[self.starts[bi]:self.starts[bi] + self.sizes[bi]]
                for bi in range(len(self.sizes))]


# ============================================================
# 출력
# ============================================================
def write_k(cv, opt, out_path, src_name, progress=None):
    # Also covers callers that modify the converted model before exporting it.
    cv.finalize_nrb_ids()
    UD = UNIT_DEFAULT[opt["unit"]]
    W = open(out_path, "wb")

    def put(s):
        W.write((s + "\n").encode("latin-1"))

    put("*KEYWORD")
    put("*TITLE")
    put("$#                                                                         title")
    put((cv.m.title or "converted model")[:80])
    put("$")
    put("$  Converted from Abaqus input deck: " + src_name.encode("utf-8").decode("latin-1"))
    put("$  Assumed unit system: " + UD["label"])
    put("$  Check materials, sections and contacts before running.")
    put("$")

    # CONTROL / DATABASE generation is intentionally disabled.

    for p in cv.parts:
        put("*PART")
        put("$#                                                                         title")
        put(p["title"][:80])
        put("$#     pid     secid       mid     eosid      hgid      grav    adpopt      tmid")
        put(i10(p["pid"]) + i10(p["secid"]) + i10(p["mid"]) + i10(0)
            + i10(p.get("hgid", 0)) + i10(0) * 3)

    for hg in cv.hourglasses:
        put("*HOURGLASS_TITLE")
        put(hg["title"][:80])
        put("$#    hgid       ihq        qm       ibq        q1        q2    qb/vdc        qw")
        put(i10(hg["hgid"]) + "".join(
            " " * 10 if hg.get(k) is None else
            (i10(hg[k]) if k in ("ihq", "ibq") else f10(hg[k]))
            for k in ("ihq", "qm", "ibq", "q1", "q2", "qb", "qw")))

    for s in cv.sections:
        k = s.get("kind")
        if k == "solid":
            put("*SECTION_SOLID")
            put("$#   secid    elform       aet")
            put(i10(s["secid"]) + i10(s["elform"]) + i10(0))
        elif k == "shell":
            put("*SECTION_SHELL")
            put("$#   secid    elform      shrf       nip     propt   qr/irid     icomp     setyp")
            put(i10(s["secid"]) + i10(s["elform"]) + f10(0.8333) + i10(s.get("nip", 5))
                + i10(1) + i10(0) + i10(0) + i10(1))
            put("$#      t1        t2        t3        t4      nloc     marea      idof    edgset")
            t = s["t"]
            put(f10(t) * 4 + f10(0) * 3 + i10(0))
        elif k == "beam":
            put("*SECTION_BEAM")
            put("$#   secid    elform      shrf   qr/irid       cst     scoor        nsm")
            put(i10(s["secid"]) + i10(s["elform"]) + f10(1.0) + f10(2.0)
                + i10(1 if s.get("shape") == "CIRC" else 0) + f10(0) + f10(0))
            if s["elform"] == 3:
                put("$#       a     rampt    stress")
                put(f10(s.get("a", 1)) + f10(0) + f10(0))
            else:
                put("$#     ts1       ts2       tt1       tt2     nsloc     ntloc")
                d1 = s.get("d1", 1) or 1
                d2 = 0.0 if s.get("shape") == "CIRC" else (s.get("d2") or d1)
                put(f10(d1) * 2 + f10(d2) * 2 + f10(0) * 2)
        elif k == "discrete":
            put("*SECTION_DISCRETE")
            put("$#   secid       dro        kd        v0        cl        fd")
            put(i10(s["secid"]) + i10(0) + f10(0) * 4)
            put("$#     cdl        tdl")
            put(f10(0) * 2)

    for mt in cv.mats:
        if mt["type"] == "foam57":
            put("*MAT_LOW_DENSITY_FOAM_TITLE")
            put(mt["name"][:80])
            put("$#     mid        ro         e      lcid        tc        hu      beta      damp")
            put(i10(mt["mid"]) + f10(mt["rho"]) + f10(mt["e"]) + i10(mt["lcid"])
                + f10(mt["tc"]) + f10(1) + f10(0) + f10(0))
            put("$#   shape      fail    bvflag        ed     beta1      kcon       ref")
            put(f10(1) + f10(0) * 6)
        elif mt["type"] == "plastic":
            put("*MAT_PIECEWISE_LINEAR_PLASTICITY_TITLE")
            put(mt["name"][:80])
            put("$#     mid        ro         e        pr      sigy      etan      fail      tdel")
            put(i10(mt["mid"]) + f10(mt["rho"]) + f10(mt["e"]) + f10(mt["nu"])
                + f10(mt["sigy"]) + f10(0) + f10(1e21) + f10(0))
            put("$#       c         p      lcss      lcsr        vp")
            put(f10(0) + f10(0) + i10(mt.get("lcss", 0)) + i10(0) + f10(0))
            put("$#    eps1      eps2      eps3      eps4      eps5      eps6      eps7      eps8")
            put(f10(0) * 8)
            put("$#     es1       es2       es3       es4       es5       es6       es7       es8")
            put(f10(0) * 8)
        else:
            put("*MAT_ELASTIC_TITLE")
            put(mt["name"][:80])
            put("$#     mid        ro         e        pr        da        db  not used")
            put(i10(mt["mid"]) + f10(mt["rho"]) + f10(mt["e"]) + f10(mt["nu"])
                + f10(0) * 2 + i10(0))

    for c in cv.curves:
        put("*DEFINE_CURVE_TITLE")
        put(c["name"][:80])
        put("$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint")
        put(i10(c["lcid"]) + i10(0) + f10(1) + f10(1) + f10(0) + f10(0) + i10(0) + i10(0))
        put("$#                a1                  o1")
        for x, y in c["pts"]:
            put(f20(x) + f20(y))

    mesh_bytes = sum(f.tell() for f in cv.tmp.values())
    copied_bytes = 0

    def dump(key, header):
        nonlocal copied_bytes
        f = cv.tmp.get(key)
        if not f:
            return
        f.flush()
        if f.tell() == 0:
            return
        for h in header:
            put(h)
        f.seek(0)
        while True:
            chunk = f.read(4 * 1024 * 1024)
            if not chunk:
                break
            W.write(chunk)
            copied_bytes += len(chunk)
            if progress:
                progress("write", 90+8*copied_bytes/max(mesh_bytes,1),
                         "메시 저장 %.1f / %.1f MB" % (copied_bytes/1048576,mesh_bytes/1048576))

    dump("node", ["*NODE",
                  "$#   nid               x               y               z      tc      rc"])
    dump("solid", ["*ELEMENT_SOLID",
                   "$#   eid     pid      n1      n2      n3      n4      n5      n6      n7      n8"])
    dump("tet10", ["*ELEMENT_SOLID", "$#   eid     pid", "$# next row: n1..n10"])
    dump("shell", ["*ELEMENT_SHELL",
                   "$#   eid     pid      n1      n2      n3      n4"])
    dump("beam", ["*ELEMENT_BEAM",
                  "$#   eid     pid      n1      n2      n3     rt1     rr1     rt2     rr2   local"])
    dump("mass", ["*ELEMENT_MASS", "$#   eid     nid            mass     pid"])
    dump("disc", ["*ELEMENT_DISCRETE",
                  "$#   eid     pid      n1      n2     vid           s       pf      offset"])

    def chunk_ids(ids):
        for i in range(0, len(ids), 8):
            put("".join(i10(v) for v in ids[i:i + 8]))

    # One source-ordered stream: do not regroup NSET/ELSET/SURFACE by type.
    for s in cv.set_output:
        if s["kind"] == "part":
            put("*SET_PART_LIST_TITLE")
            put(s["name"][:80])
            put("$#     sid")
            put(i10(s["sid"]))
            chunk_ids(s["ids"])
            continue
        if s["kind"] == "node":
            kw = "*SET_NODE_LIST_TITLE"
        elif s["kind"] == "segment":
            kw = "*SET_SEGMENT_TITLE"
        else:
            kw = ("*SET_SOLID_TITLE" if s["cat"] == "solid" else
                  "*SET_SHELL_LIST_TITLE" if s["cat"] == "shell" else "*SET_BEAM_TITLE")
        put(kw)
        put(s["name"][:80])
        put("$#     sid       da1       da2       da3       da4    solver")
        put(i10(s["sid"]) + f10(0) * 4 + "      MECH")
        if s["kind"] == "segment":
            put("$#      n1        n2        n3        n4        a1        a2        a3        a4")
            for g in s["segs"]:
                put("".join(i10(n) for n in g) + f10(0) * 4)
        else:
            chunk_ids(s["ids"])

    for b in cv.spcs:
        put("*BOUNDARY_SPC_SET")
        put("$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz")
        put(i10(b["sid"]) + i10(0) + "".join(i10(d) for d in b["dof"]))

    for r in cv.nrbs:
        put("*CONSTRAINED_NODAL_RIGID_BODY_TITLE")
        put(r["title"][:80])
        put("$#     pid       cid      nsid     pnode      iprt    drflag    rrflag")
        put(i10(r["pid"]) + i10(0) + i10(r["nsid"]) + i10(r["pnode"]) + i10(0) * 3)
    for p in cv.interps:
        put("*CONSTRAINED_INTERPOLATION")
        put("$#    icid      dnid      ddof      cidd      ityp     idnsw       fgm")
        put(i10(p["icid"]) + i10(p["dnid"]) + i10(123456) + i10(0) * 4)
        put("$#    inid      idof    twghtx    twghty    twghtz    rwghtx    rwghty    rwghtz")
        for n in p["nodes"]:
            put(i10(n) + i10(123) + f10(1) + f10(0) * 5)
    for q in cv.lineq:
        put("*CONSTRAINED_LINEAR_GLOBAL")
        put("$#    lcid")
        put(i10(q["lcid"]))
        put("$#     nid       dof      coef")
        for nid, dof, coef in q["terms"]:
            put(i10(nid) + i10(dof) + f10(coef))

    def contact_opt(c, k):
        """Whole-model contact: its own value first, then the per-contact value."""
        if c.get("whole") and opt.get("all_contact_" + k) is not None:
            return opt["all_contact_" + k]
        return opt.get("contact_" + k)

    for original in getattr(cv, "contacts", []):
        c = dict(original)
        for k in ("fs", "fd", "vdc", "sst", "mst"):
            if contact_opt(c, k) is not None:
                c[k] = contact_opt(c, k)
        put("*CONTACT_" + c["kind"])
        put("$#     cid                                                               heading")
        put(i10(c["cid"]) + c["title"][:70])
        put("$#    ssid      msid     sstyp     mstyp    sboxid    mboxid       spr       mpr")
        put(i10(c["ssid"]) + i10(c["msid"]) + i10(c["sstyp"]) + i10(c["mstyp"])
            + i10(0) * 2 + i10(1) * 2)
        put("$#      fs        fd        dc        vc       vdc    penchk        bt        dt")
        tied = c["kind"].startswith("TIED_")
        if tied:
            put(f10(c["fs"]) + f10(c["fd"]) + " " * 20
                + f10(c.get("vdc", 20)) + i10(0) + " " * 20)
        else:
            put(f10(c["fs"]) + f10(c["fd"]) + f10(0) * 2 + f10(c.get("vdc", 20)) + i10(0) + f10(0) + f10(1e20))
        put("$#     sfs       sfm       sst       mst      sfst      sfmt       fsf       vsf")
        if tied:
            put(" " * 20 + f10(c.get("sst", 0)) + f10(c.get("mst", 0)) + " " * 40)
        else:
            put(f10(1) * 2 + f10(c.get("sst", 0)) + f10(c.get("mst", 0)) + f10(1) * 4)
        if c["kind"].startswith("ERODING_"):
            # Required eroding card precedes optional contact card A.
            # Layout: ansys/pydyna auto/contact/contact_eroding_single_surface.py.
            put("$#    isym    erosop      iadj")
            put(i10(0) * 3)
        if not tied and any(contact_opt(c, k) is not None
                            for k in ("soft", "sbopt", "depth", "bsort")):
            put("$#    soft    sofscl    lcidab    maxpar     sbopt     depth     bsort    frcfrq")
            put("".join(" " * 10 if value is None else
                        (i10(value) if integer else f10(value))
                        for value, integer in (
                            (contact_opt(c, "soft") if contact_opt(c, "soft") is not None else 0, True),
                            (.1, False), (0, True), (1.025, False),
                            (contact_opt(c, "sbopt") if contact_opt(c, "sbopt") is not None else 2, True),
                            (contact_opt(c, "depth") if contact_opt(c, "depth") is not None else 2, True),
                            (contact_opt(c, "bsort"), True), (1, True))))

    put("*END")
    size = W.tell()
    W.close()
    for f in cv.tmp.values():
        try:
            f.close()
        except Exception:
            pass
    return size


# ============================================================
# 전체 파이프라인
# ============================================================
DEFAULT_OPT = dict(sets=True, mat=True, bc=True, ctrl=False, tet10=True, neg_elform_names=False,
                   beamNode=True, contact=True, mu=0.2, shell="auto", unit="mmts", auto_sets=True, solid="auto", all_contact="ERODING_SINGLE_SURFACE")


BOOL_DETAIL_KEYS = ("neg_elform_names",)


def bool_text(value):
    """Checkbutton variable text for a boolean detail setting."""
    return "1" if (value is True or str(value).strip().lower() in ("1", "true", "on", "yes")) else "0"
# SST/MST < 0: LS-DYNA uses |value| as the contact thickness itself.
NEGATIVE_DETAIL_KEYS = ("contact_bsort", "contact_sst", "contact_mst",
                        "all_contact_bsort", "all_contact_sst", "all_contact_mst")
CONTACT_FIELDS = ("fs", "fd", "vdc", "sst", "mst", "soft", "sbopt", "depth", "bsort")


def detail_defaults():
    result = dict(solid="auto", shell="auto", all_contact="ERODING_SINGLE_SURFACE",
                  neg_elform_names=False)
    # Blank FS/FD preserves each source interaction's friction coefficient.
    for k, value in dict(fs="", fd="", vdc=20, sst=0, mst=0,
                         soft="", sbopt="", depth="", bsort="").items():
        result["contact_"+k] = value
    # v2.6: whole-model contact; blank follows the per-contact value.
    for k in CONTACT_FIELDS:
        result["all_contact_"+k] = ""
    for kind, vals in HOURGLASS_DEFAULTS.items():
        defaults = dict(zip(("ihq", "qm", "qb", "qw"), vals))
        for k in ("ihq", "qm", "ibq", "q1", "q2", "qb", "qw"):
            result["hg_"+kind+"_"+k] = defaults.get(k) if defaults.get(k) is not None else ""
    return result


def save_detail_settings(path, values):
    values = parse_detail_settings(values)
    # Validate before touching an existing preset.
    with open(path, "w", encoding="utf-8") as stream:
        json.dump(dict(format="inp2k-settings", schema_version=1, settings=values),
                  stream, ensure_ascii=False, indent=2, allow_nan=False)
        stream.write("\n")


def load_detail_settings(path):
    with open(path, encoding="utf-8-sig") as stream:
        data = json.load(stream)
    if not isinstance(data, dict) or data.get("format") != "inp2k-settings" or data.get("schema_version") != 1:
        raise ValueError("INP2K 설정 JSON 형식/버전이 아닙니다.")
    return parse_detail_settings(data.get("settings"))


def parse_detail_settings(raw):
    """Validate before any output is opened. Blank fields preserve old behavior."""
    if not isinstance(raw, dict):
        raise ValueError("설정은 JSON 객체여야 합니다.")
    allowed = set(detail_defaults())
    if set(raw) - allowed:
        raise ValueError("알 수 없는 설정: " + ", ".join(sorted(set(raw)-allowed)))
    result = {}
    for key, text in raw.items():
        if key in BOOL_DETAIL_KEYS:
            if isinstance(text, bool):
                result[key] = text
                continue
            flag = str(text).strip().lower()
            if flag in ("1", "true", "on", "yes"):
                result[key] = True
            elif flag in ("", "0", "false", "off", "no"):
                result[key] = False
            else:
                raise ValueError(key + ": true/false 값을 입력하세요.")
            continue
        text = str(text).strip()
        if not text:
            continue
        if key == "all_contact":
            if text not in ("AUTOMATIC_SINGLE_SURFACE", "ERODING_SINGLE_SURFACE"):
                raise ValueError("전체 접촉 종류를 확인하세요.")
            result[key] = text
            continue
        if key in ("shell", "solid"):
            choices = ("auto", "2", "16") if key == "shell" else ("auto", "1", "2")
            if text not in choices:
                raise ValueError(key + ": 지원하지 않는 ELFORM")
            result[key] = text
            continue
        integer = key.rsplit("_", 1)[-1] in ("ihq", "ibq", "soft", "sbopt", "depth", "bsort")
        try:
            value = float(text)
            if not math.isfinite(value) or (integer and value != int(value)):
                raise ValueError()
            if value < 0 and key not in NEGATIVE_DETAIL_KEYS:
                raise ValueError()
            if key.endswith("contact_soft") and value not in (0, 1, 2):
                raise ValueError()
            if key.endswith("_ihq") and value not in range(0, 11):
                raise ValueError()
        except (ValueError, OverflowError):
            raise ValueError(key.upper() + ": 유효한 " + ("정수" if integer else "숫자") + "를 입력하세요.")
        result[key] = int(value) if integer else value
    return result


def convert_file(inp_path, out_path, opt, log, progress=None):
    """Keep diagnostic output independent of GUI repaint and preserve old decks."""
    path = os.path.abspath(out_path) + ".conversion.log"
    original_sink = log.sink
    try:
        diagnostic = open(path, "a", encoding="utf-8", buffering=1)
    except OSError as exc:
        log.warn("진단 로그를 저장할 수 없습니다: %s" % exc)
        return _convert_file_impl(inp_path,out_path,opt,log,progress)
    lock = threading.Lock()
    def sink(level, message):
        with lock:
            diagnostic.write("%s [%s] %s\n" % (time.strftime("%Y-%m-%d %H:%M:%S"),level,message))
        if original_sink:
            original_sink(level,message)
    log.sink = sink
    try:
        log.info("INP2K v%s 실행 · 자동 끝단 SET %s · 진단 로그: %s" %
                 (VERSION,"ON" if opt.get("auto_sets",True) else "OFF",path))
        return _convert_file_impl(inp_path,out_path,opt,log,progress)
    except Exception:
        import traceback
        log.err(traceback.format_exc())
        raise
    finally:
        log.sink = original_sink
        diagnostic.close()

def _convert_file_impl(inp_path, out_path, opt, log, progress=None):
    """progress(phase, pct, text) — pct 는 0~100 전체 진행률"""
    t0 = time.time()
    progress_lock = threading.Lock()
    latest = ["convert", 45.0, "", time.monotonic()]
    published = [0.0, None]

    def emit(phase, pct, text=""):
        with progress_lock:
            now = time.monotonic()
            latest[:] = [phase, pct, text, now]
            if progress and (now-published[0] >= .15 or phase != published[1] or phase == "done"):
                published[:] = [now,phase]
                progress(phase, pct, text)

    stop_heartbeat = threading.Event()

    def heartbeat():
        last_log = time.monotonic()
        while not stop_heartbeat.wait(1.0):
            with progress_lock:
                phase, pct, label, updated = latest
                elapsed = time.monotonic()-updated
                if progress and elapsed >= 1.0:
                    progress(phase, pct, "%s · 처리 중 %.0f초" % (label, elapsed))
            if time.monotonic()-last_log >= 5:
                source = getattr(cv,"_source_description","")
                log.info("처리 중 %.1f%% · %s · %s · 변환 경과 %.0f초" %
                         (pct,source,label,time.time()-t1))
                last_log = time.monotonic()

    emit("read", 0.0, "")
    parser = Parser(log)
    stats = read_deck(inp_path, parser, log,
                      lambda done, total: emit(
                          "read", 45.0 * done / max(total, 1),
                          "%.0f / %.0f MB" % (done / 1048576.0, total / 1048576.0)))
    model = parser.m
    t_read = time.time() - t0
    if stats["files"] > 1:
        log.ok("*INCLUDE %d개 파일을 병합했습니다." % (stats["files"] - 1))
    log.info("파트 %d개, 인스턴스 %d개, 재료 %d개를 읽었습니다."
             % (max(0, len(model.parts) - 1), len(model.instances), len(model.materials)))

    emit("convert", 45.0, "")
    t1 = time.time()
    cv = Converter(model, opt, log,
                   lambda done, total, label: emit(
                       "convert", 45.0 + 30.0 * min(done / max(total, 1), 1.0), label))
    cv.stage_progress = lambda pct, label: emit("convert", pct, label)
    pending_output = None
    pulse = threading.Thread(target=heartbeat, daemon=True)
    if pulse:
        pulse.start()
    try:
        cv.run()
        t_conv = time.time() - t1
        emit("write", 90.0, "결과 파일 저장")
        t2 = time.time()
        # An incomplete conversion must not overwrite a previously valid deck.
        out_dir = os.path.dirname(os.path.abspath(out_path))
        fd, pending_output = tempfile.mkstemp(prefix=".inp2k_", suffix=".tmp", dir=out_dir)
        os.close(fd)
        size = write_k(cv, opt, pending_output, os.path.basename(inp_path), emit)
        os.replace(pending_output, out_path)
        pending_output = None
    finally:
        stop_heartbeat.set()
        if pulse:
            pulse.join()
        for f in cv.tmp.values():
            f.close()
        if pending_output is not None:
            try:
                os.remove(pending_output)
            except OSError:
                pass
    t_write = time.time() - t2
    emit("done", 100.0, "")

    log.ok("변환 완료 · %.1f MB (%.1f초: 읽기 %.1f / 변환 %.1f / 쓰기 %.1f)"
           % (size / 1048576.0, time.time() - t0, t_read, t_conv, t_write))
    return dict(counts=cv.counts, type_count=cv.type_count, imap=cv.imap,
                n_part=len(cv.parts), n_mat=len(cv.mats), n_seg=len(cv.segsets),
                n_contact=len(getattr(cv, "contacts", [])),
                n_constr=len(cv.nrbs) + len(cv.interps) + len(cv.lineq),
                bytes=size, seconds=time.time() - t0, out=out_path)


# ============================================================
# v2.7: Shock include 생성 (기존 INP 변환과 독립, 표준 라이브러리만 사용)
# ============================================================
SHOCK_GRAVITY = 9.80665  # m/s^2; export uses mm and seconds.
SHOCK_LCID = 701
SHOCK_MOTION_ID = 700
SHOCK_SPC_ID = 702
SHOCK_POINTS = 601  # Total table points; central T..2T has N-2 points.
SHOCK_WAVEFORMS = (("half-sine", "Half-sine"),
                   ("triangular", "Triangular"),
                   ("rectangular", "Rectangular"))
SHOCK_DIRECTIONS = (("mx", "−X", 1, -1), ("px", "+X", 1, 1),
                    ("my", "−Y", 2, -1), ("py", "+Y", 2, 1),
                    ("mz", "−Z", 3, -1), ("pz", "+Z", 3, 1))


def build_shock_profile(g_value=25.0, duration_ms=15.0,
                        waveform="half-sine", direction="mx", point_count=SHOCK_POINTS):
    """Base table: 0 -> -V -> +V -> 0, with the shock pulse over T..2T.

    V = half the pulse integral. Pre/post segments are linear in velocity.
    SFO is applied separately. Times lie on the 0.00001 s export grid so
    five-decimal output cannot create duplicate time records.
    """
    def positive(value, label):
        try:
            number = float(value)
        except (ValueError, TypeError, OverflowError):
            raise ValueError("%s: 0보다 큰 숫자를 입력하세요." % label)
        if not math.isfinite(number) or number <= 0:
            raise ValueError("%s: 0보다 큰 유한한 숫자를 입력하세요." % label)
        return number

    g_value = positive(g_value, "가속도 (g)")
    duration_ms = positive(duration_ms, "펄스 시간 (ms)")
    try:
        points = int(str(point_count).strip())
    except (TypeError, ValueError, OverflowError):
        raise ValueError("데이터점 개수는 정수로 입력하세요.")
    if not 5 <= points <= 100001:
        raise ValueError("전체 데이터점 개수는 5~100001 사이의 정수로 입력하세요.")
    if waveform not in dict(SHOCK_WAVEFORMS):
        raise ValueError("지원하지 않는 Shock 파형: %s" % waveform)
    directions = {item[0]: item for item in SHOCK_DIRECTIONS}
    if direction not in directions:
        raise ValueError("Shock 방향은 mx, px, my, py, mz, pz 중 선택하세요.")
    _, direction_label, dof, sfo = directions[direction]
    if duration_ms > 1e12:
        raise ValueError("펄스 시간이 출력 가능한 범위를 벗어났습니다.")
    tick_value = duration_ms * 100.0
    ticks = round(tick_value)
    if ticks < 1 or abs(tick_value - ticks) > 1e-6:
        raise ValueError("시간 소수 5자리 출력을 위해 펄스 시간은 0.01 ms 단위로 입력하세요.")
    if points > ticks + 3:
        raise ValueError("시간 소수 5자리에서 중복 없이 가능한 최대 데이터점은 %d개입니다."
                         % (ticks + 3))
    duration_s = ticks / 100000.0
    amplitude = g_value * SHOCK_GRAVITY * 1000.0
    impulse = amplitude * duration_s
    factor = {"half-sine": 2.0 / math.pi, "triangular": 0.5, "rectangular": 1.0}[waveform]
    v_peak = impulse * (factor / 2.0)
    if not math.isfinite(v_peak) or v_peak < 0.005 or v_peak >= 1e16:
        raise ValueError("속도가 소수 2자리/20칸 출력 범위를 벗어났습니다. 가속도와 시간을 확인하세요.")

    # Only the central pulse is sampled. The solver linearly interpolates
    # the outer 0..T and 2T..3T segments from their endpoints.
    central_points = points - 2
    grid = [0] + [ticks + round(i * ticks / (central_points - 1))
                  for i in range(central_points)] + [3 * ticks]
    times, velocities, accelerations = [], [], []
    compensation_g = -v_peak / duration_s / (SHOCK_GRAVITY * 1000.0)
    for tick in grid:
        if tick < ticks:
            velocity = -v_peak * tick / ticks
            accel_g = compensation_g
        elif tick <= 2 * ticks:
            ratio = (tick - ticks) / ticks
            if waveform == "half-sine":
                velocity = -v_peak * math.cos(math.pi * ratio)
                accel_g = g_value * math.sin(math.pi * ratio)
            elif waveform == "triangular":
                fraction = ratio ** 2 if ratio <= 0.5 else 0.5 - (1 - ratio) ** 2
                velocity = -v_peak + impulse * fraction
                accel_g = g_value * 2 * min(ratio, 1 - ratio)
            else:
                velocity = -v_peak + impulse * ratio
                accel_g = g_value
        else:
            velocity = v_peak * (3 * ticks - tick) / ticks
            accel_g = compensation_g
        times.append(tick / 100000.0)
        velocities.append(0.0 if abs(velocity) < 1e-12 else velocity)
        accelerations.append(accel_g)
    # Exact endpoint values, independent of trigonometric roundoff.
    velocities[0] = velocities[-1] = 0.0
    condition = "%sg%sms" % (format(g_value, ".12g"), format(duration_ms, ".12g"))
    wave_suffix = "" if waveform == "half-sine" else "_" + waveform
    stem = "Velo_shock_profile_" + condition + wave_suffix
    spc = [1] * 6
    spc[dof - 1] = 0
    return dict(g=g_value, duration_ms=duration_ms, duration_s=duration_s,
                end_s=times[-1], waveform=waveform, direction=direction,
                direction_label=direction_label, dof=dof, sfo=sfo, spc=spc,
                nsid=MOUNT_SET_ID, lcid=(701 if sfo < 0 else 702), point_count=points,
                v_peak=v_peak, compensation_g=compensation_g,
                times=times, velocities=velocities, accelerations_g=accelerations,
                filename=str(701 if sfo < 0 else 702) + "_" + stem + "_" + direction + ".k",
                title=stem + ("_minus" if sfo < 0 else "_plus"))


def render_shock_keyword(profile):
    """Render a boundary/curve include; the parent deck must define NSET_BC.

    Field layouts checked against Ansys PyDYNA's auto/boundary/
    boundary_prescribed_motion_set.py, boundary_spc_set.py and
    auto/define/define_curve.py (https://github.com/ansys/pydyna).
    ``_ID`` adds a 10-column ID and 70-column heading before the data card.
    """
    p = profile
    lines = ["*KEYWORD",
             "*BOUNDARY_PRESCRIBED_MOTION_SET_ID",
             "$#      id heading",
             i10(SHOCK_MOTION_ID) + ("Shock_motion_" + p["direction"]),
             "$#    nsid       dof       vad      lcid        sf       vid     death     birth",
             i10(p["nsid"]) + i10(p["dof"]) + i10(0) + i10(p["lcid"]) +
             f10(1.0) + i10(0) + f10(0.0) + f10(0.0),
             "*BOUNDARY_SPC_SET_ID",
             "$#      id heading",
             i10(SHOCK_SPC_ID) + ("Shock_spc_" + p["direction"]),
             "$#    nsid       cid      dofx      dofy      dofz     dofrx     dofry     dofrz",
             i10(p["nsid"]) + i10(0) + "".join(i10(v) for v in p["spc"]),
             "*DEFINE_CURVE_TITLE",
             p["title"][:80],
             "$#    lcid      sidr       sfa       sfo      offa      offo    dattyp     lcint",
             i10(p["lcid"]) + i10(0) + f10(1.0) + f10(p["sfo"]) +
             f10(0.0) + f10(0.0) + i10(0) + i10(0),
             "$#          time (s)     velocity (mm/s)"]
    for t, v in zip(p["times"], p["velocities"]):
        # Normalize negative zero and never switch the table to exponent notation.
        v = 0.0 if abs(v) < 0.005 else v
        time_text, velocity_text = "%20.5f" % t, "%20.2f" % v
        if len(time_text) > 20 or len(velocity_text) > 20:
            raise ValueError("Shock 표 값이 20칸 고정 필드 범위를 벗어났습니다.")
        lines.append(time_text + velocity_text)
    lines.append("*END")
    return "\n".join(lines) + "\n"


def write_shock_k(out_path, g_value=25.0, duration_ms=15.0,
                  waveform="half-sine", direction="mx", point_count=SHOCK_POINTS):
    """Validate fully, then atomically write the Shock file without partial output."""
    profile = build_shock_profile(g_value, duration_ms, waveform, direction, point_count)
    content = render_shock_keyword(profile)
    out_path = os.path.abspath(os.fspath(out_path))
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="ascii", newline="\n",
                dir=os.path.dirname(out_path), prefix=".inp2k-shock-",
                suffix=".tmp", delete=False) as stream:
            temporary = stream.name
            stream.write(content)
        os.replace(temporary, out_path)
        temporary = None
    finally:
        if temporary is not None:
            os.unlink(temporary)
    profile["out"] = out_path
    return profile


def write_shock_files(output_dir, g_value=25.0, duration_ms=15.0,
                       waveform="half-sine", direction="mx", point_count=SHOCK_POINTS,
                       all_directions=False, overwrite=False):
    """Preflight every target; return per-file results for any write failures."""
    directory = os.path.expanduser(os.fspath(output_dir).strip())
    if not directory:
        raise ValueError("출력 폴더를 입력하거나 선택하세요.")
    directory = os.path.abspath(directory)
    directions = ("mx", "my", "mz", "px", "py", "pz") if all_directions else (direction,)
    profiles = [build_shock_profile(g_value, duration_ms, waveform, d, point_count) for d in directions]
    for profile in profiles:
        render_shock_keyword(profile)  # Validate formatting before writing anything.
    paths = [os.path.join(directory, profile["filename"]) for profile in profiles]
    conflicts = [path for path in paths if os.path.lexists(path)]
    if not overwrite and conflicts:
        raise FileExistsError("같은 이름의 파일이 있습니다. 다른 폴더를 지정하거나 덮어쓰기를 선택하세요: "
                              + ", ".join(os.path.basename(path) for path in conflicts))
    if any(os.path.isdir(path) for path in conflicts):
        raise IsADirectoryError("출력 파일과 같은 이름의 폴더가 있습니다.")
    os.makedirs(directory, exist_ok=True)
    written, failed = [], []
    for path, profile in zip(paths, profiles):
        try:
            written.append(write_shock_k(path, g_value, duration_ms, waveform,
                                        profile["direction"], point_count))
        except OSError as exc:
            failed.append(dict(path=path, error=str(exc)))
    return dict(written=written, failed=failed, directory=directory)


# ============================================================
# GUI
# ============================================================
PALETTE = dict(
    bg="#0F1115", card="#171A21", card2="#1D212A", line="#2A3039",
    text="#E6E9EF", dim="#8A93A3", faint="#5C6675",
    accent="#4F8CFF", accent_hi="#6BA0FF", accent_dim="#2B4A85",
    ok="#34D399", warn="#FBBF24", err="#F87171",
)


def _pick_font(cands, default, root=None):
    try:
        import tkinter.font as tkfont
        fams = set(f.lower() for f in tkfont.families(root=root))
        for c in cands:
            if c.lower() in fams:
                return c
    except Exception:
        pass
    try:
        return tkfont.nametofont(default, root=root).actual("family")
    except Exception:
        return default


def round_rect(cv, x1, y1, x2, y2, r, **kw):
    r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
    pts = [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
           x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]
    return cv.create_polygon(pts, smooth=True, splinesteps=18, **kw)


class RButton:
    """모서리가 둥근 평면 버튼"""

    def __init__(self, parent, text, command, kind="primary", w=132, h=38, font=None):
        P = PALETTE
        self.kind = kind
        self.command = command
        self.enabled = True
        bgp = parent.cget("bg")
        self.cv = tk.Canvas(parent, width=w, height=h, bg=bgp,
                            highlightthickness=0, bd=0, cursor="hand2")
        self.w, self.h = w, h
        self.shape = round_rect(self.cv, 1, 1, w - 1, h - 1, 9, fill="", outline="")
        self.label = self.cv.create_text(w / 2, h / 2, text=text, font=font,
                                         fill=P["text"])
        self._paint(False)
        self.cv.bind("<Enter>", lambda e: self._paint(True))
        self.cv.bind("<Leave>", lambda e: self._paint(False))
        self.cv.bind("<Button-1>", self._click)

    def _paint(self, hover):
        P = PALETTE
        if not self.enabled:
            fill, out, fg = P["card2"], P["line"], P["faint"]
        elif self.kind == "primary":
            fill = P["accent_hi"] if hover else P["accent"]
            out, fg = fill, "#0B1220"
        else:
            fill = P["card2"] if hover else P["card"]
            out, fg = P["line"], P["text"]
        self.cv.itemconfig(self.shape, fill=fill, outline=out)
        self.cv.itemconfig(self.label, fill=fg)

    def _click(self, _e):
        if self.enabled and self.command:
            self.command()

    def config(self, text=None, enabled=None):
        if text is not None:
            self.cv.itemconfig(self.label, text=text)
        if enabled is not None:
            self.enabled = bool(enabled)
            self.cv.config(cursor="hand2" if self.enabled else "arrow")
            self._paint(False)

    def pack(self, **kw):
        self.cv.pack(**kw)
        return self

    def grid(self, **kw):
        self.cv.grid(**kw)
        return self


class Switch:
    """토글 스위치"""

    def __init__(self, parent, text, value=True, font=None, sub=None, subfont=None):
        P = PALETTE
        self.value = bool(value)
        self.fr = tk.Frame(parent, bg=parent.cget("bg"))
        self.cv = tk.Canvas(self.fr, width=40, height=22, bg=parent.cget("bg"),
                            highlightthickness=0, bd=0, cursor="hand2")
        self.track = round_rect(self.cv, 1, 3, 39, 21, 9, fill="", outline="")
        self.knob = self.cv.create_oval(0, 0, 0, 0, fill="#FFFFFF", outline="")
        self.cv.pack(side="left")
        box = tk.Frame(self.fr, bg=parent.cget("bg"))
        box.pack(side="left", padx=(10, 0))
        self.lb = tk.Label(box, text=text, bg=parent.cget("bg"), fg=P["text"],
                           font=font, anchor="w", cursor="hand2")
        self.lb.pack(anchor="w")
        if sub:
            tk.Label(box, text=sub, bg=parent.cget("bg"), fg=P["faint"],
                     font=subfont, anchor="w").pack(anchor="w")
        for wdg in (self.cv, self.lb):
            wdg.bind("<Button-1>", self.toggle)
        self._paint()

    def _paint(self):
        P = PALETTE
        self.cv.itemconfig(self.track,
                           fill=P["accent"] if self.value else P["card2"],
                           outline=P["accent"] if self.value else P["line"])
        x = 22 if self.value else 3
        self.cv.coords(self.knob, x, 5, x + 15, 19)
        self.cv.itemconfig(self.knob, fill="#FFFFFF" if self.value else P["faint"])

    def toggle(self, _e=None):
        self.value = not self.value
        self._paint()

    def get(self):
        return self.value

    def pack(self, **kw):
        self.fr.pack(**kw)
        return self

    def grid(self, **kw):
        self.fr.grid(**kw)
        return self


class Segmented:
    """선택 세그먼트 (콤보박스 대체)"""

    def __init__(self, parent, options, index=0, font=None, padx=13):
        P = PALETTE
        self.options = options
        self.index = index
        self.font = font
        self.fr = tk.Frame(parent, bg=P["card2"], highlightthickness=1,
                           highlightbackground=P["line"], bd=0)
        self.cells = []
        for i, (_val, lab) in enumerate(options):
            c = tk.Label(self.fr, text=lab, bg=P["card2"], fg=P["dim"],
                         font=font, padx=padx, pady=5, cursor="hand2")
            c.pack(side="left")
            c.bind("<Button-1>", lambda e, k=i: self.select(k))
            self.cells.append(c)
        self._paint()

    def _paint(self):
        P = PALETTE
        for i, c in enumerate(self.cells):
            on = (i == self.index)
            c.config(bg=P["accent"] if on else P["card2"],
                     fg="#0B1220" if on else P["dim"])

    def select(self, i):
        self.index = i
        self._paint()

    def get(self):
        return self.options[self.index][0]

    def pack(self, **kw):
        self.fr.pack(**kw)
        return self


class Bar:
    """둥근 진행 바"""

    def __init__(self, parent, h=8):
        P = PALETTE
        self.h = h
        self.cv = tk.Canvas(parent, height=h, bg=parent.cget("bg"),
                            highlightthickness=0, bd=0)
        self.bgid = None
        self.fgid = None
        self.pct = 0.0
        self.cv.bind("<Configure>", lambda e: self._draw())

    def _draw(self):
        P = PALETTE
        w = max(self.cv.winfo_width(), 10)
        self.cv.delete("all")
        round_rect(self.cv, 0, 0, w, self.h, self.h / 2, fill=P["card2"], outline="")
        fw = max(self.h, w * min(max(self.pct, 0.0), 100.0) / 100.0)
        if self.pct > 0:
            round_rect(self.cv, 0, 0, fw, self.h, self.h / 2,
                       fill=P["accent"], outline="")

    def set(self, pct):
        self.pct = pct
        self._draw()

    def pack(self, **kw):
        self.cv.pack(**kw)
        return self


def card(parent, title, font_h):
    P = PALETTE
    outer = tk.Frame(parent, bg=P["card"], highlightthickness=1,
                     highlightbackground=P["line"], bd=0)
    if title:
        tk.Label(outer, text=title, bg=P["card"], fg=P["dim"], font=font_h,
                 anchor="w").pack(fill="x", padx=18, pady=(14, 0))
    inner = tk.Frame(outer, bg=P["card"])
    inner.pack(fill="both", expand=True, padx=18, pady=(8, 16))
    return outer, inner


class DarkScrollbar:
    """Canvas scrollbar: no platform-native white trough or arrow buttons."""

    def __init__(self, parent, command, width=12):
        self.command = command
        self.first, self.last = 0.0, 1.0
        self.offset = 0.0
        self.cv = tk.Canvas(parent, width=width, bg=PALETTE["bg"],
                            highlightthickness=0, bd=0, takefocus=True)
        self.cv.bind("<Configure>", lambda event: self.draw())
        self.cv.bind("<Button-1>", self.press)
        self.cv.bind("<B1-Motion>", self.drag)
        self.cv.bind("<Up>", lambda event: command("scroll", -1, "units"))
        self.cv.bind("<Down>", lambda event: command("scroll", 1, "units"))
        self.cv.bind("<Prior>", lambda event: command("scroll", -1, "pages"))
        self.cv.bind("<Next>", lambda event: command("scroll", 1, "pages"))

    def geometry(self):
        height = max(1, self.cv.winfo_height())
        span = self.last - self.first
        size = min(height, max(24, span * height))
        top = 0 if span >= 1 else self.first / (1 - span) * (height - size)
        return height, size, top

    def set(self, first, last):
        self.first, self.last = float(first), float(last)
        self.draw()

    def draw(self):
        self.cv.delete("all")
        if self.last - self.first >= 1:
            return
        _, size, top = self.geometry()
        self.cv.create_rectangle(2, top, max(3, self.cv.winfo_width() - 2), top + size,
                                 fill=PALETTE["faint"], outline="")

    def press(self, event):
        self.cv.focus_set()
        _, size, top = self.geometry()
        self.offset = event.y - top if top <= event.y <= top + size else size / 2
        self.drag(event)

    def drag(self, event):
        height, size, _ = self.geometry()
        if height <= size:
            return
        fraction = (event.y - self.offset) / (height - size) * (1 - self.last + self.first)
        self.command("moveto", max(0, min(1 - self.last + self.first, fraction)))

    def pack(self, **kwargs):
        self.cv.pack(**kwargs)


class ShockTab:
    """Independent Shock form; the save button stays visible on small windows."""

    def __init__(self, parent, ui_font, initial_dir=None):
        P = PALETTE
        self.parent = parent
        self.initial_dir = initial_dir
        self.font = (ui_font, 10)
        self.small = (ui_font, 9)
        self.profile = None
        self.g_var = tk.StringVar(parent, value="25")
        self.ms_var = tk.StringVar(parent, value="15")
        self.points_var = tk.StringVar(parent, value=str(SHOCK_POINTS))
        self.wave_var = tk.StringVar(parent, value="half-sine")
        self.direction_var = tk.StringVar(parent, value="mx")
        self.output_dir_var = tk.StringVar(parent, value=(initial_dir() if initial_dir else None)
                                           or os.path.dirname(os.path.abspath(__file__)))
        self.all_var = tk.BooleanVar(parent, value=False)
        self.overwrite_var = tk.BooleanVar(parent, value=False)
        self.name_var = tk.StringVar(parent)
        self.summary_var = tk.StringVar(parent)
        self.status_var = tk.StringVar(parent, value="출력 폴더를 확인하고 출력 실행을 누르세요.")

        footer = tk.Frame(parent, bg=P["bg"])
        footer.pack(side="bottom", fill="x", pady=(12, 0))
        self.save_button = RButton(footer, "출력 실행", self.save,
                                  w=160, h=40, font=(ui_font, 11, "bold"))
        self.save_button.pack(side="left")
        tk.Label(footer, textvariable=self.status_var, bg=P["bg"], fg=P["dim"],
                 font=self.small, anchor="w", justify="left", wraplength=490
                 ).pack(side="left", padx=(14, 0), fill="x", expand=True)

        body = tk.Frame(parent, bg=P["bg"])
        body.pack(fill="both", expand=True)
        scroller = tk.Canvas(body, bg=P["bg"], highlightthickness=0, bd=0)
        sb = DarkScrollbar(body, command=scroller.yview, width=12)
        sb.pack(side="right", fill="y")
        scroller.pack(side="left", fill="both", expand=True)
        scroller.configure(yscrollcommand=sb.set)
        content = tk.Frame(scroller, bg=P["bg"])
        window = scroller.create_window(0, 0, window=content, anchor="nw")
        content.bind("<Configure>", lambda event:
                     scroller.configure(scrollregion=scroller.bbox("all")))
        scroller.bind("<Configure>", lambda event:
                      scroller.itemconfigure(window, width=event.width))
        self.scroller = scroller

        c1, form = card(content, "SHOCK 조건", (ui_font, 9, "bold"))
        c1.pack(fill="x", pady=(8, 0))
        row = tk.Frame(form, bg=P["card"])
        row.pack(fill="x")
        for column, (label, variable) in enumerate((("Peak 가속도 (g)", self.g_var),
                                                    ("펄스 시간 T (ms)", self.ms_var),
                                                    ("전체 데이터점 개수", self.points_var))):
            cell = tk.Frame(row, bg=P["card"])
            cell.grid(row=0, column=column, sticky="ew", padx=(0, 18))
            row.grid_columnconfigure(column, weight=1, uniform="shock-fields")
            tk.Label(cell, text=label, bg=P["card"], fg=P["dim"], font=self.small,
                     anchor="w").pack(fill="x", pady=(0, 5))
            entry = tk.Entry(cell, textvariable=variable, width=12, font=self.font,
                             bg=P["card2"], fg=P["text"], insertbackground=P["text"],
                             relief="flat", bd=0, highlightthickness=1,
                             highlightbackground=P["line"], highlightcolor=P["accent"])
            entry.pack(fill="x", ipady=7)

        self._choices(form, "가속도 파형", self.wave_var, SHOCK_WAVEFORMS)
        self._choices(form, "가진 방향", self.direction_var,
                      [(item[0], item[1]) for item in SHOCK_DIRECTIONS])
        tk.Label(form, text="그래프는 SFO 적용 후 실제 방향 표시 · 전후 선형, 중앙 가속도 적분\n"
                 "점 수: 0~3T 전체 N점 (중앙 N−2점) · 시간 입력 0.01 ms 단위",
                 bg=P["card"], fg=P["dim"], font=self.small, anchor="w"
                 ).pack(fill="x", pady=(12, 0))

        c2, preview = card(content, "프로파일 미리보기", (ui_font, 9, "bold"))
        c2.pack(fill="x", pady=(12, 0))
        self.plot = tk.Canvas(preview, height=245, bg=P["card"],
                              highlightthickness=0, bd=0)
        self.plot.pack(fill="x")
        self.plot.bind("<Configure>", lambda event: self.draw())
        tk.Label(preview, textvariable=self.summary_var, bg=P["card"], fg=P["text"],
                 font=self.small, anchor="w", justify="left"
                 ).pack(fill="x", pady=(6, 0))

        c3, output = card(content, "출력", (ui_font, 9, "bold"))
        c3.pack(fill="x", pady=(12, 0))
        path_row = tk.Frame(output, bg=P["card"])
        path_row.pack(fill="x", pady=(0, 10))
        tk.Label(path_row, text="출력 폴더", bg=P["card"], fg=P["dim"],
                 font=self.small).pack(side="left", padx=(0, 8))
        tk.Entry(path_row, textvariable=self.output_dir_var, bg=P["card2"], fg=P["text"],
                 insertbackground=P["text"], relief="flat", font=self.font,
                 highlightthickness=1, highlightbackground=P["line"], highlightcolor=P["accent"]
                 ).pack(side="left", fill="x", expand=True, ipady=7, padx=(0, 8))
        RButton(path_row, "폴더 선택", self.pick_directory, kind="ghost", w=100,
                h=34, font=self.font).pack(side="left")
        for text, var in (("6방향 모두 저장 (mx, my, mz, px, py, pz)", self.all_var),
                          ("같은 이름의 파일 덮어쓰기", self.overwrite_var)):
            tk.Checkbutton(output, text=text, variable=var, bg=P["card"], fg=P["text"],
                           activebackground=P["card"], activeforeground=P["text"],
                           selectcolor=P["card2"], font=self.font, bd=0,
                           highlightthickness=0).pack(anchor="w", pady=(0, 6))
        tk.Label(output, textvariable=self.name_var, bg=P["card"], fg=P["accent"],
                 font=self.font, anchor="w", wraplength=650, justify="left"
                 ).pack(fill="x")
        tk.Label(output, text="입력 시간: ms  /  파일 시간: s  /  속도: mm/s  /  1g = 9.80665 m/s²\n"
                 "NSID 100001 · LCID 음수 방향 701 / 양수 방향 702 · VAD 0 · Motion SF 1.0\n"
                 "기존 모델의 NSET_BC를 사용합니다. 가진축의 기존 SPC는 해제해야 합니다.\n"
                 "한 해석에는 한 방향 파일만 INCLUDE하고, LCID 701/702 중복을 피하세요.\n"
                 "해석 종료시간은 메인 덱에서 설정합니다. 이 파일에는 경계조건과 곡선만 생성합니다.",
                 bg=P["card"], fg=P["dim"], font=self.small, justify="left",
                 anchor="w", wraplength=680).pack(fill="x", pady=(10, 0))

        # Only this tab's descendants handle wheel scrolling; no global bindings
        # that could steal scrolling from the converter log or detail dialog.
        def wheel(event):
            if getattr(event, "num", None) in (4, 5):
                step = -1 if event.num == 4 else 1
            else:
                delta = getattr(event, "delta", 0)
                if not delta:
                    return
                step = -max(1, int(abs(delta) / 120)) if delta > 0 else max(1, int(abs(delta) / 120))
            scroller.yview_scroll(step, "units")
            return "break"

        def bind_wheel(widget):
            for event_name in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                widget.bind(event_name, wheel, add="+")
            for child in widget.winfo_children():
                bind_wheel(child)
        bind_wheel(scroller)
        for variable in (self.g_var, self.ms_var, self.points_var, self.wave_var, self.direction_var, self.all_var):
            variable.trace_add("write", self.refresh)
        self.refresh()

    def _choices(self, parent, label, variable, choices):
        P = PALETTE
        row = tk.Frame(parent, bg=P["card"])
        row.pack(fill="x", pady=(12, 0))
        tk.Label(row, text=label, width=12, anchor="w", bg=P["card"], fg=P["dim"],
                 font=self.small).pack(side="left")
        for value, text in choices:
            tk.Radiobutton(row, text=text, value=value, variable=variable,
                           font=self.font, bg=P["card"], fg=P["text"],
                           activebackground=P["card"], activeforeground=P["text"],
                           selectcolor=P["card2"], highlightthickness=0,
                           bd=0, padx=6, cursor="hand2").pack(side="left")

    def refresh(self, *_args):
        try:
            p = build_shock_profile(self.g_var.get(), self.ms_var.get(),
                                    self.wave_var.get(), self.direction_var.get(), self.points_var.get())
        except ValueError as exc:
            self.profile = None
            self.name_var.set("—")
            self.summary_var.set(str(exc))
            self.status_var.set("가속도·펄스 시간·데이터점 개수를 확인하세요.")
            self.save_button.config(enabled=False)
            self.draw()
            return
        self.profile = p
        if self.all_var.get():
            self.name_var.set("6개 파일 저장 · 미리보기 방향: " + p["direction"] + "\n" +
                "\n".join(build_shock_profile(p["g"], p["duration_ms"], p["waveform"],
                    d, p["point_count"])["filename"] for d in ("mx", "my", "mz", "px", "py", "pz")))
        else:
            self.name_var.set(p["filename"])
        self.summary_var.set("종료: %g ms (%.5f s)  ·  파일 전체: %d점\n"
                             "적용 T/2T 속도: %+.2f / %+.2f mm/s  ·  최종: 0.00  ·  SFO: %+d" %
                             (p["duration_ms"] * 3, p["end_s"], len(p["times"]),
                              -p["sfo"] * p["v_peak"], p["sfo"] * p["v_peak"], p["sfo"]))
        self.save_button.config(enabled=True)
        self.status_var.set("출력 폴더를 확인하고 출력 실행을 누르세요.")
        self.draw()

    def draw(self):
        P = PALETTE
        cv = self.plot
        cv.delete("all")
        p = self.profile
        if p is None:
            return
        width = max(200, cv.winfo_width())
        left, right = 92, width - 24
        total = p["end_s"]
        series = (("Acceleration (g), " + p["direction_label"],
                   [p["sfo"] * a for a in p["accelerations_g"]], P["ok"]),
                  ("Velocity (mm/s), " + p["direction_label"],
                   [p["sfo"] * v for v in p["velocities"]], P["accent"]))
        for panel, (label, values, color) in enumerate(series):
            top, bottom = 27 + panel * 120, 95 + panel * 120
            limit = max(abs(value) for value in values)
            cv.create_text(left, top - 14, text=label, anchor="w", fill=P["dim"], font=self.small)
            y_zero = (top + bottom) / 2
            y_peak = top
            cv.create_line(left, y_zero, right, y_zero, fill=P["line"])
            cv.create_line(left, top, left, bottom, fill=P["line"])
            cv.create_text(left - 8, y_zero, text="0", anchor="e", fill=P["dim"], font=self.small)
            cv.create_text(left - 8, y_peak, text="%.2f" % limit,
                           anchor="e", fill=color, font=self.small)
            cv.create_text(left - 8, bottom, text="−%.2f" % limit,
                           anchor="e", fill=color, font=self.small)
            for multiple in range(4):
                x = left + (right - left) * multiple / 3.0
                cv.create_line(x, top, x, bottom, fill=P["line"], dash=(2, 4))
                cv.create_text(x, bottom + 13, text="%g" % (p["duration_ms"] * multiple),
                               fill=P["dim"], font=self.small)
            points = list(zip(p["times"], values))
            if panel == 0:
                t = p["duration_s"]
                comp = p["sfo"] * p["compensation_g"]
                middle = [(time, value) for time, value in points if t <= time <= 2*t]
                points = [(0.0, comp), (t, comp)] + middle + [(2*t, comp), (total, comp)]
            coords = []
            for t, value in points:
                coords.extend((left + (t / total) * (right - left),
                               y_zero + (value / limit) * (y_peak - y_zero)))
            cv.create_line(*coords, fill=color, width=2)
        cv.create_text(right, 242, text="Time (ms)", anchor="se", fill=P["dim"], font=self.small)

    def pick_directory(self):
        from tkinter import filedialog
        current = os.path.expanduser(self.output_dir_var.get().strip())
        options = dict(parent=self.parent, title="Shock 출력 폴더 선택")
        if os.path.isdir(current):
            options["initialdir"] = current
        path = filedialog.askdirectory(**options)
        if path:
            self.output_dir_var.set(path)

    def save(self):
        from tkinter import messagebox
        self.refresh()
        if self.profile is None:
            return
        p = self.profile
        try:
            result = write_shock_files(self.output_dir_var.get(), p["g"], p["duration_ms"],
                                       p["waveform"], p["direction"], p["point_count"],
                                       self.all_var.get(), self.overwrite_var.get())
        except (OSError, ValueError) as exc:
            self.status_var.set("저장 실패: %s" % exc)
            messagebox.showerror("Shock 출력 실패", str(exc), parent=self.parent)
            return
        if result["failed"]:
            details = "\n".join(os.path.basename(f["path"]) + ": " + f["error"] for f in result["failed"])
            self.status_var.set("%d개 저장 / %d개 실패" % (len(result["written"]), len(result["failed"])))
            messagebox.showerror("Shock 일부 출력 실패", self.status_var.get() + "\n" + details,
                                 parent=self.parent)
        else:
            self.status_var.set("%d개 파일 저장 완료 · %s" % (len(result["written"]), result["directory"]))


def run_gui():
    global tk
    try:
        import tkinter as tk
        from tkinter import filedialog
    except ImportError:
        print("tkinter를 찾을 수 없어 GUI를 열 수 없습니다.")
        print("  Windows/macOS 공식 파이썬에는 기본 포함되어 있습니다.")
        print("  Linux:  sudo apt install python3-tk   (또는 배포판의 tk 패키지)")
        print()
        print("CLI로는 그대로 쓸 수 있습니다:")
        print("  python inp2k.py model.inp -o model.k")
        return 1

    P = PALETTE
    root = tk.Tk()
    ui = _pick_font(["Pretendard", "Noto Sans KR", "Noto Sans CJK KR",
                     "Malgun Gothic", "맑은 고딕", "Apple SD Gothic Neo",
                     "Segoe UI", "Helvetica Neue"], "TkDefaultFont", root)
    # Labels, entries, file paths, numbers and log all use one font family.
    import tkinter.font as tkfont
    for font_name in tkfont.names(root=root):
        tkfont.nametofont(font_name, root=root).configure(family=ui)
    root.option_add("*Font", (ui, 10))
    F_H1 = (ui, 19, "bold")
    F_LB = (ui, 11)
    F_SM = (ui, 9)
    F_HD = (ui, 9, "bold")
    F_BODY = (ui, 10)
    F_BT = (ui, 11, "bold")

    root.title("INP2K v%s  ·  Abaqus → LS-DYNA / Shock" % VERSION)
    root.geometry("980x860")
    root.minsize(820, 640)
    root.configure(bg=P["bg"])
    try:
        root.tk.call("tk", "scaling", 1.3)
    except Exception:
        pass

    state = dict(path=None, out=None, busy=False, t0=0.0)
    q = queue.Queue()

    wrap = tk.Frame(root, bg=P["bg"], padx=26, pady=22)
    wrap.pack(fill="both", expand=True)

    # ---------- 헤더 ----------
    head = tk.Frame(wrap, bg=P["bg"])
    head.pack(fill="x")
    tk.Label(head, text="INP2K", bg=P["bg"], fg=P["text"], font=F_H1).pack(side="left")
    tk.Label(head, text="Abaqus .inp  →  LS-DYNA .k", bg=P["bg"], fg=P["faint"],
             font=F_LB).pack(side="left", padx=(12, 0), pady=(6, 0))

    engine_ok = HAVE_NUMPY and HAVE_PANDAS
    badge = tk.Frame(head, bg=P["card2"], highlightthickness=1,
                     highlightbackground=P["ok"] if engine_ok else P["warn"])
    badge.pack(side="right", pady=(4, 0))
    tk.Label(badge, bg=P["card2"], fg=P["ok"] if engine_ok else P["warn"], font=F_SM,
             padx=10, pady=4,
             text=("가속 엔진 사용 중  numpy+pandas" if engine_ok
                   else "느린 경로  " + ("pandas 없음" if HAVE_NUMPY else "numpy 없음"))
             ).pack()

    # Custom dark tabs do not inherit the Windows native white notebook theme.
    notebook = tk.Frame(wrap, bg=P["bg"])
    notebook.pack(fill="both", expand=True, pady=(16, 0))
    tab_bar = tk.Frame(notebook, bg=P["bg"])
    tab_bar.pack(fill="x", pady=(0, 6))
    page_area = tk.Frame(notebook, bg=P["bg"])
    page_area.pack(fill="both", expand=True)
    converter_tab = tk.Frame(page_area, bg=P["bg"])
    shock_tab = tk.Frame(page_area, bg=P["bg"])
    pages = (converter_tab, shock_tab)
    tabs = []

    def select_tool(index):
        for i, page in enumerate(pages):
            page.pack_forget()
            tabs[i].configure(bg=P["accent_dim"] if i == index else P["card"],
                              fg=P["text"] if i == index else P["dim"])
        pages[index].pack(fill="both", expand=True)

    for index, label in enumerate(("INP → K 변환", "Shock")):
        button = tk.Button(tab_bar, text=label, command=lambda i=index: select_tool(i),
                           bg=P["card"], fg=P["dim"], font=F_LB,
                           activebackground=P["accent_dim"], activeforeground=P["text"],
                           relief="flat", bd=0, highlightthickness=1,
                           highlightbackground=P["line"], highlightcolor=P["accent"],
                           padx=22, pady=9, cursor="hand2")
        button.pack(side="left", padx=(0, 6))
        tabs.append(button)
    notebook.shock = ShockTab(shock_tab, ui, initial_dir=lambda:
        os.path.dirname(os.path.abspath(state["out"] or state["path"]))
        if state["out"] or state["path"] else None)
    select_tool(0)
    wrap = converter_tab

    # ---------- 가속 안내 ----------
    if not engine_ok:
        warnc = tk.Frame(wrap, bg="#2A2115", highlightthickness=1,
                         highlightbackground=P["warn"])
        warnc.pack(fill="x", pady=(14, 0))
        inner = tk.Frame(warnc, bg="#2A2115")
        inner.pack(fill="x", padx=16, pady=12)
        tk.Label(inner, bg="#2A2115", fg=P["warn"], font=F_LB, anchor="w",
                 text="변환이 느린 이유입니다. numpy·pandas 없이 순수 파이썬으로 도는 중입니다."
                 ).pack(anchor="w")
        tk.Label(inner, bg="#2A2115", fg=P["dim"], font=F_SM, anchor="w",
                 text="설치하면 큰 모델에서 10배 이상 빨라집니다. 설치 후 프로그램을 다시 켜 주세요."
                 ).pack(anchor="w", pady=(2, 8))
        inst_row = tk.Frame(inner, bg="#2A2115")
        inst_row.pack(anchor="w")
        inst_msg = tk.Label(inst_row, text="", bg="#2A2115", fg=P["dim"], font=F_SM)

        def do_install():
            btn_inst.config(text="설치 중…", enabled=False)
            inst_msg.config(text="pip 실행 중입니다. 잠시 기다려 주세요.")

            def job():
                import subprocess
                try:
                    r = subprocess.run([sys.executable, "-m", "pip", "install",
                                        "numpy", "pandas"],
                                       capture_output=True, text=True)
                    q.put(("inst", r.returncode, (r.stdout or "")[-400:]
                           + (r.stderr or "")[-400:]))
                except Exception as e:
                    q.put(("inst", 1, str(e)))
            threading.Thread(target=job, daemon=True).start()

        btn_inst = RButton(inst_row, "numpy · pandas 설치", do_install,
                           kind="primary", w=180, h=34, font=F_LB)
        btn_inst.pack(side="left")
        inst_msg.pack(side="left", padx=(12, 0))
    else:
        btn_inst = None
        inst_msg = None

    # ---------- 파일 ----------
    c1, f1 = card(wrap, "입력 파일", F_HD)
    c1.pack(fill="x", pady=(14, 0))
    pathvar = tk.StringVar(value="선택된 파일이 없습니다")
    outvar = tk.StringVar(value="")
    tk.Label(f1, textvariable=pathvar, bg=P["card"], fg=P["text"], font=F_BODY,
             anchor="w").pack(fill="x")

    def pick():
        p = filedialog.askopenfilename(
            title="Abaqus 입력 파일 선택",
            filetypes=[("Abaqus deck", "*.inp *.dat *.blk *.inc"), ("모든 파일", "*.*")])
        if not p:
            return
        state["path"] = p
        pathvar.set("%s   ·   %.1f MB" % (os.path.basename(p),
                                          os.path.getsize(p) / 1048576.0))
        state["out"] = os.path.splitext(p)[0] + ".k"
        outvar.set(state["out"])
        btn_run.config(enabled=True)

    def pick_out():
        p = filedialog.asksaveasfilename(defaultextension=".k",
                                         filetypes=[("LS-DYNA keyword", "*.k *.key")])
        if p:
            state["out"] = p
            outvar.set(p)

    r1 = tk.Frame(f1, bg=P["card"])
    r1.pack(fill="x", pady=(12, 0))
    RButton(r1, "파일 선택", pick, kind="ghost", w=104, h=34, font=F_LB).pack(side="left")
    tk.Label(r1, text="출력", bg=P["card"], fg=P["faint"],
             font=F_SM).pack(side="left", padx=(16, 6))
    oe = tk.Entry(r1, textvariable=outvar, font=F_BODY, bg=P["card2"], fg=P["text"],
                  insertbackground=P["text"], relief="flat", bd=0,
                  highlightthickness=1, highlightbackground=P["line"],
                  highlightcolor=P["accent"])
    oe.pack(side="left", fill="x", expand=True, ipady=6, padx=(0, 8))
    RButton(r1, "변경", pick_out, kind="ghost", w=60, h=34, font=F_LB).pack(side="left")

    # ---------- 옵션 ----------
    c2, f2 = card(wrap, "옵션", F_HD)
    c2.pack(fill="x", pady=(14, 0))
    sw = {}
    items = [("sets", "세트 출력", "SET_NODE_LIST / SET_SOLID"),
             ("mat", "재료·단면", "MAT / SECTION"),
             ("bc", "경계조건", "BOUNDARY_SPC_SET"),
             ("contact", "접촉·구속", "원본 CONTACT / CONSTRAINED")]
    grid = tk.Frame(f2, bg=P["card"])
    grid.pack(fill="x")
    for i, (k, lab, sub) in enumerate(items):
        s_ = Switch(grid, lab, DEFAULT_OPT[k], font=F_LB, sub=sub, subfont=F_SM)
        s_.grid(row=i // 2, column=i % 2, sticky="w", padx=(0, 24), pady=9)
        sw[k] = s_
    for cix in range(2):
        grid.grid_columnconfigure(cix, weight=1, uniform="options")

    r2 = tk.Frame(f2, bg=P["card"])
    r2.pack(fill="x", pady=(14, 0))
    detail = parse_detail_settings(detail_defaults())

    def show_details():
        if state["busy"]:
            return
        win = tk.Toplevel(root)
        win.withdraw()                     # v2.5: size after the content is built
        win.title("상세 설정")
        win.configure(bg=P["bg"])
        win.transient(root)
        from tkinter import messagebox
        shell = tk.Frame(win, bg=P["bg"], padx=24, pady=22)
        shell.pack(fill="both", expand=True)
        tk.Label(shell, text="상세 설정", bg=P["bg"], fg=P["text"],
                 font=F_H1, anchor="w").pack(fill="x")
        tk.Label(shell, text="필요한 항목만 조정하고, 자주 쓰는 값은 JSON으로 저장하세요.",
                 bg=P["bg"], fg=P["dim"], font=F_BODY, anchor="w").pack(fill="x", pady=(6, 18))
        nav = tk.Frame(shell, bg=P["bg"])
        nav.pack(fill="x", pady=(0, 14))
        # v2.5: reserve the bottom rows first; a short window shrinks the
        # page card instead of clipping the buttons.
        buttons = tk.Frame(shell, bg=P["bg"])
        buttons.pack(side="bottom", fill="x")
        tk.Label(shell, text="공란은 기존값 유지 · 불러온 설정은 [적용] 후 변환에 반영됩니다.",
                 bg=P["bg"], fg=P["dim"], font=F_SM, anchor="w").pack(side="bottom", fill="x", pady=(12, 12))
        book, page_host = card(shell, "", F_HD)
        book.pack(fill="both", expand=True)
        page_host.grid_columnconfigure(0, weight=1)
        page_host.grid_rowconfigure(0, weight=1)
        pages, tabs = [], []
        def select_page(index):
            pages[index].tkraise()
            for i, button in enumerate(tabs):
                button.kind = "primary" if i == index else "ghost"
                button._paint(False)
        variables = {}
        groups = [
            ("Formulation", [("all_contact", "전체 접촉", "ERODING_SINGLE_SURFACE"),
                             ("solid", "Solid ELFORM (육면체 전용)", "auto"),
                             ("shell", "Shell ELFORM", "auto")]),
            ("Contact", [("contact_"+k, k.upper() + (" (공란: 원본, 없으면 0.2)" if k in ("fs", "fd") else ""), detail_defaults()["contact_"+k])
                         for k in CONTACT_FIELDS]),
            ("Whole contact", [("all_contact_"+k, k.upper(), "") for k in CONTACT_FIELDS]),
        ]
        for kind in ("shell", "solid"):
            defaults = dict(zip(("ihq", "qm", "qb", "qw"), HOURGLASS_DEFAULTS[kind]))
            groups.append(("Hourglass " + kind, [("hg_"+kind+"_"+k, k.upper(),
                           "" if defaults.get(k) is None else str(defaults[k]))
                           for k in ("ihq", "qm", "ibq", "q1", "q2", "qb", "qw")]))
        titles = ("요소 · 전체 접촉", "개별 접촉 계수", "전체 접촉 계수", "쉘 Hourglass", "솔리드 Hourglass")
        notes = (
            "전체 접촉은 ELSET_ALL(900001)에 적용합니다.\n순수 C3D10은 ELFORM 16 유지 · Solid 지정은 육면체 전용",
            "FS·FD 공란: 원본 유지, 원본 값이 없으면 0.2 · SST·MST 음수 입력 가능(두께 절댓값)\nSOFT · SBOPT · DEPTH · BSORT는 비-TIE 접촉에 적용",
            "ELSET_ALL 전체 접촉에만 적용합니다. 공란은 개별 접촉 계수 값을 따릅니다.\nSST·MST 음수 입력 가능(두께 절댓값)",
            "쉘 PART가 공유하는 HGID 1의 설정입니다. 공란은 기존 처리를 유지합니다.",
            "솔리드 PART가 공유하는 HGID 2의 설정입니다. 공란은 기존 처리를 유지합니다.")
        for index, (title, fields) in enumerate(groups):
            tab = tk.Frame(page_host, bg=P["card"])
            tab.grid(row=0, column=0, sticky="nsew")
            pages.append(tab)
            button = RButton(nav, titles[index], lambda i=index: select_page(i),
                             kind="ghost", w=150, h=36, font=F_BODY)
            button.pack(side="left", padx=(0, 8))
            tabs.append(button)
            tk.Label(tab, text=titles[index], font=F_LB, bg=P["card"], fg=P["text"],
                     anchor="w").pack(fill="x", pady=(8, 6))
            tk.Label(tab, text=notes[index], font=F_SM, bg=P["card"], fg=P["dim"],
                     anchor="w", justify="left", wraplength=650).pack(fill="x", pady=(0, 14))
            form = tk.Frame(tab, bg=P["card"])
            form.pack(fill="x")
            columns = 1 if index == 0 else 3
            for col in range(columns):
                form.grid_columnconfigure(col, weight=1, uniform="fields")
            for position, (key, label, default) in enumerate(fields):
                cell = tk.Frame(form, bg=P["card"])
                cell.grid(row=position//columns, column=position%columns,
                          sticky="ew", padx=(0, 16 if columns > 1 else 0), pady=(0, 12))
                short_label = label.split(" (")[0] if "contact_" in key else label
                tk.Label(cell, text=short_label, font=F_SM, bg=P["card"], fg=P["dim"],
                         anchor="w").pack(fill="x", pady=(0, 5))
                var = tk.StringVar(value=str(detail.get(key, "")))
                variables[key] = var
                if key in ("all_contact", "solid", "shell"):
                    choices = (("AUTOMATIC_SINGLE_SURFACE", "ERODING_SINGLE_SURFACE")
                               if key == "all_contact" else
                               ("auto", "1", "2") if key == "solid" else ("auto", "2", "16"))
                    entry = tk.OptionMenu(cell, var, *choices)
                    entry.configure(font=F_BODY, bg=P["card2"], fg=P["text"],
                        activebackground=P["accent_dim"], activeforeground=P["text"],
                        relief="flat", bd=0, highlightthickness=1,
                        highlightbackground=P["line"], highlightcolor=P["accent"],
                        anchor="w", padx=10, pady=6, cursor="hand2", takefocus=True)
                    entry["menu"].configure(font=F_BODY, bg=P["card2"], fg=P["text"],
                        activebackground=P["accent_dim"], activeforeground=P["text"],
                        relief="flat", bd=0)
                    entry.pack(fill="x")
                else:
                    entry = tk.Entry(cell, textvariable=var, font=F_BODY, width=12,
                        bg=P["card2"], fg=P["text"], insertbackground=P["text"],
                        selectbackground=P["accent_dim"], selectforeground=P["text"],
                        relief="flat", bd=0, highlightthickness=1,
                        highlightbackground=P["line"], highlightcolor=P["accent"])
                    entry.pack(fill="x", ipady=7)
            if index == 0:
                # v2.5: PAD / TA / ADHESIVE property names -> solid ELFORM -1
                var = tk.StringVar(value=bool_text(detail.get("neg_elform_names")))
                variables["neg_elform_names"] = var
                tk.Checkbutton(tab, text="PAD · TA · ADHESIVE → ELFORM -1",
                    variable=var, onvalue="1", offvalue="0", font=F_BODY,
                    bg=P["card"], fg=P["text"], activebackground=P["card"],
                    activeforeground=P["text"], selectcolor=P["card2"],
                    highlightthickness=0, bd=0, anchor="w", cursor="hand2"
                    ).pack(fill="x", pady=(2, 6))
        select_page(0)
        def save_json():
            try:
                values = parse_detail_settings({k: v.get() for k, v in variables.items()})
                path = filedialog.asksaveasfilename(parent=win, defaultextension=".json",
                    initialfile="inp2k-settings.json", filetypes=[("JSON", "*.json")])
                if path:
                    save_detail_settings(path, values)
            except (ValueError, OSError) as exc:
                messagebox.showerror("설정 저장 실패", str(exc), parent=win)
        def load_json():
            path = filedialog.askopenfilename(parent=win, filetypes=[("JSON", "*.json")])
            if not path:
                return
            try:
                values = load_detail_settings(path)
            except (ValueError, OSError) as exc:
                messagebox.showerror("설정 불러오기 실패", str(exc), parent=win)
                return
            for key, var in variables.items():
                if key in BOOL_DETAIL_KEYS:
                    var.set(bool_text(values.get(key, False)))
                    continue
                var.set(values.get(key, detail_defaults()[key] if key in ("shell", "solid", "all_contact") else ""))
        def reset():
            for key, value in detail_defaults().items():
                variables[key].set(bool_text(value) if key in BOOL_DETAIL_KEYS else value)
        def apply():
            try:
                values = parse_detail_settings({k: v.get() for k, v in variables.items()})
            except ValueError as exc:
                messagebox.showerror("설정 확인", str(exc), parent=win)
                return
            detail.clear()
            detail.update(values)
            win.destroy()
        RButton(buttons, "JSON 저장", save_json, kind="ghost", w=100, h=34, font=F_LB).pack(side="left", padx=4)
        RButton(buttons, "불러오기", load_json, kind="ghost", w=100, h=34, font=F_LB).pack(side="left", padx=4)
        RButton(buttons, "초기값", reset, kind="ghost", w=80, h=34, font=F_LB).pack(side="left", padx=4)
        RButton(buttons, "적용", apply, kind="primary", w=90, h=34, font=F_LB).pack(side="right", padx=(8, 0))
        RButton(buttons, "취소", win.destroy, kind="ghost", w=80, h=34, font=F_LB).pack(side="right")
        win.bind("<Escape>", lambda event: win.destroy())
        # v2.5: fit the real content (all pages share one grid cell) so the
        # bottom buttons are never clipped; keep the window on screen.
        win.update_idletasks()
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        width = min(max(860, win.winfo_reqwidth() + 20), sw - 40)
        height = min(max(720, win.winfo_reqheight() + 20), sh - 80)
        win.minsize(min(820, width), min(680, height))
        x = root.winfo_rootx() + (root.winfo_width() - width) // 2
        y = root.winfo_rooty() + (root.winfo_height() - height) // 2
        x = min(max(0, x), max(0, sw - width))
        y = min(max(0, y), max(0, sh - height - 40))
        win.geometry("%dx%d+%d+%d" % (width, height, x, y))
        win.deiconify()
        win.lift()
        try:
            win.grab_set()
        except tk.TclError:
            win.after(100, lambda: win.winfo_exists() and win.grab_set())
    RButton(r2, "상세 설정", show_details, kind="ghost", w=120, h=34, font=F_LB).pack(side="left")

    # ---------- 실행 ----------
    c3, f3 = card(wrap, "", F_HD)
    c3.pack(fill="x", pady=(14, 0))
    r3 = tk.Frame(f3, bg=P["card"])
    r3.pack(fill="x")
    btn_run = RButton(r3, "변환 실행", lambda: start(), kind="primary", w=132, h=40,
                      font=F_BT)
    btn_run.pack(side="left")
    btn_run.config(enabled=False)
    btn_open = RButton(r3, "폴더 열기", lambda: open_folder(state.get("out")),
                       kind="ghost", w=104, h=40, font=F_LB)
    btn_open.pack(side="left", padx=(10, 0))
    btn_open.config(enabled=False)
    btn_finish = RButton(r3, "완료", lambda: root.destroy() if not state["busy"] else None,
                         kind="primary", w=76, h=40, font=F_LB)
    btn_finish.pack(side="left", padx=(10,0))
    btn_finish.config(enabled=False)

    stat_box = tk.Frame(r3, bg=P["card"])
    stat_box.pack(side="right")
    pctvar = tk.StringVar(value="")
    phasevar = tk.StringVar(value="대기 중")
    tk.Label(stat_box, textvariable=pctvar, bg=P["card"], fg=P["accent"],
             font=(ui, 15, "bold")).pack(side="right", padx=(10, 0))
    tk.Label(stat_box, textvariable=phasevar, bg=P["card"], fg=P["dim"],
             font=F_SM).pack(side="right")

    bar = Bar(f3)
    bar.pack(fill="x", pady=(14, 0))

    # ---------- 로그 ----------
    c4, f4 = card(wrap, "로그", F_HD)
    c4.pack(fill="both", expand=True, pady=(14, 0))
    txt = tk.Text(f4, font=F_BODY, wrap="word", bg=P["card"], fg=P["text"],
                  relief="flat", bd=0, highlightthickness=0, height=13,
                  insertbackground=P["text"], spacing1=1, spacing3=1)
    sb = DarkScrollbar(f4, command=txt.yview, width=12)
    txt.configure(yscrollcommand=sb.set)
    sb.pack(side="right", fill="y")
    txt.pack(fill="both", expand=True)
    txt.tag_config("warn", foreground=P["warn"])
    txt.tag_config("err", foreground=P["err"])
    txt.tag_config("ok", foreground=P["ok"])
    txt.tag_config("info", foreground=P["dim"])
    txt.tag_config("head", foreground=P["text"])

    def add_line(lv, m):
        txt.insert("end", m + "\n", lv)
        if int(txt.index("end-1c").split(".")[0]) > 3000:
            txt.delete("1.0", "501.0")  # Complete records remain in conversion.log.
        txt.see("end")

    def open_folder(pth):
        if not pth:
            return
        d = os.path.dirname(os.path.abspath(pth))
        try:
            if sys.platform.startswith("win"):
                os.startfile(d)
            elif sys.platform == "darwin":
                os.system('open "%s"' % d)
            else:
                os.system('xdg-open "%s"' % d)
        except Exception:
            pass

    def worker(path, out, opt):
        log = Log(sink=lambda lv, m: q.put(("log", lv, m)))
        try:
            r = convert_file(path, out, opt, log,
                             progress=lambda ph, pct, t: q.put(("prog", ph, pct, t)))
            q.put(("done", r, None))
        except Exception:
            import traceback
            q.put(("done", None, traceback.format_exc()))

    def start():
        if state["busy"] or not state["path"]:
            return
        out = outvar.get().strip() or (os.path.splitext(state["path"])[0] + ".k")
        state["out"] = out
        opt = dict(DEFAULT_OPT)
        for k, s_ in sw.items():
            opt[k] = s_.get()
        opt.update(detail)
        opt.update(tet10=True, beamNode=True, auto_sets=True, unit="mmts")
        txt.delete("1.0", "end")
        add_line("head", "▶  " + os.path.basename(state["path"]))
        state["busy"] = True
        btn_finish.config(enabled=False)
        state["t0"] = time.time()
        btn_run.config(text="변환 중…", enabled=False)
        btn_open.config(enabled=False)
        bar.set(0)
        pctvar.set("0%")
        phasevar.set("시작하는 중")
        threading.Thread(target=worker, args=(state["path"], out, opt),
                         daemon=True).start()

    PH = {"read": "읽는 중", "convert": "변환 중", "write": "파일 쓰는 중",
          "done": "마무리"}

    def poll():
        deadline = time.monotonic()+.015
        try:
            for _ in range(80):
                if time.monotonic() >= deadline:
                    break
                it = q.get_nowait()
                if it[0] == "log":
                    add_line(it[1], it[2])
                elif it[0] == "prog":
                    _, ph, pct, t = it
                    bar.set(pct)
                    pctvar.set("%d%%" % pct)
                    el = time.time() - state["t0"]
                    eta = ""
                    if pct > 4 and el > 1:
                        eta = "  ·  남은 시간 약 %d초" % max(1, int(el * (100 - pct) / pct))
                    phasevar.set("%s   %s%s" % (PH.get(ph, ph), t, eta))
                elif it[0] == "inst":
                    code, msg = it[1], it[2]
                    if btn_inst:
                        btn_inst.config(text="설치 완료" if code == 0 else "설치 실패",
                                        enabled=code != 0)
                    if inst_msg:
                        inst_msg.config(
                            text=("설치했습니다. 프로그램을 껐다 켜면 가속이 적용됩니다."
                                  if code == 0 else "설치 실패 — 로그를 확인하세요."))
                    add_line("ok" if code == 0 else "err", msg.strip()[-600:])
                elif it[0] == "done":
                    state["busy"] = False
                    btn_run.config(text="변환 실행", enabled=True)
                    r, errtext = it[1], it[2]
                    if errtext:
                        bar.set(0)
                        pctvar.set("")
                        phasevar.set("실패")
                        add_line("err", errtext)
                    else:
                        bar.set(100)
                        pctvar.set("100%")
                        phasevar.set("완료  ·  %.1f초" % r["seconds"])
                        btn_open.config(enabled=True)
                        btn_finish.config(enabled=True)
                        c = r["counts"]
                        add_line("head", "")
                        add_line("head", "   절점 %s      솔리드 %s      쉘 %s      보 %s"
                                 % (f"{c['node']:,}", f"{c['solid']:,}",
                                    f"{c['shell']:,}", f"{c['beam']:,}"))
                        add_line("head", "   PART %d   재료 %d   세그먼트 %d   접촉 %d   구속 %d"
                                 % (r["n_part"], r["n_mat"], r["n_seg"],
                                    r["n_contact"], r["n_constr"]))
                        add_line("head", "")
                        for k, n in sorted(r["type_count"].items(),
                                           key=lambda kv: -kv[1]):
                            src, sub = k.split("|")
                            dst = "변환 안 됨" if sub == "?" else DYNA_KEYWORD.get(sub, sub)
                            add_line("info", "   %-10s →  %-34s %s"
                                     % (src, dst, f"{n:,}"))
                        if r["imap"]:
                            add_line("head", "")
                            seen = {}
                            for a, b in r["imap"]:
                                seen[(a, b)] = seen.get((a, b), 0) + 1
                            for (a, b), n in seen.items():
                                add_line("info", "   %-28s →  %s" % (a[:28], b))
                        add_line("head", "")
                        add_line("ok", "   저장  " + r["out"])
        except queue.Empty:
            pass
        root.after(100, poll)

    poll()
    root.mainloop()
    return 0


# ============================================================
# 진단 · 자체 시험
# ============================================================
MINI_DECK = """*Heading
selftest
*Node
1, 0., 0., 0.
2, 1., 0., 0.
3, 1., 1., 0.
4, 0., 1., 0.
5, 0., 0., 1.
6, 1., 0., 1.
7, 1., 1., 1.
8, 0., 1., 1.
*Element, type=C3D8R, elset=ALL
1, 1, 2, 3, 4, 5, 6, 7, 8
*Nset, nset=BOT
1, 2, 3, 4
*Solid Section, elset=ALL, material=STEEL
*Material, name=STEEL
*Density
7.85e-9
*Elastic
210000., 0.3
*Boundary
BOT, ENCASTRE
"""


def run_check():
    print("=" * 58)
    print(" inp2k 진단  v%s" % VERSION)
    print("=" * 58)
    print(" 파이썬      : %s" % sys.version.replace("\n", " "))
    print(" 실행 파일   : %s" % sys.executable)
    print(" 플랫폼      : %s" % sys.platform)
    print(" 스크립트    : %s" % os.path.abspath(__file__))
    print(" 콘솔 인코딩 : %s" % (getattr(sys.stdout, "encoding", "?") or "?"))
    print("-" * 58)

    ok = True
    if sys.version_info < (3, 8):
        print(" [X] 파이썬 3.8 이상이 필요합니다.")
        ok = False
    else:
        print(" [O] 파이썬 버전 OK")

    print(" [%s] numpy  %s" % ("O" if HAVE_NUMPY else "-",
                               np.__version__ if HAVE_NUMPY else "없음 (없어도 동작, 느림)"))
    print(" [%s] pandas %s" % ("O" if HAVE_PANDAS else "-",
                               pd.__version__ if HAVE_PANDAS else "없음 (없어도 동작, 읽기 2배 느림)"))
    try:
        import tkinter
        r = tkinter.Tk()
        r.destroy()
        print(" [O] tkinter 사용 가능 (GUI 실행 가능)")
    except ImportError:
        print(" [-] tkinter 없음 → GUI 불가, CLI만 사용 가능")
        print("     Linux: sudo apt install python3-tk")
    except Exception as e:
        print(" [-] tkinter는 있으나 창을 열 수 없습니다: %s" % e)
        print("     (원격 접속·디스플레이 없음 환경) CLI를 쓰세요.")

    print("-" * 58)
    print(" 자체 시험 변환…")
    import tempfile as _tf
    d = _tf.mkdtemp(prefix="inp2k_")
    ip = os.path.join(d, "selftest.inp")
    op = os.path.join(d, "selftest.k")
    try:
        with open(ip, "w", encoding="utf-8") as f:
            f.write(MINI_DECK)
        log = Log()
        r = convert_file(ip, op, dict(DEFAULT_OPT), log)
        txt = open(op, encoding="latin-1").read()
        need = ["*KEYWORD", "*PART", "*SECTION_SOLID", "*MAT_ELASTIC",
                "*NODE", "*ELEMENT_SOLID", "*BOUNDARY_SPC_SET", "*END"]
        miss = [k for k in need if k not in txt]
        if miss or r["counts"]["node"] != 8 or r["counts"]["solid"] != 1:
            print(" [X] 자체 시험 실패 (누락: %s)" % (", ".join(miss) or "없음"))
            ok = False
        else:
            print(" [O] 자체 시험 통과 — 절점 8, 솔리드 1, %d바이트 생성" % r["bytes"])
    except BrokenPipeError:
        raise
    except Exception:
        import traceback
        traceback.print_exc()
        print(" [X] 자체 시험 중 오류")
        ok = False
    finally:
        shutil.rmtree(d, ignore_errors=True)

    print("=" * 58)
    print(" 결과: %s" % ("정상 동작합니다." if ok else "문제가 있습니다. 위 내용을 확인하세요."))
    print("=" * 58)
    return 0 if ok else 1


# ============================================================
# CLI
# ============================================================
def main():
    for st in (sys.stdout, sys.stderr):
        try:
            st.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass
    ap = argparse.ArgumentParser(description="Abaqus INP → LS-DYNA keyword 변환기")
    ap.add_argument("input", nargs="?", help="Abaqus .inp 파일")
    ap.add_argument("-o", "--out", help="출력 .k 경로")
    ap.add_argument("--no-sets", action="store_true", help="세트 출력 안 함")
    ap.add_argument("--no-auto-sets", action="store_true", help="자동 ELSET_ALL/RIGID_Y/RIGID_Z 생성 생략")
    ap.add_argument("--no-contact", action="store_true", help="접촉·구속 변환 안 함")
    ap.add_argument("--no-ctrl", action="store_true", help=argparse.SUPPRESS)
    ap.add_argument("--tet10", action="store_true", help="C3D10 전용 프로퍼티에서 2차 사면체 유지 (혼합 프로퍼티는 코너 축약)")
    ap.add_argument("--shell", default="auto", choices=["auto", "2", "16"])
    ap.add_argument("--unit", default="mmts", choices=list(UNIT_DEFAULT))
    ap.add_argument("--mu", type=float, default=0.2, help="기본 마찰계수")
    ap.add_argument("--neg-elform-names", action="store_true",
                    help="PAD/TA/ADHESIVE 이름의 육면체 솔리드 프로퍼티를 ELFORM -1로")
    ap.add_argument("--check", action="store_true",
                    help="환경 진단 및 자체 시험 (실행이 안 될 때)")
    ap.add_argument("--shock", action="store_true", help="INP 없이 Shock 속도 .k 파일 생성 (s, mm/s)")
    ap.add_argument("--shock-g", type=float, default=25.0, help="Shock peak 가속도 (g), 기본 25")
    ap.add_argument("--shock-ms", type=float, default=15.0, help="Shock 펄스 시간 (ms), 기본 15")
    ap.add_argument("--shock-waveform", choices=[v for v, _ in SHOCK_WAVEFORMS], default="half-sine")
    ap.add_argument("--shock-direction", choices=[v[0] for v in SHOCK_DIRECTIONS], default="mx")
    ap.add_argument("--shock-points", type=int, default=SHOCK_POINTS, help="Shock 전체 데이터점 수 (0과 3T 포함, 중앙 구간 N-2점)")
    args = ap.parse_args()

    if args.shock:
        if args.input or args.check:
            ap.error("--shock는 INP 입력 또는 --check와 함께 사용하지 않습니다.")
        if args.unit != "mmts":
            ap.error("Shock 출력 단위는 mm·s·mm/s입니다. --unit mmts를 사용하세요.")
        try:
            profile = build_shock_profile(args.shock_g, args.shock_ms,
                                          args.shock_waveform, args.shock_direction, args.shock_points)
            result = write_shock_k(args.out or profile["filename"], args.shock_g,
                                   args.shock_ms, args.shock_waveform, args.shock_direction, args.shock_points)
        except (ValueError, OSError) as exc:
            ap.error(str(exc))
        print("  저장: %s" % result["out"])
        print("  0..%g s / %d점 / 최종 속도 %+.6f mm/s / Curve SFO=%+d" %
              (result["end_s"], len(result["times"]),
               0.0, result["sfo"]))
        print("  NSET_BC(100001) 필요: 기존 가진축 SPC 해제, LCID 701 중복 확인.")
        return 0
    if args.check:
        return run_check()
    if not args.input:
        return run_gui() or 0

    opt = dict(DEFAULT_OPT)
    opt.update(sets=not args.no_sets, contact=not args.no_contact, auto_sets=not args.no_auto_sets,
               ctrl=False, tet10=args.tet10,
               shell=args.shell, unit=args.unit, mu=args.mu,
               neg_elform_names=args.neg_elform_names)
    out = args.out or (os.path.splitext(args.input)[0] + ".k")

    def sink(lv, m):
        tag = {"info": "  ", "ok": "  ", "warn": "! ", "err": "X "}[lv]
        print(tag + m)

    log = Log(sink=sink)
    last = [0.0]

    PHN = {"read": "읽는 중", "convert": "변환 중", "write": "쓰는 중", "done": "완료"}

    def prog(ph, pct, text):
        now = time.time()
        if now - last[0] < 0.3 and ph != "done":
            return
        last[0] = now
        n = int(pct / 4)
        bar = "#" * n + "-" * (25 - n)
        sys.stderr.write("\r  [%s] %3.0f%%  %-9s %-22s" % (bar, pct, PHN.get(ph, ph), text))
        sys.stderr.flush()

    r = convert_file(args.input, out, opt, log, prog)
    sys.stderr.write("\r" + " " * 50 + "\r")
    print("  저장: %s (%.1f MB, %.1f초)"
          % (r["out"], r["bytes"] / 1048576.0, r["seconds"]))
    return 0


if __name__ == "__main__":
    _code = 0
    try:
        _code = main() or 0
    except SystemExit:
        raise
    except KeyboardInterrupt:
        _code = 1
    except BrokenPipeError:
        try:
            os.close(sys.stdout.fileno())
        except Exception:
            pass
        _code = 0
    except Exception:
        import traceback
        traceback.print_exc()
        print()
        print("오류가 발생했습니다. 위 내용을 함께 알려주시면 원인을 찾을 수 있습니다.")
        print("환경 확인:  python inp2k.py --check")
        _code = 1
    if _code and sys.platform.startswith("win"):
        try:
            input("\n엔터를 누르면 창이 닫힙니다...")
        except Exception:
            pass
    sys.exit(_code)
