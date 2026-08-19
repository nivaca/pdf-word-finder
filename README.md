# pdf-word-finder

**Versión 1.0** · © Nicolás Vaughan 2026 · Licencia MIT

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

Requiere Python 3.9 o posterior.

```bash
pip install pypdf
```

Opcionalmente:

```bash
pip install pymupdf
```

Si `pymupdf` está instalado, el programa lo usa automáticamente para extraer
el texto, porque respeta mejor el orden de lectura en páginas a dos
columnas, con notas al pie o con aparato crítico. Si no está, recurre a
`pypdf`, que basta para textos de composición sencilla. No hay que indicar
nada: la elección es automática.

El archivo lleva la línea `#!/usr/bin/env python3`, de modo que en macOS y
en Linux puede ejecutarse directamente si se le da permiso de ejecución:

```bash
chmod +x pdf_word_finder.py
./pdf_word_finder.py libro.pdf amor
```

Para tenerlo a mano desde cualquier directorio, basta copiarlo a un lugar
del `PATH` —`~/.local/bin/`, por ejemplo—, o bien poner allí un enlace
simbólico con el nombre corto de la orden:

```bash
ln -s ~/proyectos/pdf-word-finder/pdf_word_finder.py ~/.local/bin/pdf-word-finder
```

Así se escribe `pdf-word-finder libro.pdf amor` sin más.

> **Nota sobre los nombres.** Los archivos fuente llevan guiones bajos
> —`pdf_word_finder.py`— porque el guion no es un carácter válido en un
> identificador de Python y un archivo llamado `pdf_word_finder.py` no podría
> importarse con `import`. Los ejecutables y las órdenes de consola, en
> cambio, llevan guiones: `pdf-word-finder`. No es una inconsecuencia sino la
> convención corriente en Python, y trae una ventaja práctica: al ser el
> núcleo un módulo importable de veras, la interfaz gráfica lo usa con un
> `import` normal y el empaquetado para distribución no requiere artificio
> alguno (§11).

---

## 3. Uso básico

```bash
python pdf_word_finder.py libro.pdf amor virtus "de rerum natura"
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
python pdf_word_finder.py libro.pdf --words-file onomastico.txt > indice.txt
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
python pdf_word_finder.py libro.pdf --words-file terminos.txt
```

Los términos del archivo se suman a los que se escriban en la línea de
órdenes, así que ambas cosas pueden combinarse.

---

## 5. Expresiones regulares

Hay dos maneras de usarlas.

**Por término**, con el prefijo `re:`, que permite mezclar patrones y
palabras literales en la misma búsqueda:

```bash
python pdf_word_finder.py libro.pdf amor "re:virtu(s|tem|tis)" "de rerum natura"
```

**En bloque**, con `--regex`, cuando *todos* los términos son patrones:

```bash
python pdf_word_finder.py libro.pdf --regex "Marcolph\w*" "am(or|oris|orem)"
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
python pdf_word_finder.py libro.pdf "re:amor|virtus" --regex-word
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
python pdf_word_finder.py libro.pdf amor --substring
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
python pdf_word_finder.py libro.pdf amor --context --context-width 80
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
python pdf_word_finder.py libro.pdf --words-file onomastico.txt --txt indice.txt
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
python pdf_word_finder.py libro.pdf --words-file terminos.txt --context --csv indice.csv
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
python pdf_word_finder.py dialogus.pdf \
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

El archivo `pdf_word_finder_gui.py` abre una ventana sencilla para quien
prefiera no pasar por la consola, o para búsquedas ocasionales en las que no
vale la pena recordar las opciones.

```bash
python pdf_word_finder_gui.py
```

No duplica ni una línea de la lógica de búsqueda: **carga el programa de
línea de órdenes y llama a sus funciones**. Cualquier corrección que se haga
en `pdf_word_finder.py` —en la extracción del texto, en la normalización, en
la construcción de patrones— se refleja en la interfaz sin tocarla. Las dos
piezas no pueden desincronizarse.

La ventana ofrece lo mismo que la línea de órdenes: selector de archivo,
recuadro para escribir los términos (uno por renglón, con `re:` y `#` igual
que en un archivo de lista), casillas para todas las opciones, resultados en
tipografía monoespaciada, casilla para pasar del informe de lista al
detallado, y botones para guardar la lista alfabetizada en TXT, exportar el CSV o
copiar el informe al portapapeles. El botón
«Cargar lista…» permite volcar un archivo de términos ya preparado.

