# Ejemplo sintético: cuerpo centrado en el impacto

El usuario de demostración no puede reutilizar los códigos de producto del CSV porque la exportación elimina sus ceros iniciales.

**Caso del fixture:** DEMO-P01 tiene el código **000842**, pero el archivo de prueba contiene **842**. DEMO-P02 tiene **052100** y aparece como **52100**.

**Esperado:** conservar los códigos textuales completos en las nuevas exportaciones y reprocesar las exportaciones pendientes, sin modificar los archivos ya descargados.

**Entorno:** demo-alpha. **Módulo:** exports. **Prioridad:** P1. **Origen:** escenario inventado para evaluación.

El historial del fixture contiene seis eventos; no representa seis usuarios distintos confirmados. El Agent Brief se publicaría en un comentario separado y se enlazaría desde el cuerpo. Este ejemplo no se ha publicado como incidencia real.
