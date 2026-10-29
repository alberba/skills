# Prompt de ejecución (v5)

Se entrega tal cual a un agente nuevo, sustituyendo `{SKILL_DIR}`, `{CASES}` y `{OUT}`. No se le da nada más: ni `checks.json`, ni `rubric.md`, ni otras salidas. Sin red ni escrituras externas.

---

Evalúas la skill de `{SKILL_DIR}`: lee `SKILL.md` y los ficheros que enlace.

Lee `{CASES}`. Para cada elemento de `cases`, actúa como si el usuario hubiera enviado `request` en un repositorio con las reglas de `common`. `evidence` sustituye cualquier consulta al código, a GitHub o a `gh`. No ejecutes nada contra servicios reales: cada decisión de crear o comentar se expresa como plan y no se ejecuta.

Escribe en `{OUT}` un array JSON con un objeto por caso y estos campos:

- `id`: el del caso.
- `action`: texto: una frase con la acción decidida.
- `title`, `body`, `brief`: texto exacto que se publicaría o quedaría tras editarlo, o `null` si no corresponde. `body` es el cuerpo de la issue nueva o editada, o el texto de un comentario que no lleva la especificación; `brief`, el de un comentario que lleva la especificación aparte (un Agent Brief o la estructura que exija el repo).
- `labels`: lista de textos con los labels que el plan deja en la issue afectada, completos.
- `questions`: lista de textos con las preguntas pendientes para el usuario.
- `operations`: objetos `{"operation", "target"}` con `operation` entre `create_issue`, `comment`, `edit_body`, `edit_comment`, `add_label`, `remove_label`. `target` es el repositorio, `#N` o la URL afectada. Un caso sin escrituras lleva `[]`.
- `commands`: lista de textos con los comandos `gh` exactos que ejecutarías, en orden, sin ejecutarlos; `[]` si no hay escrituras.
- `others`: solo si el caso exige más de una issue, lista de objetos `{"title","body","brief","labels"}` con las demás (los campos de arriba recogen la primera); si no, `[]`.
- `notes`: un único texto con las limitaciones y supuestos.

Responde solo con la ruta del fichero escrito.
