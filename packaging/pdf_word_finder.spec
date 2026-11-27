# -*- mode: python ; coding: utf-8 -*-
"""
Receta de PyInstaller para pdf-word-finder.

Construye dos ejecutables autónomos: la interfaz gráfica y el programa de
línea de órdenes. Lo más cómodo es usarla mediante scripts/construir.py, que
además empaqueta el resultado en un .zip con la licencia y la
documentación. A mano, en la carpeta del proyecto:

    pip install pyinstaller "pypdf[crypto]"
    pyinstaller --clean --noconfirm --distpath build/release \
        --workpath build/pyinstaller packaging/pdf_word_finder.spec

(Sin --distpath ni --workpath, PyInstaller escribe en dist/ y build/; el
proyecto deja todo en build/, y dist/ sin usar.)

Por omisión construye en MODO CARPETA: pdf-word-finder/ contiene los dos
ejecutables y, al lado, las bibliotecas que necesitan. Es lo recomendable.
Arranca bastante más rápido, porque no tiene que descomprimirse en cada
ejecución, y levanta muchas menos sospechas entre los antivirus, que
desconfían —con alguna razón— de un ejecutable que se descomprime solo en una
carpeta temporal y ejecuta código desde allí. La contrapartida es que hay que
distribuir la carpeta entera, comprimida.

Para obtener en su lugar un ejecutable único por programa:

    PWF_ONEFILE=1 pyinstaller packaging/pdf_word_finder.spec          (macOS y Linux)
    set PWF_ONEFILE=1 && pyinstaller packaging/pdf_word_finder.spec   (Windows, cmd)
    $env:PWF_ONEFILE=1; pyinstaller packaging/pdf_word_finder.spec    (Windows, PowerShell)

(con las mismas opciones --distpath y --workpath). El resultado queda en
build/release/. PyInstaller NO compila para otros sistemas: hay
que ejecutarlo en Windows para obtener el .exe, en macOS para el .app y en
Linux para el binario correspondiente. Véase el README, §11.

El código está en el paquete src/pdf_word_finder. Los módulos de un paquete
no pueden ejecutarse sueltos (sus importaciones relativas fallan), así que
los ejecutables arrancan desde dos archivos mínimos que hay junto a esta
receta, lanzador_cli.py y lanzador_gui.py, y el paquete se encuentra por
`pathex`. El nombre de cada ejecutable se declara en `name`, más abajo, y es
independiente del nombre del archivo.

© Nicolás Vaughan 2026. Licencia GNU GPL v3 o posterior.
"""

import os
import re
from pathlib import Path

# Las rutas se toman de la carpeta de esta receta (SPECPATH, que define
# PyInstaller), no de la carpeta desde donde se la llama.
AQUÍ = Path(SPECPATH)
SRC = AQUÍ.parent / "src"

# La versión se lee del propio paquete: es su única fuente. Se extrae con
# una expresión regular en vez de importar el módulo, porque importarlo
# ejecutaría código durante la construcción sin necesidad alguna.
VERSION = re.search(
    r'^__version__\s*=\s*"([^"]+)"',
    (SRC / "pdf_word_finder" / "__init__.py").read_text(encoding="utf-8"),
    re.M,
).group(1)

# Modo carpeta por omisión; archivo único solo si se pide expresamente.
UN_SOLO_ARCHIVO = bool(os.environ.get("PWF_ONEFILE"))

# Los lanzadores importan el paquete con un `import` corriente, de modo que
# PyInstaller lo descubre solo al analizar el código, y con él pypdf y sus
# dependencias. No hacen falta ni `datas` ni `hiddenimports`.

descartes = ["matplotlib", "numpy", "PIL", "pytest"]

# PyMuPDF, en cambio, sí queda fuera aunque esté instalado: el paquete lo carga
# con importlib.import_module y PyInstaller no puede verlo. Es lo deseable por
# omisión —añade unos 40 MB—, pero si quiere incluirlo para que el ejecutable
# extraiga mejor el texto, ponga hiddenimports=["pymupdf"] en el Analysis de
# la interfaz.

# --- análisis -------------------------------------------------------------

a_gui = Analysis(
    [str(AQUÍ / "lanzador_gui.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    excludes=descartes,
    noarchive=False,
)
pyz_gui = PYZ(a_gui.pure)

a_cli = Analysis(
    [str(AQUÍ / "lanzador_cli.py")],
    pathex=[str(SRC)],
    binaries=[],
    datas=[],
    hiddenimports=[],
    excludes=descartes + ["tkinter"],   # este no necesita interfaz gráfica
    noarchive=False,
)
pyz_cli = PYZ(a_cli.pure)

# --- ejecutables ----------------------------------------------------------
# En modo carpeta el ejecutable lleva solo el código y las bibliotecas quedan
# fuera, recogidas por el COLLECT del final; en modo archivo único va todo
# dentro. De ahí que los argumentos cambien según el modo.

contenido_gui = [a_gui.binaries, a_gui.datas] if UN_SOLO_ARCHIVO else []
contenido_cli = [a_cli.binaries, a_cli.datas] if UN_SOLO_ARCHIVO else []

exe_gui = EXE(
    pyz_gui,
    a_gui.scripts,
    *contenido_gui,
    [],
    exclude_binaries=not UN_SOLO_ARCHIVO,
    name="pdf-word-finder-gui",
    debug=False,
    strip=False,
    upx=False,
    console=False,          # sin ventana de consola detrás de la interfaz
    argv_emulation=False,   # póngalo en True si quiere arrastrar PDF al icono
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,              # ruta a un .ico (Windows) o .icns (macOS)
)

exe_cli = EXE(
    pyz_cli,
    a_cli.scripts,
    *contenido_cli,
    [],
    exclude_binaries=not UN_SOLO_ARCHIVO,
    name="pdf-word-finder",
    debug=False,
    strip=False,
    upx=False,
    console=True,           # este sí necesita consola
    icon=None,
)

# --- recolección (solo en modo carpeta) -----------------------------------
# Los dos programas se recogen en una sola carpeta, de modo que compartan el
# intérprete y las bibliotecas en vez de duplicarlos.

if not UN_SOLO_ARCHIVO:
    coll = COLLECT(
        exe_gui,
        a_gui.binaries,
        a_gui.datas,
        exe_cli,
        a_cli.binaries,
        a_cli.datas,
        strip=False,
        upx=False,
        name="pdf-word-finder",
    )

# --- paquete .app de macOS ------------------------------------------------
# En modo carpeta envuelve la carpeta recogida; en modo archivo único, el
# ejecutable suelto.

app = BUNDLE(
    coll if not UN_SOLO_ARCHIVO else exe_gui,
    name="pdf-word-finder.app",
    icon=None,
    bundle_identifier="co.edu.uniandes.pdf-word-finder",
    info_plist={
        "CFBundleName": "pdf-word-finder",
        "CFBundleDisplayName": "pdf-word-finder",
        "CFBundleShortVersionString": VERSION,
        "CFBundleVersion": VERSION,
        "NSHumanReadableCopyright": "© Nicolás Vaughan 2026. Licencia GNU GPL v3 o posterior.",
        "NSHighResolutionCapable": True,
    },
)