Solo requiere **tkinter**, que viene con Python. Si en Linux faltara:

```bash
sudo apt install python3-tk
```

Tres decisiones internas que conviene conocer, por si alguna vez retoca el
archivo:

**Cómo se carga el núcleo.** Con un `import pdf_word_finder` corriente, que
funciona porque los dos archivos están en la misma carpeta. De ahí que deban
viajar juntos; si no lo encuentra, la interfaz avisa con un cuadro de diálogo
en vez de fallar en silencio. Que sea una importación normal y no una carga
por ruta importa además para el empaquetado (§11).

**Los errores no cierran la ventana.** Las funciones del núcleo terminan el
programa con `sys.exit()` cuando el PDF está cifrado o una expresión regular
está mal formada, que es lo correcto en la consola pero cerraría la ventana
sin explicación. La interfaz captura ese `SystemExit` y lo convierte en un
cuadro de diálogo con el mismo mensaje.

**La búsqueda corre en un hilo aparte.** Extraer el texto de un libro entero
toma varios segundos, y hacerlo en el hilo principal congelaría la ventana.
El resultado vuelve por una cola, que el hilo principal revisa cada décima
de segundo, porque tkinter no admite que otro hilo toque los controles.
El formato del informe, además, lo compone el núcleo y no la interfaz, de
modo que tampoco ahí puede haber dos versiones que diverjan; lo único que
cambia es que en la ventana las advertencias se muestran junto a los
resultados, mientras que en la consola van al canal de error.
Además, el texto extraído queda en memoria: cambiar una casilla y volver a
buscar no relee el PDF.

---

## 11. Distribución

Para quien tenga Python instalado basta con los archivos `.py`. Para
entregárselo a alguien que no lo tenga —un asistente de investigación, un
colega de otro departamento— hay que empaquetarlo en un ejecutable autónomo.

### PyInstaller

El archivo `pdf-word-finder.spec` que acompaña al proyecto contiene la
receta. En la carpeta del proyecto:

```bash
pip install pyinstaller pypdf
pyinstaller --clean --noconfirm pdf-word-finder.spec
```

En `dist/` quedan dos ejecutables autónomos —la interfaz gráfica y el
programa de consola— que no requieren Python ni bibliotecas en la máquina de
destino. Pesan unos 15–20 MB cada uno, casi todo intérprete de Python.

**No se puede compilar para otros sistemas.** PyInstaller empaqueta el
intérprete de la máquina donde se ejecuta, de modo que el `.exe` de Windows
hay que construirlo en Windows, el `.app` de macOS en un Mac y el binario de
Linux en Linux. No hay opción de compilación cruzada, y los emuladores no
sirven. Las dos salidas son tener acceso a las tres máquinas, o dejar que lo
haga GitHub (más abajo).

Dos particularidades de esta receta que conviene no perder de vista si algún
día la modifica:

La receta no necesita ni `datas` ni `hiddenimports`, y conviene entender por
qué, porque es justamente lo que se estropearía si algún día renombrara los
archivos con guiones. PyInstaller descubre lo que hay que empaquetar
**analizando el código en busca de importaciones**. Como la interfaz importa
el núcleo con un `import` corriente (§10), lo encuentra, y con él encuentra
`pypdf` y sus dependencias. Todo entra solo.

Si el núcleo llevara guiones en el nombre no podría importarse así: habría
que cargarlo por ruta con importlib, empaquetarlo como archivo acompañante
en `datas`, declarar `hiddenimports=["pypdf"]` a mano —porque un archivo
tratado como dato no se analiza, y sus importaciones quedan invisibles— y
añadir código para localizarlo dentro del ejecutable, donde los acompañantes
no están junto al programa sino en una carpeta temporal cuya ruta queda en
`sys._MEIPASS`. Los guiones bajos ahorran las cuatro cosas.

