# Registro de cambios

Los cambios notables de pdf-word-finder. Las versiones publicadas están en
[GitHub](https://github.com/nivaca/pdf-word-finder/releases) (la 1.1, la
1.4, la 1.5 y la 1.6 tienen página de publicación; de la 1.2 a la 1.23 son solo etiquetas).
El programa y su README están en español; hay un README en inglés,
`README_en.md`.

## 1.6 — 2026-11-21

- **Se requiere Python 3.14 o posterior**: en `pyproject.toml`, en los
  README, en los lanzadores de Windows (un Python más viejo cuenta como si
  no hubiera ninguno, y se ofrecen a instalar uno nuevo) y en el propio
  programa, que lo dice en un renglón en vez de fallar con un error de
  sintaxis.
- **El proyecto se reorganiza en carpetas.** El programa es el paquete
  `src/pdf_word_finder/`, dividido en módulos: `extraction`, `text`,
  `patterns`, `search`, `report`, `cli` y `gui`. Un `pyproject.toml` lo
  hace instalable (`pip install .`, `pipx install .`) con dos órdenes,
  `pdf-word-finder` y `pdf-word-finder-gui`. La receta de PyInstaller y sus
  dos lanzadores están en `packaging/`, `subir_version.py` en `scripts/`, y
  los dos `.bat` en `windows/`.
- La receta `pdf_word_finder.spec` está ahora en el repositorio; antes el
  `.gitignore` la dejaba fuera.
- Las funciones del paquete lanzan excepciones (`PdfError`,
  `PatternError`) en vez de terminar el programa, y la línea de órdenes y la
  ventana comparten la búsqueda (`search()`), el informe y la exportación a
  TXT y CSV. La ventana ya no tiene su propia copia del bucle de búsqueda ni
  de la exportación a CSV.
- `scripts/construir.py` construye los ejecutables y los empaqueta, con la
  licencia, los README, los registros de cambios y `docs/`, en
  `dist/pdf-word-finder-SISTEMA-VERSIÓN.zip`.
- Pruebas: 43, con pytest, en `tests/`. Generan sus propios PDF pequeños.
- La dependencia es `pypdf[crypto]`, que abre también los PDF cifrados con
  AES.
- En la ventana, un ancho de contexto que no sea un número ya no detiene la
  búsqueda: se usa 60.
- El README ya no describe el flujo de trabajo de GitHub, que se quitó en
  la 1.4; el §11 explica cómo construir en cada sistema y publicar a mano.
- Dos documentos de descripción en `docs/`: `DESCRIPTION.md`, en inglés,
  sobre cómo se hizo el programa, y `DESCRIPCIÓN_es.md`, una descripción en
  español.
- El paquete para Linux se construye con Python 3.15. Para esta versión no
  hay paquete para Windows.

## 1.5 — 2026-11-21

- Una lista del software libre que usa el programa, con versiones y
  licencias: `docs/LICENCIAS_DE_TERCEROS_es.md` y, en inglés,
  `docs/THIRD_PARTY_LICENSES.md`. El README remite a ella, y el paquete la
  lleva, junto con `LICENSE` y los README.
- El paquete para Linux se construye con Python 3.15. Para esta versión no
  hay paquete para Windows.
- **La licencia es ahora la GNU GPL, versión 3 o posterior** (antes era
  MIT): `LICENSE`, el README, los encabezados de los scripts y
  `__license__`.
- Una traducción al inglés del README, `README_en.md`.
- `crear-acceso-directo.bat` crea un acceso directo en el menú Inicio de
  Windows (y, si se quiere, en el escritorio), que ejecuta `pythonw.exe`
  con la ventana directamente, así que no queda detrás ninguna ventana de
  consola y Windows no lo bloquea como un `.bat` descargado.
- `subir_version.py` cambia la versión en todos los lugares de los README
  (`subir_version.py 1.5`), la muestra (`--mostrar`) y comprueba que los
  README coincidan con `__version__` (`--revisar`).

## 1.4 — 2026-08-20

- La versión está en un solo lugar, `__version__` en
  `pdf_word_finder.py`; la ventana y la receta de PyInstaller la toman de
  allí, y los encabezados de los scripts ya no la repiten. El README tiene
  una sección sobre la versión.
- El flujo de construcción `build.yml` ya no está en el repositorio.

## 1.23 — 2026-08-20

- El lanzador de Windows, `pdf-word-finder.bat`, abre el programa justo
  después de instalar Python, sin empezar de nuevo. Como el Python nuevo
  aún no está en el PATH de esa ventana, lo busca en las carpetas donde
  suele instalarse, de la versión más reciente hacia atrás.

## 1.22 — 2026-08-20

- El lanzador de Windows instala el Python más reciente que ofrezca
  winget (prueba de `Python.Python.3.19` hasta `3.12`), en lugar de
  instalar siempre el 3.12.
- El README se reescribió en partes.

## 1.21 — 2026-08-20

- El lanzador de Windows prueba Python ejecutándolo, no con `where`:
  Windows 11 trae un `python` falso que solo abre la Store. Si falla la
  instalación de Python con winget para el usuario, lo intenta de nuevo
  de la manera normal, y comprueba que Python funcione antes de seguir.
- El flujo de construcción se ejecuta también con las etiquetas sin `v`
  (`1.2` tanto como `v1.2`).

## 1.2 — 2026-08-20

- `--sort` ordena la lista alfabéticamente, y `--txt FILE` la exporta a
  un archivo de texto; la ventana puede guardar la lista como texto o
  como CSV.
- El texto de un PDF se extrae una vez y se guarda para las búsquedas
  siguientes.
- PyMuPDF se importa como `pymupdf`, no con el nombre antiguo `fitz`.
- La ventana tiene un cuadro «Acerca de…», con la versión y los datos
  técnicos (Python, Tcl/Tk, pypdf, PyMuPDF y el sistema), y hace la
  búsqueda en segundo plano.
- Los scripts pasan a llamarse `pdf_word_finder.py` y
  `pdf_word_finder_gui.py`, para que uno pueda importarse desde el otro.
- `pdf-word-finder.bat`, un lanzador para Windows que instala Python (con
  winget, o si no desde la Store) y pypdf cuando faltan, y abre la
  ventana.
- Ejecutables hechos con PyInstaller (una carpeta, o un solo archivo con
  `PWF_ONEFILE=1`), y un flujo de GitHub, `build.yml`, que los construye
  para Windows, macOS y Linux y los adjunta a una versión publicada. El
  README explica cómo abrirlos cuando Windows o macOS se niegan a hacerlo.

## 1.1 — 2026-08-18

- Primera versión: un programa de línea de comandos que busca una lista
  de palabras, frases o expresiones regulares en un PDF y dice en qué
  páginas aparece cada una. Da los números de página rotulados del árbol
  `/PageLabels` (los números impresos en las páginas), advierte cuando el
  PDF no los tiene, y con `--show-logical` añade entre corchetes la
  página secuencial. Une las palabras cortadas con guion al final del
  renglón, y tiene las opciones `--words-file`, `--regex`, `--regex-word`,
  `--substring`, `--case-sensitive`, `--ignore-accents`, `--context` y
  `--csv`.
- El informe es un renglón por término, con las páginas separadas por
  comas, como en un índice; `--detailed` da el informe extenso, con el
  recuento de cada término. Los términos no encontrados y las advertencias
  van a la salida de errores, así que un resultado redirigido es un
  índice limpio.
- Una ventana sencilla (Tkinter), `pdf-word-finder-gui.py`, que usa las
  funciones del programa de línea de comandos y ofrece las mismas
  opciones.
