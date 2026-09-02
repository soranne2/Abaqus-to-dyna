@echo off
setlocal EnableDelayedExpansion
cd /d "%~dp0"
title INP2K 진단

echo ==========================================================
echo  INP2K 진단
echo ==========================================================
echo.

set "PYEXE="
py -3 -c "import sys" >nul 2>&1 && set "PYEXE=py -3"
if not defined PYEXE (
  python -c "import sys" >nul 2>&1 && set "PYEXE=python"
)
if not defined PYEXE (
  python3 -c "import sys" >nul 2>&1 && set "PYEXE=python3"
)

if not defined PYEXE (
  echo  [X] 파이썬을 찾지 못했습니다.
  echo.
  echo   확인할 것
  echo     1. python.org 에서 파이썬을 설치했는지
  echo     2. 설치할 때 "Add python.exe to PATH" 를 체크했는지
  echo        체크를 놓쳤다면 파이썬을 다시 설치하거나
  echo        Modify 에서 경로 추가를 켜 주세요.
  echo.
  echo   설치되어 있는데도 이 메시지가 나오면 아래를 실행해 보세요.
  echo     where python
  echo     where py
  echo.
  pause
  exit /b 1
)

echo  찾은 파이썬 : %PYEXE%
%PYEXE% --version
echo  현재 폴더   : %~dp0
echo.

if not exist "%~dp0inp2k.py" (
  echo  [X] inp2k.py 가 이 폴더에 없습니다.
  echo.
  if exist "%~dp0inp2k.py.txt" (
    echo      inp2k.py.txt 가 보입니다. 확장자를 .py 로 바꿔 주세요.
    echo      탐색기 - 보기 - 파일 확장명 체크 후 이름 변경
    echo.
  )
  echo  이 폴더의 파일 목록
  dir /b "%~dp0"
  echo.
  pause
  exit /b 1
)

%PYEXE% "%~dp0inp2k.py" --check
echo.
pause
