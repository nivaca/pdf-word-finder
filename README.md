# pdf-word-finder

**Versión 1.6** · © Nicolás Vaughan 2026 · Licencia GNU GPL v3 o posterior

*English version: [README_en.md](README_en.md).*

Busca una lista de palabras, frases o expresiones regulares dentro de un
archivo PDF e informa **en qué páginas aparece cada una**, distinguiendo
siempre entre los dos sistemas de numeración que conviven en un PDF.

---

## 1. Las dos numeraciones

Todo archivo PDF tiene una numeración **secuencial** (o lógica): la posición
de cada página dentro del archivo, contada desde 1. Es la que muestra la
barra de desplazamiento del visor y la que se usa al imprimir un intervalo.

Además, el archivo *puede* declarar una numeración **rotulada**: el número
que está realmente impreso en la página, almacenado en el árbol
`/PageLabels` del catálogo del documento. Ese árbol permite expresar todo lo
que la tradición tipográfica exige:

| Situación | Secuencial | Rotulada |
|---|---|---|
| Cubierta y portada sin numerar | 1, 2 | *(sin rótulo o «C-1»)* |
| Preliminares en romanas bajas | 3–14 | i–xii |
| Cuerpo de la obra | 15– | 1– |
| Reinicio en el segundo volumen | 320– | 1– |
| Láminas intercaladas | 88 | «Lám. IV» |

En una edición corriente, entonces, la página **secuencial 15** es la
**rotulada 1**: un desfase de catorce unidades que hace inservible cualquier
búsqueda que informe la cifra equivocada.

El programa informa **la rotulada**, que es la que le sirve al lector para
abrir el libro, en un renglón por término:

```
amor i, 1, 4
Sharahzad 3, 5, 23, 34
Nombre de Dios 5, 23
```

Si en algún momento hace falta también el índice interno del archivo —para
saltar a la página en el visor, por ejemplo—, la opción `--show-logical` lo
añade entre corchetes, y solo cuando difiere del rótulo:

```
amor i [sec. 1], 1 [sec. 3], 4 [sec. 6]
```

Si el PDF carece de árbol `/PageLabels`, el programa lo advierte
explícitamente en lugar de fingir una numeración rotulada inexistente
(cuidado con esto: `pypdf` devuelve por su cuenta «1, 2, 3…» cuando no hay
rótulos, y ese silencio es justamente lo que aquí se quiso evitar). En ese
caso los números impresos son, forzosamente, los secuenciales.

Conviene tener presente que un árbol `/PageLabels` puede ser mentiroso o
incompleto: lo genera el programa de composición, y no siempre con cuidado.
Si los rótulos que salen no corresponden a lo que está impreso en el libro,
`--show-logical` permite comprobar el desfase de un vistazo.

---

## 2. Instalación

Requiere Python 3.14 o posterior.

El programa es un paquete de Python que se instala con `pip` desde la
carpeta del proyecto. La instalación trae la única dependencia, `pypdf`, y
deja dos órdenes: `pdf-word-finder`, el programa de línea de órdenes, y
`pdf-word-finder-gui`, la ventana (§10).

```bash
pip install .
```

Para no mezclarlo con el Python del sistema conviene instalarlo en un entorno
propio, que es lo que hacen `pipx` y `uv`:

```bash
pipx install .
uv tool install .
```

Opcionalmente:

```bash
pip install pymupdf        # o, desde la carpeta del proyecto: pip install ".[mupdf]"
```

Si `pymupdf` está instalado, el programa lo usa automáticamente para extraer
el texto, porque respeta mejor el orden de lectura en páginas a dos
columnas, con notas al pie o con aparato crítico. Si no está, recurre a
`pypdf`, que basta para textos de composición sencilla. No hay que indicar
nada: la elección es automática, y el botón «Acerca de…» de la interfaz
gráfica dice cuál de los dos está en uso (§10).

> **Nota.** PyMuPDF se importa como `pymupdf`, no con el antiguo `fitz`. Ese
> nombre sigue funcionando, pero imprime un aviso de obsolescencia **en la
> salida ordinaria**, que se colaría en la lista al redirigirla a un archivo,
> y está anunciada su desaparición. Se conserva solo como respaldo para
> versiones antiguas de la biblioteca.

Sin instalar nada, basta tener `pypdf` y trabajar desde la carpeta `src/`:

```bash
pip install "pypdf[crypto]"
cd src
python -m pdf_word_finder libro.pdf amor     # línea de órdenes
python -m pdf_word_finder.gui                # ventana
```

Con un Python anterior a la 3.14 el programa no arranca: lo dice así, en un
renglón, en vez de fallar con un error de sintaxis.

> **Nota sobre los nombres.** El paquete lleva guiones bajos
> —`pdf_word_finder`— porque el guion no es un carácter válido en un
> identificador de Python. Las órdenes de consola y los ejecutables, en
> cambio, llevan guiones: `pdf-word-finder`. No es una inconsecuencia sino la
> convención corriente en Python.

### Organización del proyecto

