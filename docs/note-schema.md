---
aliases: [Note Schema, Schema de Notas, Note_Schema]
tags: [meta, lumina, quant]
id: DOC-SCHEMA
title: "Note Schema and Vault Governance"
type: meta
category: governance
status: stable
related: ["[[decision-maker-moc]]", "[[index]]", "[[database-hub]]", "[[kanban]]"]
created: 2026-08-10
updated: 2026-09-27
---

## Skeleton Canónico

> Es la forma única de escribir una nota nueva en este vault.
> Uso: copiar el bloque de abajo y rellenar los tres párrafos del blockquote.
> No define qué módulos merecen nota (ver el MOC, categoría 2 y 3).

```markdown
---
aliases: [Alias legible, Alias alternativo]
tags: [module, lumina, quant, <tema>]
id: DOC-<SLUG>
title: "Título legible"
type: module
category: <eje>
status: draft
related: ["[[decision-maker-moc]]", "[[index]]"]
created: 2026-09-27
updated: 2026-09-27
module: "decision_maker.core.modulo"
class: "ClasePrincipal"
---

# Título

## `modulo.py`

> Qué hace este módulo.
>
> Uso: `from decision_maker.core.modulo import Clase`
> No: qué queda explícitamente fuera de su alcance.

### Clases Principales

- **`ClasePrincipal`**: una línea de rol, no de firma.

---
```

### Los doce campos y cuáles son obligatorios

El skeleton mostraba sólo `aliases` y `tags`; en el vault hay **13 campos en uso**. La tabla los separa por obligatoriedad real, medida el 28-Sep-2026 sobre las 54 notas:

| Campo | Obligatorio | Presente en | Para qué |
|---|---|---|---|
| `aliases` | sí | 54/54 | Nombres antiguos por los que el enlace todavía resuelve. |
| `tags` | sí | 54/54 | Los cuatro ejes, ver abajo. |
| `id` | sí | 54/54 | Clave estable; el registro de [[database-hub]] lo cita. |
| `title` | sí | 54/54 | Título legible, independiente del nombre de archivo. |
| `type` | sí | 54/54 | Uno de los 12 valores medidos: `module`, `archive`, `moc`, `meta`, `narrative`, `adr`, `architecture`, `changelog`, `worklog`, `guide`, `kanban`, `roadmap`. |
| `category` | sí | 54/54 | Eje temático; coincide con la primera palabra de `tags`. |
| `status` | sí | 54/54 | `draft` \| `stable` \| `deprecated`. |
| `related` | sí | 54/54 | Wikilinks, entre comillas, siempre. |
| `updated` | sí | 54/54 | Fecha de la última revisión real del contenido. |
| `created` | sí | 54/54 | Primera aparición **en este vault**. Para 10 notas se recuperó del primer commit de git; las 6 de `sw-diagnosticoremoto/` y `tests-results/` no tienen procedencia en el historial, así que su fecha es la de entrada al vault (27-Sep-2026), no la de autoría. Faltaban en 16 y se rellenaron el 28-Sep-2026. |
| `module` | sólo `type: module` | 21/21 | Ruta completa del módulo. Es un **canal de propiedad**: debe concordar con el heading `## \`modulo.py\`` y con la fila del registro. |
| `class` | sólo `type: module` | 21/21 | Clase principal del módulo. |
| `kanban-plugin` | sólo `type: kanban` | 2/2 | Configuración del tablero. |

`module` y `class` se declaran también en el skeleton porque el bloque tiene que ser copiable tal cual, pero sólo aplican a fichas de módulo. `test_docs_fidelity.py` verifica que los tres canales de propiedad concuerden.

**Un `##` por módulo.** El outline de Obsidian es la navegación del vault: un H2 que nombra dos archivos (`a.py & b.py`) produce un nodo que no es un módulo y mezcla las clases de ambos. Cuando dos módulos van juntos, son dos H2 — como ya hace [[data-models-and-schemas]].

**Sin `---` al final del archivo.** El separador `---` es *entre* bloques de módulo. Como terminador se ve en lectura como una regla colgada sin nada debajo. Es lo mismo que se hacía en 12 de 13 notas; aquí se elimina.

**Los tres párrafos del blockquote van separados por línea en blanco.** Con las tres líneas en un solo bloque lazy (lo que había antes), Markdown las junta en **un** párrafo y el lector pierde los tres roles. Con un `>` por párrafo se leen tres, sin depender del ajuste "Strict line breaks" de Obsidian.

## Vocabulario de Tags

Cuatro ejes. Todos en minúscula, palabras compuestas siempre con guion.

| Eje | Regla | Valores |
|---|---|---|
| Tipo | Qué es la nota. `module` = documenta un `.py` del paquete. `moc` = índice. `meta` = gobernanza del vault. `archive` = histórico, fuera del control de idioma. | 12 — los mismos que acepta el campo `type`, y `test_docs_schema.py` los compara. |
| Proyecto | `lumina`, `quant`. **Presentes en las 54 notas.** Antes vivían sólo en el MOC, así que `tag:#lumina` devolvía una sola nota: el índice, que es la que nunca debería ser la respuesta. | 2 |
| Tema | Al menos uno por nota `module`. | resto |
| Autoría | `taleb`, `jaynes`, `mcelreath`. **Sólo tags.** Ver abajo. | 3 |

`component` se eliminó de las notas que lo tenían: aparecía siempre pegado a `module` y nunca solo, así que no distinguía nada.

**El vocabulario completo son 58 valores y no se enumera aquí a propósito.** Una lista de 58 valores escrita en prosa es un índice que nadie mantiene: cuando se revisó ya nombraba 44 que no estaban, y una lista así se pudre más rápido de lo que se lee. Lo que se declara es la **regla** de los cuatro ejes, y el conteo va fijado en `test_docs_schema.py`: ese test se pone rojo si el número cambia, así que un tag nuevo obliga a decidir si pertenece a un eje o a actualizar el número a propósito.

