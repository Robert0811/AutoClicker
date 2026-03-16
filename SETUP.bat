@echo off
title AutoClicker Pro - Installer
color 0B
cls

echo.
echo  ========================================
echo     AutoClicker Pro - Setup v1.0
echo  ========================================
echo.
echo  Verificare sistem...
echo.

REM Verifică dacă rulează ca administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo  [!] Rularea ca administrator este recomandata
    echo      pentru instalare completa.
    echo.
    echo  Continuam cu instalarea normala...
    timeout /t 2 >nul
)

REM Detectează arhitectura
if "%PROCESSOR_ARCHITECTURE%"=="AMD64" (
    set "ARCH=64-bit"
) else (
    set "ARCH=32-bit"
)

echo  [OK] Windows %ARCH% detectat
echo.

REM Verifică Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  [!] Python nu este instalat!
    echo.
    echo  AutoClicker necesita Python pentru prima rulare.
    echo.
    echo  Optiuni:
    echo    1. Instaleaza Python automat ^(recomandat^)
    echo    2. Anuleaza si instaleaza manual
    echo.
    choice /c 12 /n /m "  Alege optiunea (1 sau 2): "
    
    if errorlevel 2 (
        echo.
        echo  Deschid pagina de download Python...
        start https://www.python.org/downloads/
        echo.
        echo  Dupa instalare, ruleaza din nou acest setup.
        pause
        exit /b 1
    )
    
    echo.
    echo  [*] Descarc Python installer...
    
    REM Download Python
    if "%ARCH%"=="64-bit" (
        set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    ) else (
        set "PYTHON_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9.exe"
    )
    
    powershell -Command "& {[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PYTHON_URL%' -OutFile 'python_installer.exe'}"
    
    if not exist "python_installer.exe" (
        echo  [X] Descarcarea a esuat!
        echo      Te rog instaleaza Python manual.
        pause
        exit /b 1
    )
    
    echo  [*] Instalez Python...
    start /wait python_installer.exe /quiet InstallAllUsers=0 PrependPath=1 Include_test=0
    
    del python_installer.exe >nul 2>&1
    
    echo  [OK] Python instalat!
    echo.
    echo  Repornesc setup-ul...
    timeout /t 2 >nul
    "%~f0"
    exit /b 0
)

echo  [OK] Python detectat
python --version

echo.
echo  [*] Instalez dependente necesare...
python -m pip install --upgrade pip --quiet
python -m pip install --quiet pillow PyAutoGUI PyGetWindow PyMsgBox pynput pyperclip PyRect PyScreeze pytweening six

if errorlevel 1 (
    echo  [X] Instalarea dependentelor a esuat!
    pause
    exit /b 1
)

echo  [OK] Dependente instalate
echo.

REM Creează shortcut pe desktop
echo  [*] Creez shortcut pe Desktop...

set "SCRIPT_DIR=%~dp0"
set "DESKTOP=%USERPROFILE%\Desktop"
set "SHORTCUT=%DESKTOP%\AutoClicker Pro.lnk"

powershell -Command "$WS = New-Object -ComObject WScript.Shell; $SC = $WS.CreateShortcut('%SHORTCUT%'); $SC.TargetPath = 'pythonw'; $SC.Arguments = '\"%SCRIPT_DIR%autoclicker_gui.py\"'; $SC.WorkingDirectory = '%SCRIPT_DIR%'; $SC.IconLocation = 'shell32.dll,14'; $SC.Description = 'AutoClicker Pro - Click automat'; $SC.Save()"

if exist "%SHORTCUT%" (
    echo  [OK] Shortcut creat pe Desktop
) else (
    echo  [!] Nu s-a putut crea shortcut
)

echo.
echo  ========================================
echo     INSTALARE COMPLETA!
echo  ========================================
echo.
echo  AutoClicker Pro este gata de folosit!
echo.
echo  Cum sa-l folosesti:
echo    - Dublu-click pe "AutoClicker Pro" de pe Desktop
echo    - SAU ruleaza "Porneste_AutoClicker.bat"
echo    - Apasa Z pentru a porni/opri
echo.
echo  Apasa orice tasta pentru a porni AutoClicker...
pause >nul

start "" pythonw "%SCRIPT_DIR%autoclicker_gui.py"
