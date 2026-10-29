# Ejemplo sintético: cuerpo autocontenido

Título: `[Bug]: La exportación CSV elimina los ceros iniciales de los códigos de producto`

```markdown
## Descripción del problema

El usuario de demostración no puede reutilizar los códigos de producto del CSV porque la exportación elimina sus ceros iniciales.

**Actual:** DEMO-P01 tiene el código 000842 y el archivo contiene 842; DEMO-P02 tiene 052100 y aparece como 52100.
**Esperado:** el CSV conserva el código textual completo.

## Entorno demo

demo-alpha

## Módulo

exports

## Origen

Escenario inventado para evaluación.

## Información adicional

El historial del fixture contiene seis eventos; no representa seis usuarios distintos confirmados.

## Para implementar

**Objetivo:** el código de producto (`ExportRow.product_code`) en la exportación CSV de demo-alpha.

**Terminado cuando:**
- [ ] Una exportación nueva de DEMO-P01 y DEMO-P02 contiene 000842 y 052100.
- [ ] Las tres exportaciones pendientes se reprocesan con los códigos completos.
- [ ] Cantidades e importes del CSV mantienen su comportamiento actual.

**Evidencia:** fixture simulado, sin verificar contra un servicio.

**Dónde mirar:** `ExportRow` trata `product_code` como texto; el serializador lo convierte a entero.

**Fuera de alcance:** los archivos ya descargados no se modifican.
```

Este ejemplo no se ha publicado como incidencia real.