```
src/pdf_word_finder/     el programa
    __init__.py          versión y metadatos; comprueba la versión de Python
    extraction.py        abre el PDF: el texto y el rótulo de cada página
    text.py              normalización del texto, orden alfabético español
    patterns.py          de un término a una expresión regular
    search.py            la búsqueda, común a la consola y a la ventana
    report.py            el informe y la exportación a TXT y CSV
    cli.py               el programa de línea de órdenes
    gui.py               la interfaz gráfica (tkinter)
    _argparse_es.py      los mensajes de argparse, en español
tests/                   las pruebas (pytest)
packaging/               la receta de PyInstaller y sus dos lanzadores
scripts/                 construir.py, subir_version.py y test.py
windows/                 el lanzador y el acceso directo para Windows
docs/                    el software libre usado y sus licencias
pyproject.toml           los datos del paquete y sus dependencias
```

Las pruebas usan PDF pequeños que generan ellas mismas, con y sin árbol
`/PageLabels`, de modo que el repositorio no guarda ningún PDF:

```bash
pip install -e ".[dev]"
python scripts/test.py
```

`scripts/test.py` corre cada archivo de pruebas en un proceso propio, todos a
la vez (tantos como procesadores; `-j N` lo cambia, `-v` muestra cada
archivo al terminar), y sale con 1 si alguna falla, mostrando la salida de
los archivos que fallaron. `pytest`, a secas, las corre una tras otra.

---

## 3. Uso básico

```bash
pdf-word-finder libro.pdf amor virtus "de rerum natura"
```

Salida:

```
amor i, 1, 4
virtus 4
```

Un renglón por término, con las páginas separadas por comas: es la forma de
un índice, y puede pegarse tal cual en el original de la edición o
importarse a un procesador de textos sin retoques.

Los términos que no aparecen no ensucian la lista; se avisan aparte:

```
sin apariciones: de rerum natura
```

Esa nota, como todas las demás advertencias, sale por el **canal de error**
y no por la salida ordinaria. La consecuencia práctica es que redirigir el
resultado a un archivo da un índice limpio, mientras las advertencias se
siguen viendo en pantalla:

```bash
pdf-word-finder libro.pdf --words-file onomastico.txt > indice.txt
```

Con `--detailed` se obtiene en cambio el informe extenso, con el recuento de
cada término y una página por renglón:

```
«amor»: 7 apariciones en 3 páginas
    i
    1 ×4
    4 ×2
```

Ahí sí se indica con `×` cuántas veces aparece el término en cada página, y
es también el único formato en que caben los fragmentos de contexto (§7).

Las frases de varias palabras se escriben entre comillas. Internamente los
espacios se convierten en `\s+`, de modo que la frase se encuentra aunque
esté partida por un salto de renglón o por un cambio de página del
compositor.

---

## 4. Listas de términos en un archivo

Para un léxico extenso conviene ponerlo en un archivo de texto, uno por
renglón. El signo `#` inicia un comentario:

```text
# terminos.txt — vocabulario del Dialogus
Marcolphus
Salomon
rusticus          # cf. la nota de la p. 44
"scientia divina"
re:sapient(ia|em|iae)
```

```bash
pdf-word-finder libro.pdf --words-file terminos.txt
```

Los términos del archivo se suman a los que se escriban en la línea de
órdenes, así que ambas cosas pueden combinarse.

---

## 5. Expresiones regulares

Hay dos maneras de usarlas.

**Por término**, con el prefijo `re:`, que permite mezclar patrones y
palabras literales en la misma búsqueda:

```bash
pdf-word-finder libro.pdf amor "re:virtu(s|tem|tis)" "de rerum natura"
```

**En bloque**, con `--regex`, cuando *todos* los términos son patrones:

```bash
pdf-word-finder libro.pdf --regex "Marcolph\w*" "am(or|oris|orem)"
```

Algunos patrones útiles para trabajo filológico:

| Patrón | Encuentra |
|---|---|
| `re:\bMarcolph\w*` | todas las formas flexivas de un nombre propio |
| `re:(?:im)?possibil\w+` | una familia léxica con prefijo opcional |
| `re:\d{1,2}[.,]\s*\d+` | referencias del tipo «12, 34» |
| `re:[A-Z]{2,}` | versalitas y siglas transcritas en mayúsculas |
| `re:qu[oa]d\s+\w+` | una colocación sintáctica |

Por omisión los patrones **no** se delimitan: quien escribe la expresión
decide dónde empieza y dónde termina. Si se prefiere que reciban los mismos
límites de palabra que los términos literales, se añade `--regex-word`:

```bash
pdf-word-finder libro.pdf "re:amor|virtus" --regex-word
```

La alternancia se agrupa antes de aplicar los límites, de modo que
`amor|virtus` no queda delimitada solo en una de las dos ramas.

Si una expresión está mal formada, el programa termina con un mensaje claro
en vez de un volcado de pila:

```
error: expresión regular mal formada «amor(»: missing ), unterminated subpattern at position 4
```

La segunda mitad de ese mensaje procede del módulo `re` de Python y viene
siempre en inglés; no está en mi mano traducirla.

---

## 6. Opciones

