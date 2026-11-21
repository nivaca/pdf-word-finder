@echo off
rem ---------------------------------------------------------------------
rem  pdf-word-finder - lanzador para Windows
rem
rem  Se hace doble clic en este archivo y se abre la ventana del programa.
rem  Si falta Python 3.14 o posterior, se ofrece instalarlo; si falta
rem  pypdf, se instala solo.
rem  Tras instalar Python el lanzador sigue adelante sin que haya que
rem  volver a empezar.
rem
rem  (c) Nicolas Vaughan 2026. Licencia GNU GPL v3 o posterior.
rem ---------------------------------------------------------------------
rem  NOTA: este archivo se escribe sin tildes a proposito. La consola de
rem  Windows no usa UTF-8 por omision y los acentos saldrian ilegibles.
rem  Conserve tambien los finales de renglon CRLF si lo edita.
rem ---------------------------------------------------------------------

setlocal

rem --- comprobar que el programa esta donde debe ------------------------
rem  Este archivo vive en la carpeta "windows" del proyecto; el programa,
rem  en la carpeta "src", al lado. Se trabaja desde "src" porque
rem  "python -m" busca alli el paquete.
cd /d "%~dp0..\src" 2>nul || goto :sin_programa
if not exist "pdf_word_finder\gui.py" goto :sin_programa
if not exist "pdf_word_finder\cli.py" goto :sin_programa

rem --- localizar Python -------------------------------------------------
call :buscar_python
if defined PY goto :con_python

call :instalar_python
if defined PY goto :con_python
goto :fin_sin_python


rem =====================================================================
rem  Con Python ya disponible: dependencia y arranque
rem =====================================================================
:con_python

%PY% -c "import tkinter" >nul 2>&1
if errorlevel 1 goto :sin_tkinter

%PY% -c "import pypdf" >nul 2>&1
if errorlevel 1 (
    echo.
    echo   Preparando el programa. Esto solo ocurre la primera vez...
    echo.
    %PY% -m pip install --user "pypdf[crypto]"
    if errorlevel 1 goto :fallo_pip
    echo.
    echo   Listo.
)

rem  "pythonw" en vez de "python" para que no quede detras una ventana
rem  negra de consola.
start "" %PYW% -m pdf_word_finder.gui
exit /b 0


rem =====================================================================
rem  Subrutina: deja PY y PYW definidos, o vacios si no hay Python
rem =====================================================================
:buscar_python
rem  No se usa "where": Windows 11 trae un "python" de mentira, un archivo
rem  vacio en WindowsApps cuyo unico oficio es abrir la Store. "where" lo
rem  encuentra y uno creeria que hay Python. Por eso se comprueba
rem  EJECUTANDOLO: solo un Python de verdad responde sin error. La misma
rem  prueba descarta las versiones anteriores a la 3.14, que el programa
rem  no admite: para el lanzador cuentan como si no hubiera Python.
set "PY="
set "PYW="
set "PRUEBA=import sys; sys.exit(sys.version_info < (3, 14))"
py -3 -c "%PRUEBA%" >nul 2>&1 && (set "PY=py -3" & set "PYW=pyw -3" & exit /b 0)
python -c "%PRUEBA%" >nul 2>&1 && (set "PY=python" & set "PYW=pythonw" & exit /b 0)

rem  Recien instalado, Python aun no figura en el PATH de esta ventana:
rem  la lista de programas se hereda al abrirla y no se actualiza sola.
rem  Se busca entonces en las carpetas donde suele quedar.
rem
rem  Se recorre una lista explicita de versiones, de mayor a menor, y NO
rem  el orden alfabetico que daria "dir /o-n": alfabeticamente "Python39"
rem  va despues de "Python313", de modo que se elegiria la version vieja.
for %%n in (319 318 317 316 315 314) do (
    if not defined PY if exist "%LOCALAPPDATA%\Programs\Python\Python%%n\python.exe" (
        set PY="%LOCALAPPDATA%\Programs\Python\Python%%n\python.exe"
    )
    if not defined PY if exist "%ProgramFiles%\Python%%n\python.exe" (
        set PY="%ProgramFiles%\Python%%n\python.exe"
    )
)
if not defined PY exit /b 0

