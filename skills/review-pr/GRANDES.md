# Revisión de PRs grandes

Una sola pasada sobre un diff grande deja ficheros sin abrir y llena el contexto antes de llegar al detalle. Reparte la revisión por capas y cruza después los resultados.

1. **Reparto.** Lista los ficheros (`git diff --stat origin/<base>...HEAD`), salta los que no son código propio (docs, CSS, generados, lock files, volcados de datos) y asigna cada uno a una capa: API y permisos; servicios y modelos; tareas, comandos y migraciones; frontend y templates; tests. Una capa de más de unas 1.500 líneas se parte en dos. El diff se lee fichero a fichero (`git diff origin/<base>...HEAD -- <ruta>`).
2. **Una revisión por capa.** Lanza un subagente por capa, en paralelo, aunque la PR te parezca abarcable de una vez, con este encargo:

   ```
   Revisa la capa <capa> de la PR <N> (<owner/repo>), base origin/<base>, checkout en <ruta>.
   Ficheros: <lista>.
   Aplica a esos ficheros la Cobertura, el listón y Dónde buscar de <ruta de SKILL.md>; puedes abrir cualquier otro fichero para seguir llamadas, componentes y puntos de entrada.
   No leas reviews publicadas ni publiques nada.
   Devuelve una línea por hallazgo (`fichero:línea · gravedad · obligatorio/opcional · qué pasa · evidencia`) y una sección Descartados con lo que miraste y por qué lo descartas.
   ```

   Solo si tu entorno no tiene herramienta de subagentes, revisa tú capa a capa y cierra la lista de cada una antes de abrir la siguiente.
3. **Cruce.** Según vuelve cada capa, comprueba en el código sus hallazgos antes de aceptarlos y fija tú su gravedad con el listón de `SKILL.md`: una capa ve solo su parte y tiende a subirla. Con todas las listas: une los síntomas de una misma causa en un hallazgo anclado donde nace; pasa cada descarte por el listón de `SKILL.md`, porque una capa vista sola descarta de más; y mira lo que atraviesa capas: el mismo dato escrito desde dos puntos de entrada, un contrato que cambia en una capa y se consume en otra, un permiso que la API exige y el export no.

El reparto termina cuando cada fichero de código no saltado está en una capa y su revisión ha vuelto. Después sigue con **Orden** y **Publicación** de `SKILL.md`.