| Opción | Efecto |
|---|---|
| `--words-file ARCHIVO` | lee términos adicionales de un archivo |
| `--regex` | trata todos los términos como expresiones regulares |
| `--regex-word` | aplica límites de palabra también a las expresiones |
| `--substring` | busca también dentro de las palabras |
| `--case-sensitive` | distingue mayúsculas de minúsculas |
| `--ignore-accents` | ignora los signos diacríticos |
| `--no-dehyphenate` | conserva la división silábica de fin de renglón |
| `--show-logical` | añade la página secuencial entre corchetes |
| `--detailed` | informe extenso en vez de la lista compacta |
| `--context` | muestra un fragmento de cada aparición (implica `--detailed`) |
| `--context-width N` | anchura del fragmento (60 caracteres por omisión) |
| `--sort` | ordena la lista alfabéticamente |
| `--txt ARCHIVO` | exporta la lista alfabetizada a un archivo de texto |
| `--csv ARCHIVO` | escribe además los resultados en un CSV |

Los nombres de las opciones se dejaron en inglés a propósito, porque es la
convención de las herramientas de línea de órdenes y porque así se pueden
copiar de la documentación de otras utilidades sin sorpresas. Toda la ayuda,
en cambio, y todos los mensajes están en español.

### Palabras completas o fragmentos

Por omisión se buscan **palabras completas**: `amor` no encuentra `amoroso`
ni `desamor`. La delimitación no se hace con `\b` sino con miradas hacia
atrás y hacia adelante `(?<!\w)…(?!\w)`, lo cual importa cuando el término
lleva apóstrofo, guion o puntuación —casos en los que `\b` da resultados
contraintuitivos.

Con `--substring` se busca en cualquier posición:

```bash
pdf-word-finder libro.pdf amor --substring
```

### Diacríticos

`--ignore-accents` elimina los signos diacríticos tanto del texto como de
los términos, de manera que `busqueda` encuentra `búsqueda`, y `philologia`
encuentra `philología`. Es especialmente útil con OCR de impresos antiguos,
donde los acentos se pierden o se inventan con frecuencia.

**Advertencia para textos con notación métrica o crítica:** la opción
también pliega los términos de búsqueda, de modo que un patrón escrito
adrede para distinguir mácrones (`ā`) o diéresis (`ë`) deja de discriminar
en silencio. Conviene usar una cosa o la otra, no ambas.

### División silábica

Por omisión, `philo-\nlogia` se vuelve a unir en `philologia` antes de
buscar, de suerte que las palabras partidas al final del renglón no se
pierdan. Se contemplan todos los guiones Unicode, incluido el guion suave
(`U+00AD`) que ciertos generadores de PDF insertan.

Hay un caso en que esto perjudica: los compuestos con guion legítimo que
casualmente quedan partidos ahí mismo. Si el texto los tiene en abundancia,
`--no-dehyphenate` desactiva el comportamiento.

---

## 7. Contexto, exportación y alfabetización

```bash
pdf-word-finder libro.pdf amor --context --context-width 80
```

```
«amor»: 2 apariciones en 2 páginas
    i
        …Prefacio: el amor cortés y la philología medieval…
    1
        …Capítulo I. Marcolphus responde al rey. El AMOR vence todo…
```

El fragmento va sangrado bajo el número de página, de modo que la columna de
cifras se sigue leyendo de un vistazo. `--context` activa por sí solo el
informe detallado, porque en la lista compacta no hay dónde alojar los
fragmentos; no hace falta añadir `--detailed`.

### Exportar la lista a un archivo de texto

```bash
pdf-word-finder libro.pdf --words-file onomastico.txt --txt indice.txt
```

`--txt` escribe la lista **siempre alfabetizada**, un término por renglón,
sin encabezados ni notas: solo las entradas, listas para pegarse en el
original de la edición.

```
amor i, 1, 4
Marcolphus 1, 4
philologia i, 4
virtus 4
```

La ordenación sigue el alfabeto español: prescinde de tildes y de mayúsculas
—«ámbito», «Ámbito» y «ambito» van al mismo sitio— pero **conserva la eñe
como letra propia**, después de la ene, de modo que «leña» va detrás de
«lengua» y no confundida entre las enes. La *ch* y la *ll* se ordenan como
c+h y l+l, según la reforma académica de 1994. No depende de la
configuración regional del sistema, así que el resultado es idéntico en
cualquier máquina.

Lo escrito va en UTF-8 y con salto de renglón final, para que se comporte
bien en cualquier editor.

Si además quiere ver ordenada la lista en pantalla, `--sort` hace lo propio
con la salida ordinaria; por omisión esta respeta el orden en que se dieron
los términos, que a veces es el que interesa (el de un guion de trabajo, por
ejemplo).

### Volcar a una hoja de cálculo

Para volcar los resultados a una hoja de cálculo:

```bash
pdf-word-finder libro.pdf --words-file terminos.txt --context --csv indice.csv
```

El CSV lleva las columnas `termino`, `pagina_secuencial`, `pagina_rotulada`,
`apariciones` y `contexto`, con una fila por término y página. Ahí se
conservan **las dos** numeraciones a propósito, aunque en pantalla solo
aparezca la rotulada: un archivo de datos se filtra y se ordena después, y
tener la secuencial a mano evita rehacer la búsqueda si algún día hace falta
verificar una página en el visor. Basta ocultar la columna. Va codificado en
UTF-8; si al abrirlo en Excel se ven los acentos mal, hay que importarlo
indicando esa codificación en lugar de abrirlo con doble clic. Las filas
salen alfabetizadas por término, igual que en el TXT.

