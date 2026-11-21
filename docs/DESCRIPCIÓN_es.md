# pdf-word-finder 1.6: descripción

## Análisis

pdf-word-finder busca en un PDF una lista de palabras, frases o expresiones regulares e informa en qué páginas aparece cada una. Lo que lo distingue de la búsqueda de un visor de PDF es el número de página que da: el impreso en la página, tomado del árbol `/PageLabels` del archivo, y no la posición de la página dentro del archivo. En un libro corriente los dos números no coinciden (los preliminares van en romanas, el cuerpo vuelve a empezar en 1), y solo el impreso sirve para hacer un índice o para encontrar un pasaje en el libro de papel.

Nicolas Vaughan lo escribió en agosto de 2026 para ese trabajo, los índices onomásticos y de materias de una edición, y de ahí salieron los requisitos. La salida tenía que tener la forma de un índice, un renglón por término con sus páginas separadas por comas, lista para copiarse; las advertencias, aparte, para que la salida redirigida a un archivo quedara limpia. Si el PDF no tiene rótulos, el programa debe decirlo, y no fingir una numeración que no existe. Había que encontrar las palabras partidas por un guion a final de renglón, las frases cortadas entre dos renglones y las formas con o sin tildes, y admitir expresiones regulares para las flexiones latinas (`re:virtu(s|tem|tis)`). La lista debía poder ordenarse con el alfabeto español y exportarse a texto y a CSV. Por último, el programa tenía que servirles también a colegas sin Python y sin costumbre de la consola, de ahí la ventana, los ejecutables y el lanzador para Windows.

## Diseño

Desde la versión 1.6 el programa es el paquete `src/pdf_word_finder/`, con un módulo por tarea. `extraction` abre el PDF y devuelve, para cada página, su texto y su rótulo, y si los rótulos son reales; `text` normaliza el texto y da la clave del orden alfabético; `patterns` convierte cada término en una expresión regular compilada; `search` busca todos los términos en todas las páginas; `report` compone el informe (de lista o detallado) y escribe los archivos TXT y CSV. Sobre esa base hay dos interfaces, `cli` (la línea de órdenes) y `gui` (la ventana), que llaman a las mismas funciones y por eso no pueden encontrar cosas distintas ni dar informes distintos.

Los datos son pocos y van en registros sencillos: `Document` (textos, rótulos y si hay árbol `/PageLabels`), `Options` (las opciones de búsqueda, inmutable), `Hit` (página secuencial, rótulo, número de apariciones y fragmentos de contexto) y `Result`, que reúne las apariciones de cada término y cuenta las páginas sin texto.

Una decisión de fondo es que las funciones del paquete no terminan el programa: cuando un PDF no se puede abrir o una expresión está mal formada lanzan `PdfError` o `PatternError`. La línea de órdenes las convierte en un mensaje y un código de salida; la ventana, en un cuadro de diálogo. Hasta la 1.5 llamaban a `sys.exit()`, y la ventana tenía que atrapar esa salida para no cerrarse.

Alrededor del paquete, `packaging/` guarda la receta de PyInstaller y dos archivos mínimos que arrancan los ejecutables; `scripts/`, el guion que construye los paquetes y el que cambia la versión; `windows/`, el lanzador y el acceso directo para Windows; `tests/`, las pruebas, y `docs/`, estas descripciones y la lista del software libre usado.

## Implementación

Está escrito en Python 3.14 o posterior: unos 2400 renglones en 25 archivos de código, de los cuales 1185 son el paquete y 382 las pruebas. Lee el PDF con pypdf (y cryptography, para los archivos cifrados); si está instalado PyMuPDF, extrae el texto con él, porque respeta mejor el orden de lectura en páginas a dos columnas o con notas. La ventana usa Tkinter y la línea de órdenes, argparse. Las órdenes `pdf-word-finder` y `pdf-word-finder-gui` las declara `pyproject.toml`.

### Los rótulos de página

pypdf inventa la numeración «1, 2, 3…» cuando el archivo no tiene árbol `/PageLabels`, y esos números son indistinguibles de los reales. Por eso el programa consulta el catálogo del PDF, y si el árbol falta o no da un rótulo por página, usa la numeración secuencial y lo advierte en una nota.

### Normalización y patrones

El texto de cada página pasa por NFKC, que deshace las ligaduras; se vuelven a unir las palabras partidas por cualquiera de los guiones de Unicode a final de renglón, y el texto queda en un solo renglón. Las palabras completas se delimitan con aserciones (`(?<!\w)…(?!\w)`) y no con `\b`, que falla junto a un apóstrofo o un guion; los espacios de una frase admiten cualquier blanco, también un salto de renglón. Con `--ignore-accents` se quitan los diacríticos tanto al texto como al término.