rem  El pythonw de al lado, para abrir sin ventana de consola detras.
for %%q in (%PY%) do set PYW="%%~dpqpythonw.exe"
for %%q in (%PYW%) do if not exist "%%~q" set PYW=%PY%
exit /b 0


rem =====================================================================
rem  Instalacion de Python
rem =====================================================================
:instalar_python
echo.
echo ============================================================
echo   pdf-word-finder necesita Python 3.14 o posterior
echo ============================================================
echo.
echo   Python es un programa gratuito de uso corriente. Ocupa unos
echo   100 MB y se instala en dos o tres minutos.
echo.
choice /C SN /N /M "   Desea instalarlo ahora? (S/N): "
if errorlevel 2 exit /b 0

where winget >nul 2>&1
if errorlevel 1 goto :via_store

rem  winget identifica cada serie de Python por separado (Python.Python.3.14,
rem  .3.15...), de modo que no hay un identificador generico que signifique
rem  "la mas reciente". Se prueban de mayor a menor y se toma la primera que
rem  exista en el catalogo: asi el lanzador no envejece cada vez que sale una
rem  version nueva. Si algun dia hiciera falta, basta anadir numeros al
rem  principio de esta lista. Termina en 3.14, la minima que admite el
rem  programa.
set "PYID="
for %%v in (3.19 3.18 3.17 3.16 3.15 3.14) do (
    if not defined PYID (
        winget show --id Python.Python.%%v --exact >nul 2>&1 && set "PYID=Python.Python.%%v"
    )
)
if not defined PYID goto :via_store

echo.
echo   Instalando %PYID%. Puede tardar unos minutos...
echo   (Si Windows pide permiso, acepte.)
echo.
winget install --id %PYID% --exact --scope user --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo.
    echo   Reintentando de otro modo. Si Windows pide permiso, acepte.
    echo.
    winget install --id %PYID% --exact --accept-package-agreements --accept-source-agreements
)

call :buscar_python
if defined PY (
    echo.
    echo   Python instalado. Continuando...
    echo.
)
exit /b 0

:via_store
echo.
echo   Se abrira la Microsoft Store en la pagina de Python.
echo.
echo     1. Pulse "Obtener" o "Instalar".
echo     2. Espere a que termine.
echo     3. Cierre la Store y vuelva a esta ventana.
echo.
pause
rem  Sin espacios ni codificacion en la direccion: menos que pueda fallar.
start "" "ms-windows-store://search?query=python"
echo.
pause
call :buscar_python
exit /b 0


rem =====================================================================
rem  Salidas con explicacion
rem =====================================================================
:fin_sin_python
echo.
echo   No se pudo dejar Python listo en esta ventana.
echo.
echo   Si acaba de instalarlo, cierre esta ventana y vuelva a hacer
echo   doble clic en pdf-word-finder.bat: en una ventana nueva
echo   Windows ya lo reconoce.
echo.
echo   Si ya tenia Python, compruebe que sea la version 3.14 o
echo   posterior: las anteriores no sirven.
echo.
pause
exit /b 1

:sin_tkinter
echo.
echo   Se encontro Python, pero le falta el componente "tkinter",
echo   necesario para la ventana del programa.
echo.
echo   Suele ocurrir con instalaciones minimas. La version de la
echo   Microsoft Store lo trae; conviene instalar esa.
echo.
pause
exit /b 1

:sin_programa
echo.
echo   Faltan archivos. Este archivo debe estar en la carpeta
echo   "windows" del programa, y al lado, en la carpeta "src", el
echo   programa mismo:
echo.
echo     src\pdf_word_finder\gui.py
echo     src\pdf_word_finder\cli.py   (y los demas)
echo     windows\pdf-word-finder.bat   (este archivo)
echo.
echo   Si descomprimio solo una parte del ZIP, descomprimalo entero.
echo.
pause
exit /b 1

:fallo_pip
echo.
echo   No se pudo instalar el componente "pypdf".
echo.
echo   Suele deberse a que el equipo esta detras de un proxy o sin
echo   conexion. Pruebe de nuevo conectado a la red de la universidad,
echo   o pida ayuda a la Direccion de Tecnologia con esta orden:
echo.
echo     %PY% -m pip install --user "pypdf[crypto]"
echo.
pause
exit /b 1