Los avisos de que uno u otro archivo quedó escrito salen por el canal de
error, no por la salida ordinaria, de modo que sigue siendo posible
redirigir la lista a un archivo y exportar a la vez sin que se mezclen.

---

## 8. Diagnóstico

El programa avisa cuando algunas páginas no arrojaron texto:

```
nota: 12 de 340 páginas no arrojaron texto (¿digitalización sin OCR?).
```

Casi siempre significa una de tres cosas: que esas páginas son imágenes
digitalizadas sin capa de texto; que están genuinamente en blanco; o que son
láminas. Si el aviso abarca *todas* las páginas, el PDF entero es una
digitalización y ninguna búsqueda textual dará resultado mientras no se le
aplique OCR (por ejemplo con `ocrmypdf`, que conserva los rótulos de
página).

Conviene además recordar que la extracción de texto de un PDF nunca es
perfecta. Las tipografías sin incrustar, las codificaciones antiguas y los
juegos de caracteres de latín medieval producen a veces sustituciones
silenciosas. Cuando un término que se sabe presente aparece como «sin
apariciones», vale la pena buscar un fragmento más corto con `--substring`
antes de dar por buena la ausencia.

---

## 9. Un ejemplo completo

Índice de nombres propios de una edición crítica: la lista alfabetizada para
el original, el CSV para verificar, y el contexto en pantalla para cotejar
sobre la marcha, ignorando acentos porque el OCR es irregular:

```bash
pdf-word-finder dialogus.pdf \
    --words-file onomastico.txt \
    --ignore-accents \
    --context --context-width 90 \
    --txt indice_onomastico.txt \
    --csv indice_onomastico.csv
```

El TXT sale listo para pegarse en el original. El CSV, alfabetizado por
término, sirve para verificar: la columna `pagina_rotulada` es la que se
imprime, y `pagina_secuencial` queda de reserva para localizar cada pasaje
en el visor si hay que cotejarlo.

---

## 10. Interfaz gráfica

La orden `pdf-word-finder-gui` abre una ventana sencilla para quien
prefiera no pasar por la consola, o para búsquedas ocasionales en las que no
vale la pena recordar las opciones.

```bash
pdf-word-finder-gui
python -m pdf_word_finder.gui      # sin instalar, desde la carpeta src/
```

No duplica ni una línea de la lógica de búsqueda: **la ventana y la línea de
órdenes son dos módulos del mismo paquete** (`gui.py` y `cli.py`) y llaman a
las mismas funciones: `search()` para buscar, `build_report()` para componer
el informe, `write_txt()` y `write_csv()` para exportar. Cualquier corrección
que se haga en la extracción del texto, en la normalización o en la
construcción de patrones se refleja en las dos sin tocarlas. No pueden
desincronizarse.

La ventana ofrece lo mismo que la línea de órdenes: selector de archivo,
recuadro para escribir los términos (uno por renglón, con `re:` y `#` igual
que en un archivo de lista), casillas para todas las opciones, resultados en
tipografía monoespaciada, casilla para pasar del informe de lista al
detallado, y botones para guardar la lista alfabetizada en TXT, exportar el
CSV o copiar el informe al portapapeles. El botón «Cargar lista…» permite
volcar un archivo de términos ya preparado.

Apartado a la derecha, el botón **«Acerca de…»** abre una ventana con la
versión, la autoría, un resumen de la licencia y un apartado de datos
técnicos: versión de Python y de Tcl/Tk, versión de pypdf, si PyMuPDF está
instalado —y por tanto cuál de los dos está extrayendo el texto—, si el
programa corre desde el código fuente o como ejecutable autónomo, y el
sistema operativo. Un botón copia todo eso al portapapeles. No es adorno:
cuando alguien reporte que «no encuentra una palabra que sí está», lo
primero que hay que saber es con qué extractor se leyó el PDF.

Solo requiere **tkinter**, que viene con Python. Si en Linux faltara:

```bash
sudo apt install python3-tk          # Debian, Ubuntu
sudo dnf install python3-tkinter     # Fedora
```

Tres decisiones internas que conviene conocer, por si alguna vez retoca el
código:

**Los errores no cierran la ventana.** Las funciones del paquete no terminan
el programa cuando el PDF no se puede abrir o una expresión regular está mal
formada: lanzan una excepción (`PdfError`, `PatternError`). La línea de
órdenes la convierte en un mensaje de error y un código de salida; la
ventana, en un cuadro de diálogo con el mismo mensaje.

**La búsqueda corre en un hilo aparte.** Extraer el texto de un libro entero
toma varios segundos, y hacerlo en el hilo principal congelaría la ventana.
El resultado vuelve por una cola, que el hilo principal revisa cada décima
de segundo, porque tkinter no admite que otro hilo toque los controles.
El formato del informe, además, lo compone `report.py` y no la interfaz, de
modo que tampoco ahí puede haber dos versiones que diverjan; lo único que
cambia es que en la ventana las advertencias se muestran junto a los
resultados, mientras que en la consola van al canal de error.
Además, el texto extraído queda en memoria: cambiar una casilla y volver a
buscar no relee el PDF.

