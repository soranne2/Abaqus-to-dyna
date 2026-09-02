@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title INP2K - Abaqus INP to LS-DYNA K 변환기

rem ── 파이썬 찾기 ─────────────────────────────────────────────
set "PYEXE="
py -3 -c "import sys" >nul 2>&1 && set "PYEXE=py -3"
if not defined PYEXE (
  python -c "import sys" >nul 2>&1 && set "PYEXE=python"
)
if not defined PYEXE (
  python3 -c "import sys" >nul 2>&1 && set "PYEXE=python3"
)
if not defined PYEXE (
  for %%D in ("%LOCALAPPDATA%\Programs\Python" "C:\Python312" "C:\Python311" "C:\Python310") do (
    for /d %%P in ("%%~D\Python3*") do (
      if not defined PYEXE if exist "%%~P\python.exe" set "PYEXE=%%~P\python.exe"
    )
    if not defined PYEXE if exist "%%~D\python.exe" set "PYEXE=%%~D\python.exe"
  )
)

if not defined PYEXE (
  echo.
  echo   [X] 파이썬을 찾지 못했습니다.
  echo.
  echo   python.org 에서 Python 3.12 를 설치하세요.
  echo   설치 화면 맨 아래 "Add python.exe to PATH" 를 반드시 체크해야 합니다.
  echo.
  pause
  exit /b 1
)

rem ── 스크립트 확인 ───────────────────────────────────────────
if not exist "%~dp0inp2k.py" (
  echo.
  echo   [X] inp2k.py 를 찾을 수 없습니다.
  echo       이 bat 파일과 같은 폴더에 inp2k.py 가 있어야 합니다.
  echo.
  if exist "%~dp0inp2k.py.txt" (
    echo       inp2k.py.txt 가 보입니다. 확장자를 .py 로 바꿔 주세요.
    echo       ^(탐색기 - 보기 - 파일 확장명 체크 후 이름 변경^)
    echo.
  )
  dir /b "%~dp0*.py" 2>nul
  pause
  exit /b 1
)

rem ── 파이썬 버전 확인 ────────────────────────────────────────
%PYEXE% -c "import sys;sys.exit(0 if sys.version_info>=(3,8) else 1)" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   [X] 파이썬 3.8 이상이 필요합니다.
  %PYEXE% --version
  echo.
  pause
  exit /b 1
)

rem ── 선택 패키지 ─────────────────────────────────────────────
%PYEXE% -c "import numpy" >nul 2>&1
if errorlevel 1 (
  echo.
  echo   numpy / pandas 가 없습니다. 없어도 동작하지만 큰 모델에서 많이 느립니다.
  set /p ANS="  지금 설치할까요? (Y/N) "
  if /i "!ANS!"=="Y" (
    echo.
    %PYEXE% -m pip install --upgrade pip
    %PYEXE% -m pip install numpy pandas
    echo.
  )
)

rem ── 실행 ────────────────────────────────────────────────────
if "%~1"=="" (
  rem 더블클릭 - GUI
  %PYEXE% "%~dp0inp2k.py"
  if errorlevel 1 (
    echo.
    echo   GUI 실행에 실패했습니다. 진단을 실행합니다.
    echo.
    %PYEXE% "%~dp0inp2k.py" --check
    echo.
    pause
  )
) else (
  rem inp 파일을 이 bat 위에 끌어다 놓은 경우
  echo.
  echo   변환: %~nx1
  echo.
  %PYEXE% "%~dp0inp2k.py" %*
  echo.
  pause
)
exit /b 0