**El tag `archive` excluye del control de idioma, y excluye mucho.** Hoy son 25 de 54 notas, y entre ellas [[database-hub]] (37 enlaces entrantes) y [[kanban]]. El tag mezcla dos intenciones —"esto es histórico" y "esto está en otro idioma"— y por eso alcanza a las dos notas más consultadas del vault. Se mantiene porque el filtro es correcto, pero el número está fijado en el test: si alguien confunde `archive` con `deprecated`, el CI se pone rojo en vez de silenciosamente dejar de verificar 25 notas.

## Los dos axes que no se mezclan

- **Personas son tags, no wikilinks.** El MOC enlazaba `Nassim Taleb` y `E.T. Jaynes` a notas que no existen, mientras las mismas personas ya estaban como tags `taleb`/`jaynes` en las notas. Dos representaciones del mismo hecho, ya divergidas 3 contra 2. Se elige el eje de tags; los enlaces se desvanecen a texto plano.
- **`Dev-Agents Foundation` no es una nota de este vault.** Es un directorio fuera del repo (`~/.config/opencode/dev-agents/`). Ningún wikilink puede resolverlo, porque no es un destino posible.

## Convención de Nombres de Archivo

`lowercase-with-hyphens`. Única excepción: `README.md`, que GitHub, GitLab y el resto de plataformas ya leen como la portada de un directorio, así que una convención propia no aporta nada ahí.

El porqué no es estético: las 15 notas de este vault se llamaban `AHP.md`, `TOPSIS.md`, `Monte_Carlo_Engine.md`, y un wikilink escrito con otro caso o con `_` no las abre. La resolución de Obsidian es sensible a mayúsculas en Linux y en GitHub, así que el nombre del archivo **es** parte del contrato del enlace.

## Regla de Idioma

MOC, narrativas y notas de gobernanza en **español**. La ficha de referencia de un módulo se escribe en el idioma que mejor explique el mecanismo, y el vault hoy es mixto a propósito: de las 29 notas que el control de idioma verifica, 17 son español y 12 inglés.

Lo que **no** es opcional es la ausencia de intruders: una nota en español no lleva un token inglés incrustado en la frase, ni al revés. Eso es lo que `check_obsidian_language.py` mide, nota por nota, y no depende de qué idioma se elija para la nota.

La regla se cambió el 28-Sep-2026 porque la anterior —"fichas de módulo siempre en inglés"— ya no se sostenía: `robust-optimization.md` y `bootstrap-ranking.md` eran las dos fichas en inglés, y las dos describían mal su módulo. Al corregirlas contra el código, el inglés no tenía nada que aportar y la frontera quedó artificial. **Lo que la cambiaría de vuelta:** que el mantenedor vuelva a escribir módulos en inglés de forma consistente; entonces se reinvierte entera de una vez, no nota por nota.

## Qué cambiaría estas decisiones

- **Raíz del vault = `docs/`.** Cambió desde `docs/obsidian/` el 27-Sep-2026. La razón original —que la raíz del repo metería `results/` (~300 reportes generados) y `.venv/` en el grafo— era cierta pero arrancaba de otra capa: aplicaba a la **raíz del repo**, no a `docs/`. Bajo `docs/` los 54 archivos `.md` son todos documentación, y no hay `results/`, `.venv/`, `node_modules/` ni `__pycache__`. Lo que se ganó fue alcance: con la raíz en `docs/obsidian/`, `index.md`, `architecture.md`, `guide.md`, `adr/` y `reorganization/` quedaban fuera del grafo e inalcanzables por wikilink.

  **Lo que la cambiaría:** contenido *generado por el proyecto* dentro de `docs/` —un `docs/results/`, un `docs/.venv`, un `docs/node_modules/`— y no un cambio de gusto.

  **Una salvedad que esta versión corrige:** la primera redacción decía "archivos generados dentro de `docs/`" sin más, y se cumplía sola con `.obsidian/`, que es metadata del vault y no contenido del proyecto. Obsidian escribe ahí por diseño, así que la regla tiene que excluirlo explícitamente o no es una regla: es un disparador que se dispara solo. La forma de detectarlo ya no es leer el criterio, es medir: `check_docs_scope.py` verifica que bajo `docs/` no exista ningún directorio generado, con `docs/.obsidian/` en la lista de excepciones.

- **`.obsidian/` sólo en `docs/`, nunca en la raíz del repo.** El 28-Sep-2026 hubo dos copias byte-idénticas de 1.1 MB, una en cada sitio, y ninguna de las dos estaba en `.gitignore`. La de la raíz es la peligrosa: abrir el repo en Obsidian con un `.obsidian/` arriba convierte **todo el repositorio** en el vault, que es exactamente el problema que motivó mover la raíz a `docs/`. Se borró la de la raíz y se añadió `/.obsidian/` al `.gitignore` del repo. **Lo que la cambiaría:** nada foreseeable; si alguien necesita abrir el repo completo como vault, es una decisión distinta y deliberada, no un descuido de limpieza.
- **Los archivos generados de los plugins no se versionan, su `manifest.json` sí.** `main.js` y `styles.css` son ~1 MB de código generado por plugin. `manifest.json` es la fuente de verdad de qué plugin y qué versión, así que sin él un clon nuevo se queda sin plugins en silencio. Regla en el `.gitignore` raíz.
- **El vocabulario de tags no se enumera.** Ver arriba: la regla de los cuatro ejes es lo que se declara; el conteo de 58 vive en un test que puede ponerse rojo.