---

## 11. Distribución

Para quien tenga Python instalado basta con el código fuente (§2). Para
entregárselo a alguien que no lo tenga —un asistente de investigación, un
colega de otro departamento— hay que empaquetarlo en un ejecutable autónomo.

### PyInstaller

La receta está en `packaging/pdf_word_finder.spec`, y `scripts/construir.py`
la ejecuta y empaqueta el resultado. En la carpeta del proyecto:

```bash
pip install pyinstaller "pypdf[crypto]"
python scripts/construir.py
```

El resultado es `build/release/pdf-word-finder-SISTEMA-VERSIÓN.zip` (SISTEMA es
`linux`, `win` o `macos`), que lleva dentro la carpeta `pdf-word-finder/`
con los ejecutables, la licencia, los README, los registros de cambios y
`docs/`. Todo queda dentro de `build/` (el trabajo intermedio de
PyInstaller, en `build/pyinstaller/`); `dist/` no se usa. La receta puede
usarse también sola, con las mismas carpetas:

```bash
pyinstaller --clean --noconfirm --distpath build/release --workpath build/pyinstaller packaging/pdf_word_finder.spec
```

En `build/release/pdf-word-finder/` quedan los dos programas —la interfaz gráfica y
el de consola— junto a la subcarpeta `_internal/` con el intérprete y las
bibliotecas que ambos comparten. Nada de eso requiere Python en la máquina
de destino. La carpeta entera pesa unos 50 MB y **se distribuye completa,
comprimida**: los ejecutables no funcionan sacados de ella.

#### Carpeta o archivo único

Ese es el modo por omisión, y conviene que lo siga siendo. La alternativa es
un ejecutable único por programa:

```bash
PWF_ONEFILE=1 pyinstaller packaging/pdf_word_finder.spec          # macOS y Linux
$env:PWF_ONEFILE=1; pyinstaller packaging/pdf_word_finder.spec    # Windows, PowerShell
```

(Con las opciones `--distpath` y `--workpath` de arriba, los ejecutables
quedan también en `build/release/`; sin ellas, PyInstaller los deja en
`dist/`.)

Un archivo suelto es más cómodo de mandar, pero paga dos precios. El
primero es de velocidad: el ejecutable único se descomprime en una carpeta
temporal **en cada ejecución**. Medido en esta misma máquina, arrancar y
mostrar la versión:

| | Modo carpeta | Archivo único |
|---|---|---|
| arranque | 79 ms | 264 ms |

El segundo precio es peor: descomprimirse solo en una carpeta temporal y
ejecutar código desde allí es, estructuralmente, lo que hace cierto programa
malicioso, y algunos antivirus lo tratan como tal. El modo carpeta no hace
nada de eso y levanta muchas menos sospechas. Si un colega reporta que
Windows «no puede acceder al archivo» —mensaje engañoso con el que Defender
suele anunciar que ha bloqueado algo—, el modo carpeta es la primera
respuesta.

En rigor el modo carpeta ocupa más en disco (unos 50 MB frente a 33 MB
sumando los dos ejecutables únicos), pero comprimido para su distribución la
diferencia se estrecha, y de todos modos no es lo que está en juego.

**No se puede compilar para otros sistemas.** PyInstaller empaqueta el
intérprete de la máquina donde se ejecuta, de modo que el `.exe` de Windows
hay que construirlo en Windows, el `.app` de macOS en un Mac y el binario de
Linux en Linux. No hay opción de compilación cruzada, y los emuladores no
sirven. Hay que tener acceso a las tres máquinas (más abajo).

Dos particularidades de esta receta que conviene no perder de vista si algún
día la modifica:

La receta no necesita ni `datas` ni `hiddenimports`, y conviene entender por
qué. PyInstaller descubre lo que hay que empaquetar **analizando el código en
busca de importaciones**. Los ejecutables arrancan desde dos archivos
mínimos, `packaging/lanzador_cli.py` y `packaging/lanzador_gui.py`, que
importan el paquete con un `import` corriente; la receta le dice a
PyInstaller dónde está (`pathex`, la carpeta `src/`), y desde ahí encuentra
`pypdf` y sus dependencias. Todo entra solo.

Los lanzadores existen porque un módulo de un paquete no puede ejecutarse
suelto: sus importaciones relativas (`from .search import …`) fallan fuera
del paquete. PyMuPDF, en cambio, queda fuera aunque esté instalado, porque
el programa lo carga con `importlib` y PyInstaller no lo ve. Es lo deseable:
añadiría unos 40 MB, y su licencia es la AGPL.

**El nombre del ejecutable es independiente del nombre del archivo.** Se
declara en `name`, dentro de cada bloque `EXE`, y por eso los ejecutables
salen como `pdf-word-finder` y `pdf-word-finder-gui` aunque las fuentes
lleven guiones bajos.

### Construir en cada sistema y publicar

Desde la versión 1.4 no hay construcción automática: el proyecto ya no tiene
un flujo de trabajo de GitHub. Cada paquete se construye en su sistema con
`scripts/construir.py` y se adjunta a mano a la *release*. El orden es este:

