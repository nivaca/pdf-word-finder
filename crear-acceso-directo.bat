@echo off
rem ---------------------------------------------------------------------
rem  pdf-word-finder - crear el acceso en el menu de inicio
rem
rem  Se hace doble clic una sola vez. Deja el programa en el menu de
rem  inicio (y, si se quiere, en el escritorio), de modo que despues se
rem  abra como cualquier otra aplicacion.
rem
rem  El acceso NO apunta a este .bat sino directamente a pythonw.exe, que
rem  es lo que conviene por dos razones: no queda una ventana negra de
rem  consola detras, y Windows no somete los accesos directos al filtro
rem  que aplica a los archivos de ordenes bajados de internet.
rem
rem  (c) Nicolas Vaughan 2026. Licencia MIT.
rem ---------------------------------------------------------------------
rem  NOTA: sin tildes a proposito (la consola de Windows no usa UTF-8) y
rem  con finales de renglon CRLF.
rem ---------------------------------------------------------------------

setlocal
cd /d "%~dp0"

if not exist "pdf_word_finder_gui.py" goto :sin_programa

rem --- localizar Python -------------------------------------------------
rem  Se comprueba ejecutandolo: Windows 11 trae un "python" de mentira en
rem  WindowsApps que solo sirve para abrir la Store.
set "PYW="
py -3 -c "import sys" >nul 2>&1 && set "PYW=pyw"
if not defined PYW (
    python -c "import sys" >nul 2>&1 && set "PYW=pythonw"
)
if not defined PYW goto :sin_python

rem  Se necesita la ruta completa: un acceso directo no busca en el PATH.
for /f "delims=" %%r in ('%PYW% -c "import sys; print(sys.executable)" 2^>nul') do set "RUTAPYW=%%r"
if not defined RUTAPYW goto :sin_python

rem  sys.executable puede devolver python.exe; se prefiere pythonw.exe, que
rem  es el mismo interprete sin ventana de consola.
set "RUTAPYW=%RUTAPYW:python.exe=pythonw.exe%"
if not exist "%RUTAPYW%" goto :sin_python

echo.
echo   Python encontrado en:
echo     %RUTAPYW%
echo.

rem --- menu de inicio ---------------------------------------------------
call :crear "Programs"
if errorlevel 1 goto :fallo

echo   Acceso creado en el menu de inicio.
echo.
choice /C SN /N /M "   Desea tambien un acceso en el escritorio? (S/N): "
if errorlevel 2 goto :fin

call :crear "Desktop"
if errorlevel 1 goto :fallo
echo.
echo   Acceso creado en el escritorio.

:fin
echo.
echo   Listo. Busque "pdf-word-finder" en el menu de inicio.
echo.
pause
exit /b 0


rem =====================================================================
rem  Subrutina: crea el .lnk en la carpeta especial que se le indique
rem  ("Programs" = menu de inicio del usuario; "Desktop" = escritorio)
rem =====================================================================
:crear
rem  En vez de meter toda la orden de PowerShell entre comillas dentro del
rem  .bat -donde cmd la parte en pedazos y el entrecomillado se vuelve
rem  ilegible- se escribe un guion temporal y se ejecuta. Un archivo creado
rem  aqui mismo no lleva marca de procedencia, de modo que -ExecutionPolicy
rem  Bypass basta para que corra.
set "PS1=%TEMP%\pwf_acceso.ps1"

> "%PS1%" echo $carpeta = [Environment]::GetFolderPath('%~1')
>>"%PS1%" echo $enlace = Join-Path $carpeta 'pdf-word-finder.lnk'
>>"%PS1%" echo $c = (New-Object -ComObject WScript.Shell).CreateShortcut($enlace)
>>"%PS1%" echo $c.TargetPath = '%RUTAPYW%'
>>"%PS1%" echo $c.Arguments = '"%CD%\pdf_word_finder_gui.py"'
>>"%PS1%" echo $c.WorkingDirectory = '%CD%'
>>"%PS1%" echo $c.IconLocation = '%RUTAPYW%,0'
>>"%PS1%" echo $c.Description = 'Busca palabras en un PDF e informa la pagina impresa'
>>"%PS1%" echo $c.Save()

powershell -NoProfile -ExecutionPolicy Bypass -File "%PS1%"
set "RESULTADO=%errorlevel%"
del "%PS1%" >nul 2>&1
exit /b %RESULTADO%


rem =====================================================================
rem  Errores
rem =====================================================================
:sin_python
echo.
echo   No se encontro Python en este equipo.
echo.
echo   Ejecute primero pdf-word-finder.bat, que se ofrece a instalarlo,
echo   y vuelva luego a este archivo.
echo.
pause
exit /b 1

:sin_programa
echo.
echo   Este archivo debe estar en la misma carpeta que:
echo.
echo     pdf_word_finder.py
echo     pdf_word_finder_gui.py
echo.
pause
exit /b 1

:fallo
echo.
echo   No se pudo crear el acceso directo.
echo.
echo   Si el equipo restringe la ejecucion de PowerShell, hagalo a mano:
echo   clic derecho sobre pdf-word-finder.bat, "Mostrar mas opciones",
echo   "Crear acceso directo", y arrastre el resultado a:
echo.
echo     %%APPDATA%%\Microsoft\Windows\Start Menu\Programs
echo.
pause
exit /b 1