### Orden alfabético español

La clave de orden prescinde de tildes y mayúsculas, pero conserva la eñe como letra propia: antes de quitar los diacríticos la cambia por `n` seguida de `￿`, que va después de cualquier letra, de modo que «leña» queda detrás de «lengua».

### Los mensajes en español

argparse toma sus mensajes de `gettext`. `_argparse_es.py` sustituye esas funciones por una tabla propia, y así «usage:» u «options:» salen en español sin catálogos `.mo`.

### Los ejecutables

PyInstaller construye una carpeta con los dos programas y, al lado, el intérprete y las bibliotecas. No construye un ejecutable único, que arranca más despacio y que algunos antivirus tratan como sospechoso. PyMuPDF se carga con `importlib`, de modo que PyInstaller no lo ve y no lo mete: añadiría unos 40 MB, y su licencia es la AGPL.

## Validación

Hay 43 pruebas automáticas, con pytest, que corren en Python 3.14, la versión mínima, y en 3.15. Generan sus propios PDF pequeños, con y sin árbol `/PageLabels`, de modo que el repositorio no guarda ninguno. Cubren la normalización y el orden alfabético, los patrones (palabras completas, frases, expresiones regulares, tildes), la extracción de rótulos y los errores de un archivo ausente o dañado, la búsqueda, los dos informes, la exportación a TXT y CSV, la línea de órdenes con sus errores y su ayuda en español, y la búsqueda de la ventana.

Antes de la reorganización de la 1.6 se guardó la salida del programa anterior en 18 casos (opciones, formatos, exportaciones y errores) y se comparó con la del nuevo: solo difiere el ejemplo de la ayuda. La ventana se probó con un guion que hace una búsqueda, guarda las dos exportaciones, abre el cuadro «Acerca de…» y da una expresión mal formada. El paquete para Linux se construyó y se ejecutó. Con un Python 3.13 el programa da un mensaje claro en vez de un error. Los lanzadores de Windows no se probaron en Windows para esta versión.

## Plataforma

Funciona en Linux, Windows y macOS, con Python 3.14 o posterior y pypdf; la ventana necesita Tkinter, que viene con los instaladores de python.org y que en algunas distribuciones de Linux es un paquete aparte (`python3-tk`, `python3-tkinter`). PyMuPDF es opcional. Los paquetes hechos con PyInstaller llevan su propio intérprete y no necesitan Python; cada uno se construye en su sistema, porque PyInstaller no compila para otros. El de Linux necesita una glibc igual o más nueva que la del sistema donde se construyó.

No necesita internet. Solo el lanzador de Windows sale a la red, y solo la primera vez, para instalar Python y pypdf si faltan.

### Licencias

pdf-word-finder está bajo la GPL, versión 3 o posterior. pypdf es BSD-3-Clause; cryptography, Apache-2.0 o BSD-3-Clause; Python, de la Python Software Foundation; Tcl/Tk, de tipo BSD; PyMuPDF, AGPL-3.0, pero no va en los paquetes. `docs/LICENCIAS_DE_TERCEROS_es.md` enumera todo el software libre que usa, con su versión y su licencia, también las bibliotecas que van dentro de los paquetes.

## Ambiente

Fue desarrollado en Fedora Linux con KDE Plasma, con Python 3.15 para el trabajo diario y Python 3.14 para comprobar la versión mínima, y con uv para los entornos de prueba y de construcción. El código se gestiona con git y está publicado en GitHub (https://github.com/nivaca/pdf-word-finder) y en Codeberg (https://codeberg.org/nivaca/pdf-word-finder). Los paquetes de cada versión están en la página de *releases* de GitHub.

Se instala desde la carpeta del proyecto con `pip install .` (o `pipx install .`, `uv tool install .`), que deja las órdenes `pdf-word-finder` y `pdf-word-finder-gui`. Sin instalarlo, basta tener pypdf y ejecutar `python -m pdf_word_finder` o `python -m pdf_word_finder.gui` desde la carpeta `src/`. En Windows, `windows\pdf-word-finder.bat` hace todo eso con un doble clic, y `windows\crear-acceso-directo.bat` pone el programa en el menú de inicio. Los paquetes de PyInstaller se descomprimen y se ejecutan tal cual.

El programa no guarda ajustes: todo se indica en cada búsqueda, con las opciones de la línea de órdenes o con las casillas de la ventana. El número de versión está en un solo lugar, `src/pdf_word_finder/__init__.py`.

Contacto: nicolasvaughan@proton.me