```bash
python scripts/subir_version.py 1.6        # la versión nueva, en todas partes
python scripts/subir_version.py --revisar
git commit -am "Versión 1.6"
git tag -a 1.6 -m "Versión 1.6"
git push origin main 1.6
python scripts/construir.py                # en cada sistema
```

Tres cosas que conviene tener presentes:

* **En Linux, construir en el sistema más viejo que se quiera admitir.** Un
  binario de Linux exige una glibc igual o más antigua que la de la máquina
  donde se construyó. Construido en una distribución reciente, no abre en
  una más vieja; al revés no hay problema.

* **En macOS se empaqueta con `ditto`, no con `zip`.** El paquete `.app`
  contiene enlaces simbólicos que `zip` convierte en copias, y la aplicación
  resultante no abre en la máquina de destino. `scripts/construir.py` ya lo
  hace así. Es un error clásico y difícil de diagnosticar, porque la
  construcción no protesta.

* **La etiqueta y `__version__` deben concordar.** Una etiqueta `1.3` sobre
  un código que se anuncia como 1.2 produce descargas que mienten sobre sí
  mismas, y eso no se puede corregir después: las releases publicadas no se
  editan sin romper los enlaces de quien ya descargó. La versión se cambia
  con `scripts/subir_version.py` (§12), y el paquete toma su nombre de
  `__version__`.

### Publicar una release a mano

Hay dos caminos.

Por la web: pestaña «Releases» → «Draft a new release» → «Choose a tag»
(puede crearla ahí mismo) → arrastrar los archivos de `build/release/` a la zona de
adjuntos → «Publish release».

Por consola, con la herramienta oficial `gh`:

```bash
gh release create v1.6 \
    build/release/pdf-word-finder-linux-1.5.zip \
    build/release/pdf-word-finder-win-1.5.zip \
    --title "pdf-word-finder 1.6" \
    --notes "Versión 1.6."
```

En ambos casos recuerde que los paquetes deben construirse en cada sistema
operativo, de modo que a mano solo podrá adjuntar el de la máquina que tenga
delante.

### Si Windows o macOS se resisten a abrirlo

Los ejecutables van sin firma digital, y los dos sistemas lo notan. En macOS,
Gatekeeper se negará a abrir la aplicación: la salida es hacer clic derecho
sobre ella y elegir «Abrir», que ofrece una excepción por única vez. En
Linux no hay obstáculo; basta `chmod +x`. Windows merece apartado aparte.

#### En Windows 11

Esto es lo que hay que explicarle a quien reciba el programa. Conviene
pegarlo tal cual en el correo, porque quien no lo sepa suele concluir que el
archivo está dañado y lo borra.

**1. Desbloquear el archivo.** Windows marca todo lo que llega de internet
con un distintivo invisible, y es ese distintivo —no el programa— lo que
dispara la advertencia. Clic derecho → Propiedades → abajo del todo, casilla
**«Desbloquear»** → Aceptar.

Si lo que recibió es un `.zip`, conviene desbloquearlo **antes** de
descomprimirlo: así se limpia todo su contenido de una vez y no hay que
repetir la operación con cada archivo extraído. Si es un `.exe` suelto, se
hace sobre él directamente.

Hecho esto, lo corriente es que el aviso del punto siguiente ya no aparezca:
desbloquear es justamente quitarle a Windows el motivo para desconfiar. El
punto 2 queda por si acaso.

**2. Al ejecutarlo aparecerá una pantalla azul** que dice «Windows protegió
su PC». No es un error ni un virus: es el aviso de editor desconocido. Se
pulsa **«Más información»** —y solo entonces aparece el botón—
**«Ejecutar de todas formas»**.

Con eso basta la primera vez; después abre sin preguntar nada.

Si prefiere hacerlo desde PowerShell, una orden reemplaza al primer paso:

```powershell
Unblock-File .\pdf-word-finder-gui.exe        # un archivo suelto
Get-ChildItem -Recurse .\pdf-word-finder | Unblock-File   # una carpeta
```

Dos situaciones en las que lo anterior no funciona, ambas propias de
Windows 11:

* **Smart App Control.** Es una protección que viene activa en algunas
  instalaciones limpias de Windows 11 y bloquea sin apelación todo programa
  sin firmar: no ofrece un «ejecutar de todas formas». Se comprueba en
  Seguridad de Windows → Control de aplicaciones y explorador. Desactivarlo
  es **irreversible** —no puede volver a encenderse sin reinstalar el
  sistema—, de modo que no es algo que convenga pedirle a nadie. Si el
  destinatario lo tiene activo, lo sensato es darle el código fuente y que
  instale Python (más abajo).

* **Modo S.** Solo admite programas de la Microsoft Store. Salir del modo S
  es gratuito pero también irreversible.

Si además el antivirus pone en cuarentena el archivo —cosa distinta del
aviso anterior—, hay que restaurarlo desde Seguridad de Windows → Protección
antivirus y contra amenazas → Historial de protección, o excluir la carpeta.
Las exclusiones bajan la guardia del sistema en esa carpeta, así que conviene
usarlas solo sobre una que uno controle, y no sobre Descargas.

Nótese que nada de esto ocurre con los ejecutables que usted mismo construya
en su máquina: el distintivo lo pone la descarga, no el programa. Solo lo
verán quienes lo reciban por internet.

