# AFDC v4 · Demo estática

Implementación independiente de la consulta pública de `frankhode/afdc_v4`, preparada para el repositorio `frankhode/afdc_v4_demo` y GitHub Pages. El repositorio original no se modifica.

**Estado:** aplicación y muestra de datos preparadas; fotografías pendientes de recibir. No se simulan fotografías ni se consultan archivos del servidor original. Los 346 fotogramas seleccionados se muestran como pendientes hasta incorporar copias autorizadas.

## Ejecutar

No requiere instalar paquetes JavaScript, compilar, PHP ni MySQL. Desde esta carpeta:

```sh
python -m http.server 8000 --directory docs
```

Abrir `http://localhost:8000`. También se puede copiar `docs/` a una carpeta de XAMPP y abrirla mediante Apache. No abrir `index.html` con doble clic: el navegador necesita HTTP para cargar módulos y JSON.

## Contenido

- 87 sobres reales del respaldo del 31/07/2026, unidos por barcode y SYS.
- 346 referencias reales a fotogramas, sin rutas de origen.
- «El Diego»: 11 fotografías de 3 sobres, conservando el orden y la pertenencia de la única colección marcada pública en el SQL.
- Tres recorridos nuevos: Fútbol argentino (36 sobres), Música y escenarios (24), Teatro, arte y ciudad (24). No son colecciones privadas del sistema.
- Algunos sobres participan en más de una colección. Los recuentos representan la muestra, no el total del archivo.

## Funciones

| Recorrido | Implementación |
| --- | --- |
| Simple | Coincidencia parcial en título o materias, sin distinguir mayúsculas/acentos |
| Avanzada | Campos del sistema original; AND/OR evaluados de izquierda a derecha; NOT por condición; rango de años |
| Índices | 600, 610, 611, 630, 650, 651 y 655; inicio alfabético, bloques de 25, enlaces exactos a sobres |
| Resultados | Tabla, refinado sobre todos los resultados, orden, paginación, filtro de fotos incluidas y CSV |
| Ficha / visor | Datos descriptivos, materias enlazadas, tira, anterior/siguiente, zoom, ajuste, 100%, giro, desplazamiento y pantalla completa |
| Colecciones | Colección pública original y recorridos de demo, con enlaces a fotogramas específicos |
| Preferencias | Temas oscuro/claro/vintage y favoritos locales |

Las cuentas, permisos, edición, recortes, catalogación, campeonatos y edición impresa quedan fuera de esta demo. No hay botones que simulen guardar cambios en la base original.

## Incorporar fotografías

1. Preparar un ZIP con copias que se puedan mostrar públicamente, conservando nombres como `FO069829_001.jpg` o `BNA_FO069829_001.tif`. La lista exacta está en `docs/data/images-requested.json`.
2. Para reunir archivos desde una carpeta local de bajas, se incluye `scripts/collect_images.ps1`. No sube archivos ni modifica los originales. Ejemplo en PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\collect_images.ps1 -SourceRoot "D:\Fotos\Bajas" -OutputDir "$env:USERPROFILE\Desktop\afdc-demo-fotos"
```

3. Importar únicamente las imágenes revisadas y autorizadas:

```sh
python -m pip install Pillow
python scripts/import_images.py /ruta/seleccion.zip --confirmed-public
python scripts/validate.py
```

El importador admite ZIP o carpeta, selecciona únicamente los IDs del manifiesto, genera JPEG de hasta 1600 px y miniaturas de 320 px, aplica la orientación y elimina metadatos EXIF/GPS/comentarios. Los archivos que no pertenecen a la muestra se ignoran. No extrae rutas del ZIP. Detecta IDs duplicados. El parámetro `--confirmed-public` registra una decisión humana: no comprueba derechos ni el contenido visual.

Para incluir imágenes de otros sobres hay que adaptar primero la selección; no se inventan vínculos por semejanza visual o de título.

## Extracción reproducible

Mantener el SQL fuera del repositorio:

```sh
python scripts/extract_sample.py /ruta/privada/respaldo.sql
```

Este comando **recrea el catálogo y deja las imágenes pendientes**; volver a importar las copias tras ejecutarlo. El lector interpreta INSERTs de phpMyAdmin, no ejecuta SQL. Usa una lista explícita de tablas y campos, conserva identificadores y acentos, prioriza los fotogramas de colecciones públicas y selecciona un máximo inicial de cuatro imágenes por sobre adicional. Las rutas internas nunca se exportan. Revisar el contenido de una nueva muestra antes de publicarla; los filtros automáticos de asuntos sensibles no sustituyen esa revisión.

## Publicar en GitHub Pages

1. Crear el repositorio público **afdc_v4_demo** en la cuenta `frankhode`.
2. Subir únicamente el contenido de esta carpeta; **nunca el respaldo SQL ni la carpeta de fotografías originales**.
3. En **Settings → Pages → Build and deployment**, elegir **Deploy from a branch**, rama **main** y carpeta **/docs**; guardar.
4. Abrir la URL que indique GitHub al terminar el despliegue.

La publicación usa únicamente `docs/`; scripts y tests no se sirven como parte del sitio. Las rutas relativas y la navegación con `#/` funcionan bajo el prefijo del repositorio, incluidos enlaces directos, recargas y el botón Atrás. `.nojekyll` evita procesar la aplicación con Jekyll.

Referencia: [Configuring a publishing source for GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Verificación

```sh
npm test
python scripts/validate.py
python -m unittest discover -s tests -p 'test_*.py'
```

La comprobación visual en navegador quedó pendiente: el navegador del entorno bloqueó el acceso a las vistas locales. El visor no se ha validado aún con las fotografías reales, que están pendientes del ZIP.

No se necesitan dependencias npm. Las 12 pruebas automáticas verifican semántica booleana, acentos, índices, referencias, imágenes disponibles, CSV y extracción. `validate.py` valida el esquema permitido y exige que cada imagen declarada exista.

## Procedencia y límites

Se tomó como referencia el commit `2ae40e23c5dbeab82451a6228a99055783572b40` de `frankhode/afdc_v4`: buscadores simple/avanzado, índices, perfil de tabla, encabezado, temas y visor. Esta es una adaptación funcional, no una conversión literal de todos sus módulos.

Se conservan títulos y materias originales, incluso errores de transcripción. Una fotografía de «El Diego» puede pertenecer a un sobre titulado con un partido sin que su registro tenga a Maradona como materia; se mantiene esa diferencia real, sin agregar datos inventados.

La selección publicada excluye usuarios, contraseñas, roles, propietarios, actividad, favoritos de origen, colecciones privadas, ubicaciones físicas, rutas de discos, registros MARC completos y observaciones internas. Todos los campos de la demo son descargables: el carácter estático no ofrece control de acceso. No se concede una licencia abierta sobre las fotografías.
