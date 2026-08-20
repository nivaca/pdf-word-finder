@echo off
rem ---------------------------------------------------------------------
rem  pdf-word-finder - lanzador para Windows
rem
rem  Se hace doble clic en este archivo y se abre la ventana del programa.
rem  Si falta Python, se ofrece instalarlo; si falta pypdf, se instala solo.
rem
rem  (c) Nicolas Vaughan 2026. Licencia MIT.
rem ---------------------------------------------------------------------
rem  NOTA: este archivo se escribe sin tildes a proposito. La consola de
rem  Windows no usa UTF-8 por omision y los acentos saldrian ilegibles.
rem  Conserve tambien los finales de renglon CRLF si lo edita.
rem ---------------------------------------------------------------------

setlocal
cd /d "%~dp0"

rem --- comprobar que el programa esta al lado ---------------------------
if not exist "pdf_word_finder_gui.py" goto :sin_programa
if not exist "pdf_word_finder.py" goto :sin_programa

rem --- localizar Python -------------------------------------------------
rem  El lanzador "py" viene con la instalacion oficial; "python" a secas
rem  es lo que deja la version de la Microsoft Store.

call :buscar_python
if not defined PY goto :ofrecer_python

rem --- comprobar tkinter ------------------------------------------------
%PY% -c "import tkinter" >nul 2>&1
if errorlevel 1 goto :sin_tkinter

rem --- instalar pypdf la primera vez ------------------------------------
%PY% -c "import pypdf" >nul 2>&1
if errorlevel 1 (
    echo.
    echo Preparando el programa. Esto solo ocurre la primera vez...
    echo.
    %PY% -m pip install --user pypdf
    if errorlevel 1 goto :fallo_pip
    echo.
    echo Listo.
)

rem --- abrir la ventana -------------------------------------------------
rem  "pythonw" en vez de "python" para que no quede detras una ventana
rem  negra de consola.
start "" %PYW% "pdf_word_finder_gui.py"
exit /b 0


rem =====================================================================
rem  Subrutina: deja PY y PYW definidos, o vacios si no hay Python
rem =====================================================================
:buscar_python
rem  No se usa "where": Windows 11 trae un "python" de mentira, un archivo
rem  vacio en WindowsApps cuyo unico oficio es abrir la Store. "where" lo
rem  encuentra y uno creeria que hay Python. Por eso se comprueba
rem  EJECUTANDOLO: solo un Python de verdad responde sin error.
set "PY="
set "PYW="
py -3 -c "import sys" >nul 2>&1 && (set "PY=py -3" & set "PYW=pyw -3" & exit /b 0)
python -c "import sys" >nul 2>&1 && (set "PY=python" & set "PYW=pythonw" & exit /b 0)
exit /b 0


rem =====================================================================
rem  Instalacion de Python
rem =====================================================================
:ofrecer_python
echo.
echo ============================================================
echo   pdf-word-finder necesita Python
echo ============================================================
echo.
echo   Python es un programa gratuito de uso corriente. Ocupa unos
echo   100 MB y se instala en dos o tres minutos.
echo.
choice /C SN /N /M "   Desea instalarlo ahora? (S/N): "
if errorlevel 2 goto :cancelado

rem  Se prueba winget, que viene con Windows 11 y no necesita que el
rem  usuario elija nada. Si no esta, o falla, se recurre a la Store.
where winget >nul 2>&1
if errorlevel 1 goto :via_store

echo.
echo   Instalando Python. Puede tardar unos minutos...
echo   (Si Windows pide permiso, acepte.)
echo.
rem  Primero por ambito de usuario, que no pide permisos de administrador.
rem  Algunos paquetes no lo admiten; entonces se reintenta del modo normal,
rem  que puede pedir permiso. Si tampoco, queda la Store.
winget install --id Python.Python.3.12 --exact --scope user --accept-package-agreements --accept-source-agreements
if errorlevel 1 (
    echo.
    echo   Reintentando de otro modo. Si Windows pide permiso, acepte.
    echo.
    winget install --id Python.Python.3.12 --exact --accept-package-agreements --accept-source-agreements
)
if errorlevel 1 goto :via_store

rem  winget puede terminar bien y aun asi no dejar Python utilizable en
rem  esta ventana. Se comprueba de veras antes de cantar victoria.
call :buscar_python
if not defined PY goto :reabrir
goto :reabrir

:via_store
echo.
echo   Se abrira la Microsoft Store en la pagina de Python.
echo.
echo     1. Pulse "Obtener" o "Instalar".
echo     2. Espere a que termine.
echo     3. Cierre la Store y vuelva aqui.
echo.
pause
rem  Sin espacios ni codificacion en la direccion: menos que pueda fallar.
start "" "ms-windows-store://search?query=python"
echo.
echo   Cuando haya terminado la instalacion, cierre esta ventana y
echo   vuelva a hacer doble clic en pdf-word-finder.bat
echo.
pause
exit /b 1

:reabrir
echo.
echo ============================================================
echo   Python quedo instalado.
echo ============================================================
echo.
echo   Cierre esta ventana y vuelva a hacer doble clic en
echo   pdf-word-finder.bat para abrir el programa.
echo.
echo   (Hace falta cerrarla porque Windows solo reconoce los
echo   programas recien instalados en ventanas nuevas.)
echo.
pause
exit /b 0

:cancelado
echo.
echo   De acuerdo, no se instalo nada.
echo.
echo   Sin Python este lanzador no puede abrir el programa. La otra
echo   via es pedirle a quien se lo envio la version ejecutable.
echo.
pause
exit /b 1


rem =====================================================================
rem  Errores
rem =====================================================================
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
echo   Faltan archivos. En esta misma carpeta deben estar:
echo.
echo     pdf_word_finder.py
echo     pdf_word_finder_gui.py
echo     pdf-word-finder.bat   (este archivo)
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
echo     %PY% -m pip install --user pypdf
echo.
pause
exit /b 1