**El nombre del ejecutable es independiente del nombre del archivo.** Se
declara en `name`, dentro de cada bloque `EXE`, y por eso los ejecutables
salen como `pdf-word-finder` y `pdf-word-finder-gui` aunque las fuentes
lleven guiones bajos.

### Construcción automática con GitHub Actions

El archivo `.github/workflows/build.yml` construye las tres versiones en las
máquinas de GitHub, sin necesidad de tener a mano un Windows y un Mac. Se
dispara al publicar una etiqueta:

```bash
git tag v1.0
git push origin v1.0
```

Los tres paquetes quedan disponibles para descarga en la pestaña «Actions»
del repositorio. También puede lanzarse a mano desde ahí.

Dos detalles del flujo de trabajo: se compila en **Ubuntu 22.04** y no en la
versión más reciente, porque un binario de Linux exige una glibc igual o más
antigua que la de la máquina donde se construyó —compilar en la más vieja
amplía la compatibilidad, al revés no funciona—; y `macos-latest` produce un
binario para Apple Silicon, así que para Mac con procesador Intel hay que
añadir una entrada `macos-13`.

### Firma digital

Los ejecutables salen sin firmar, y eso tiene consecuencias visibles para
quien los reciba:

* **Windows.** SmartScreen mostrará una advertencia de «editor desconocido».
  El usuario puede seguir adelante desde «Más información → Ejecutar de
  todas formas», pero conviene avisarle de antemano. Firmar requiere un
  certificado de firma de código, que es de pago.

* **macOS.** Gatekeeper se negará a abrir la aplicación. La salida sin
  certificado es hacer clic derecho sobre ella y elegir «Abrir», que ofrece
  una excepción por única vez. Firmar y notarizar exige una cuenta de
  desarrollador de Apple, también de pago.

* **Linux.** No hay obstáculo; basta `chmod +x`.

Para distribución dentro de la universidad, la advertencia y una instrucción
de una línea suelen bastar. Para distribución pública conviene pensar en los
certificados.

### Alternativas más ligeras

Si el destinatario tiene Python, hay caminos más sencillos que un ejecutable
de 20 MB:

* **Los archivos sueltos.** Cuatro archivos y `pip install pypdf`. Para
  colegas con soltura técnica es lo más simple.

* **Un archivo `.pyz`.** `zipapp` empaqueta todo en un solo archivo
  ejecutable por Python, de unos pocos KB. Requiere Python en la máquina de
  destino, pero se distribuye como una unidad.

* **Un paquete instalable.** Con un `pyproject.toml` mínimo y un punto de
  entrada de consola, `pipx install` deja la orden `pdf-word-finder`
  disponible en todo el sistema. Es lo indicado si algún día publica el
  programa en PyPI, y los nombres actuales ya sirven tal cual.

---

## 12. Versión

Versión **1.0**. La cifra se consulta desde el propio programa:

```bash
python pdf_word_finder.py --version
```

```
pdf-word-finder 1.0 — © Nicolás Vaughan 2026 — licencia MIT
```

En el código está declarada una sola vez, en `__version__`, y de ahí la toma
tanto `--version` como el encabezado. Al modificar el programa basta con
cambiarla en ese único lugar.

---

## 13. Licencia y autoría

© Nicolás Vaughan 2026.

Distribuido bajo **licencia MIT**; el texto completo está en el archivo
`LICENSE` que acompaña a este README. En resumen: cualquiera puede usar,
copiar, modificar, fusionar, publicar, distribuir, sublicenciar y vender
copias del programa, con la única condición de conservar el aviso de
copyright y el de la licencia en las copias o partes sustanciales que
distribuya. El programa se entrega «tal cual», sin garantía de ninguna
clase.

Al distribuirlo conviene incluir los cuatro archivos
—`pdf_word_finder.py`, `pdf_word_finder_gui.py`, `README.md` y `LICENSE`—,
más `pdf-word-finder.spec` si quiere que otros puedan construir los
ejecutables,
porque el aviso de copyright que llevan incorporado los dos programas remite
al último, y la interfaz gráfica no funciona sin el programa de línea de
órdenes en la misma carpeta.
