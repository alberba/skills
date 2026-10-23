# Retrospectiva

Por orden de impacto en la versión actual.

1. **Leer lo publicado ancla la revisión.** Las skills que leían reviews previas confirmaban lo existente y encontraban poco nuevo. La v4 cierra su lista antes de leerlas: encontró por su cuenta los cuatro puntos ya publicados.
2. **El criterio de cobertura empuja más que los pasos.** Ocho pasos y una checklist por capa costaron más vueltas sin ganar hallazgos. Lo que trajo hallazgos nuevos fue exigir, para dar la revisión por terminada, que cada promesa (docstrings, documentación, implementación hermana) esté contrastada con el código.
3. **Lo que ejecuta el CI no es trabajo del revisor.** Lint, tests y comprobaciones de migraciones salen de la v4. Se mantiene solo lo que el CI no ve: migraciones probadas con filas sembradas, ida y vuelta.
4. **Las reglas de publicación funcionan como referencia, no como pasos.** Plantilla de resumen, comentario inline de tres frases y una revisión final del borrador llevaron el cumplimiento de 2 a 9 de las 10 reglas.
5. **Las instrucciones del resumen generaban ruido.** «Qué se revisó y qué se saltó», evaluación editorial y la métrica de simplificación aparecían como relato del proceso. Fuera.
6. **Una regla con la condición mal puesta disparó el coste.** «Suite completa si la PR toca configuración o dependencias» lanzó 3,5 min de tests en la PR A.
7. **Las pistas del caso concreto no van en la skill.** Una checklist que nombraba el bug conocido habría dado la respuesta al agente; se dejó genérica antes de medir.
