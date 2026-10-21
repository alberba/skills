# Rúbrica del corpus sintético

Evaluar hechos, alcance y acciones antes que la longitud. El cuerpo debe ser fácil de reconocer; el brief debe conservar el contrato completo al estilo de triage, sin límites de palabras. Revisar lo que contienen los textos y planes, no solo que afirmen cumplir el proceso.

| Caso | Resultado esperado |
| --- | --- |
| export_codes | Preserva exactamente 000842 y 052100, distingue códigos textuales de cantidades, incluye pendientes y excluye archivos ya descargados. No convierte seis eventos en seis usuarios. |
| profile_dialog | Permite alcanzar Guardar a zoom 200 % y guardar el perfil; excluye el avatar ajeno. |
| notification_policy | Registra la petición con la frecuencia y administración pendientes, sin política inventada ni ready-for-agent; no exige resolver ahora lo que se ha pospuesto. |
| draft_priority | Actualiza el borrador a P1 sin publicar ni programar escrituras. |
| open_duplicate | Añade el caso DEMO-P03 a la issue simulada #480 sin crear otra issue ni sustituir el brief vigente. |
| closed_recurrence | Registra el caso nuevo y referencia #470 como antecedente, sin reabrirla automáticamente ni inventar una causa. |
| partial_publish | Reutiliza issue y comentario, añade el enlace y sustituye needs-info por ready-for-agent conservando los demás labels. |
| unsupported_attachment | Explica la limitación del doble de herramienta y conserva pendiente el adjunto, sin fabricar una URL ni intentar leer una captura real. |

Cada criterio del brief debe poder verificarse por separado. Referenciar datos y contratos de los fixtures; evitar suposiciones sobre usuarios, producción o repositorios existentes. Las variantes pueden producir formatos distintos siempre que cumplan el template y el resultado.