> **Conviene distribuirlo dentro de un `.zip` y no como `.exe` suelto.** No
> es por comodidad: un `.exe` desnudo tropieza además con obstáculos previos
> a Windows. Chrome y Edge lo señalan en la barra de descargas y exigen un
> «Conservar de todos modos» adicional, y la mayoría de los correos
> —Outlook y Gmail entre ellos— rechazan de plano los adjuntos ejecutables,
> a veces sin avisar al remitente. Comprimido no ocurre ninguna de las dos
> cosas. Por eso `scripts/construir.py` empaqueta antes de publicar.

#### El otro problema: los antivirus

Distinto del aviso anterior, y más molesto, es que los ejecutables hechos con
PyInstaller disparan **falsos positivos** en algunos antivirus. La razón es
estructural: un ejecutable de un solo archivo se descomprime en una carpeta
temporal y ejecuta código desde ahí, que es exactamente lo que hace cierto
programa malicioso.

Dos paliativos gratuitos:

* **Construir en modo carpeta**, que es lo que la receta hace por omisión
  precisamente por esto. Véase «Carpeta o archivo único», más arriba.

* **Reportar el falso positivo.** Microsoft y los demás fabricantes tienen
  formularios para ello y suelen corregirlo en días.

### Para colegas en Windows: el camino sin ejecutable

Windows Defender bloquea con cierta frecuencia los ejecutables hechos con
PyInstaller, y el mensaje con que lo hace —«Windows no puede acceder al
archivo especificado»— parece un problema de permisos y no lo es. Reportar el
falso positivo a Microsoft lo corrige para todo el mundo en unos días, pero
entretanto sus colegas no pueden abrir el programa, y en equipos
administrados por la universidad puede que no se corrija nunca.

El camino que no depende de nada de eso es no distribuir un ejecutable.
Python es gratuito, se instala desde la Microsoft Store sin permisos de
administrador, y ningún antivirus objeta un archivo `.py`.

Para que a un colega no le cueste más que un doble clic, el proyecto incluye
`windows/pdf-word-finder.bat`. Se distribuye un `.zip` con el código
fuente —el que GitHub ofrece en cada versión sirve tal cual—, en el que lo
que importa son dos carpetas:

```
src/pdf_word_finder/       el programa
windows/pdf-word-finder.bat
```

y la instrucción es: descomprimir y hacer doble clic en
`windows\pdf-word-finder.bat`. El lanzador busca el programa en la carpeta
`src`, al lado de la suya, y lo abre con `pythonw -m pdf_word_finder.gui`
desde allí.

El lanzador se encarga de todo lo demás. Si falta `pypdf`, lo instala sin
preguntar —es cuestión de segundos y no tiene contrapartida—. Si falta
Python 3.14 o posterior, en cambio, **pide permiso antes** (un Python más
viejo cuenta como si no hubiera ninguno): instalar un programa de 100 MB en
el equipo de otro no es algo que deba ocurrir por sorpresa. Aceptado eso,
intenta primero con `winget`, que viene incluido en Windows 11 y no obliga al
usuario a elegir nada; si no está disponible o falla, abre la Microsoft Store
en la página de Python y explica los tres pasos que hay que dar allí.

Tras instalar Python, el lanzador sigue adelante y abre el programa. Una
ventana de consola hereda la lista de programas del sistema al abrirse y no
la actualiza, de modo que no puede ver un Python que acaba de aparecer; por
eso el lanzador lo busca en las carpetas donde suele quedar. Si aun así no
lo encuentra, pide cerrar la ventana y volver a hacer doble clic, y lo dice
con esas palabras, para que nadie concluya que algo salió mal.

Si algo falla —falta `tkinter`, o pip no puede salir a la red por el
proxy— lo dice en castellano y explica qué hacer, en vez de cerrarse sin
más.

Tres detalles de ese archivo que conviene no «arreglar»:

* **Está escrito sin tildes.** La consola de Windows no usa UTF-8 por
  omisión y los acentos saldrían ilegibles. Es fealdad deliberada.

* **Lleva finales de renglón CRLF**, que es lo que exige el formato `.bat`.
  Si lo edita en un editor de Linux o macOS, conserve ese detalle.

* **Abre la ventana con `pythonw`** y no con `python`, para que no quede
  detrás una ventana negra de consola.

Sobre la versión de Python que instala: `winget` identifica cada serie por
separado —`Python.Python.3.14`, `Python.Python.3.15`…— y no existe un
identificador genérico que signifique «la más reciente». El lanzador las
prueba de mayor a menor y se queda con la primera que encuentre en el
catálogo, de modo que instala la más nueva disponible sin necesidad de
mantenimiento. La lista va de 3.19 a 3.14, la mínima que admite el
programa; si algún día hiciera falta, basta añadir números al principio.

#### Un acceso en el menú de inicio

El equivalente windows del `.desktop` de Linux es un acceso directo `.lnk`
guardado en la carpeta del menú de inicio del usuario:

```
%APPDATA%\Microsoft\Windows\Start Menu\Programs
```

Se crea con `windows\crear-acceso-directo.bat`, que se ejecuta una sola vez y ofrece
además dejar un acceso en el escritorio. Después, el programa se abre desde
el menú de inicio como cualquier otra aplicación.

