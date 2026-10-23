# Rúbrica

## Precisión de los hallazgos (0–10 cada criterio)

1. **Veracidad:** el hallazgo es técnicamente correcto.
2. **Contexto:** se revisó el código relacionado, las validaciones y los contratos, incluidas las decisiones que la PR declara.
3. **Reproducibilidad:** el escenario es alcanzable; mejor si se ejecutó.
4. **Regresión:** lo introduce o agrava la PR, comprobado contra la base.
5. **Impacto:** la gravedad es proporcional a la consecuencia real.
6. **Sugerencias:** la corrección propuesta es correcta y no introduce regresiones.
7. **Falsos positivos:** sin hallazgos incorrectos, duplicados, especulativos o de estilo.
8. **Evidencia:** argumentos verificables con código, contratos, tests o salidas; hipótesis marcadas como tales.

Se añaden **cobertura** (hallazgos reales encontrados por la ejecución, frente a la unión verificada de todas las ejecuciones) y **eficiencia** (coste y tiempo). La nota global pondera la cobertura y la evidencia por encima del resto.

## Publicación (cumple / parcial / no cumple)

1. Prioriza al lector: qué corregir y por qué, a la primera.
2. Resumen breve: valoración, hallazgos importantes, validaciones y bloqueantes; sin relatar el proceso.
3. Detalle en los comentarios inline, sin duplicarlo en el resumen.
4. Concisión: problema, impacto y solución en el mínimo texto preciso.
5. Lenguaje natural, sin referencias internas del agente.
6. Sin repeticiones: lo ya publicado solo se enlaza si sigue pendiente.
7. Conclusiones accionables: obligatorio frente a opcional.
8. Evidencia proporcional: pruebas y limitaciones resumidas.
9. Prioridad consistente con el impacto en producción.
10. Sin ruido: fuera lo preexistente, lo saltado y lo que no ayuda a decidir.