El acceso **no apunta al `.bat`** sino directamente a `pythonw.exe`, con
`-m pdf_word_finder.gui` y la carpeta `src` como carpeta de trabajo. Eso
resuelve de paso dos cosas: no queda detrás una
ventana negra de consola, y Windows no somete los accesos directos al filtro
que aplica a los archivos de órdenes descargados de internet —que es la razón
de que un `.bat` recién bajado se bloquee al hacerle doble clic en el
Explorador aunque funcione perfectamente desde la terminal—.

> Si prefiere no ejecutar nada: clic derecho sobre `pdf-word-finder.bat` →
> «Mostrar más opciones» → «Crear acceso directo», y arrastre el resultado a
> la carpeta de arriba. El efecto es el mismo, salvo que el acceso apuntará
> al `.bat` y heredará su bloqueo si lo tuviera.

Sobre ese bloqueo: se quita de una vez con

```powershell
Unblock-File .\pdf-word-finder.bat
```

o desmarcándolo en Propiedades, como se explicó más arriba.

### Alternativas más ligeras

Si el destinatario tiene Python, hay caminos más sencillos que un ejecutable
de 20 MB:

* **El código fuente.** La carpeta `src/` y `pip install "pypdf[crypto]"`
  (§2). Para colegas con soltura técnica es lo más simple.

* **Un archivo `.pyz`.** `zipapp` empaqueta todo en un solo archivo
  ejecutable por Python, de unos pocos KB. Requiere Python en la máquina de
  destino, pero se distribuye como una unidad.

* **El paquete instalable.** El proyecto ya lo es: `pipx install .` deja
  las órdenes `pdf-word-finder` y `pdf-word-finder-gui` disponibles en todo
  el sistema (§2). Es también el camino si algún día se publica en PyPI.

---

## 12. Versión

Versión **1.6**. La cifra se consulta desde el propio programa:

```bash
pdf-word-finder --version
```

```
pdf-word-finder 1.6 — © Nicolás Vaughan 2026 — licencia GPL-3.0-or-later
```

### Cambiar el número de versión

El número vive en un solo lugar: `__version__`, en
`src/pdf_word_finder/__init__.py`. De ahí lo toman el programa y la ventana,
`pyproject.toml` (como versión dinámica) y la receta de PyInstaller, que lo
lee del archivo al construir, de modo que ninguno puede quedarse atrás. Los README —`README.md` y su traducción, `README_en.md`— son la
excepción: mencionan la cifra en varios sitios y no pueden deducirla, y para
eso está `scripts/subir_version.py`:

```bash
python scripts/subir_version.py 1.6        # cambia la versión en todas partes
python scripts/subir_version.py --mostrar  # dice cuál es la actual
python scripts/subir_version.py --revisar  # comprueba que todo concuerde
```

El modo `--revisar` sirve como red de seguridad antes de etiquetar: devuelve
un código de error si alguno de los README menciona una versión distinta
de la del programa, de modo que puede llamarse desde un gancho de git.

Los patrones del guion están anclados a su contexto —`**Versión X**`,
`git tag -a X`, `pdf-word-finder X — ©`…— y no sustituyen cifras sueltas. Es
deliberado: un «1.2» perdido en cualquier renglón podría ser otra cosa, y
estropearlo sería difícil de advertir. Si añade al README una mención nueva
de la versión con otra forma, conviene añadir también su patrón al guion.

En el código está declarada una sola vez, en `__version__`, y de ahí la toma
tanto `--version` como el encabezado. Al modificar el programa basta con
cambiarla en ese único lugar.

---

## 13. Licencia y autoría

© Nicolás Vaughan 2026.

Distribuido bajo la **Licencia Pública General de GNU (GPL), versión 3 o,
a su elección, cualquier versión posterior**; el texto completo está en el
archivo `LICENSE` que acompaña a este README. En resumen: cualquiera puede
usar, estudiar, copiar, modificar y distribuir el programa, incluso a cambio
de dinero, con la condición de que lo que distribuya —el programa tal cual o
una versión modificada— vaya bajo la misma licencia, conserve los avisos de
copyright y de licencia, y se entregue acompañado de su código fuente (o de
una oferta para obtenerlo). El programa se entrega «tal cual», sin garantía
de ninguna clase.

Al distribuir el código conviene distribuir el proyecto entero, o al menos
`src/`, `pyproject.toml`, `README.md`, `README_en.md`, `LICENSE` y `docs/`,
más `packaging/` y `scripts/` si quiere que otros puedan construir los
ejecutables, porque el aviso de copyright que lleva incorporado el programa
remite a `LICENSE`. Los paquetes que hace `scripts/construir.py` ya llevan
la licencia y `docs/` dentro.

El software libre sobre el que está hecho el programa —Python, pypdf,
Tcl/Tk, PyInstaller y las bibliotecas que van dentro de los paquetes— está
enumerado, con su versión y su licencia, en
[`docs/LICENCIAS_DE_TERCEROS_es.md`](docs/LICENCIAS_DE_TERCEROS_es.md)
(en inglés, [`docs/THIRD_PARTY_LICENSES.md`](docs/THIRD_PARTY_LICENSES.md)).
Todas esas licencias son compatibles con la GPL.
