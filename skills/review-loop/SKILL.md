---
name: review-loop
description: "Bucle de review con isitech-bot hasta su aprobación con CI en verde. Usar al abrir una PR, o al pedir review del bot o llevar una PR a aprobada."
---

Lleva la PR `N` hasta la aprobación de isitech-bot. `<SKILL_DIR>` es la ruta absoluta de esta carpeta.

Lanzar este bucle autoriza sus commits sin preguntar. Siguen la convención del repo; si esta pide registrar tiempo en cada commit, los del bucle registran `0m`: el tiempo de la tarea ya va en el commit de implementación.

## Pasos

1. **Ronda.** Pide la review y espera a que se publique:

   ```bash
   bash <SKILL_DIR>/scripts/review.sh N
   ```

   Bloquea unos minutos. Imprime el `ESTADO`, el cuerpo y cada comentario inline con su id. Si sale con error, sigue su mensaje; si el run del bot falla dos veces seguidas, para e informa. Con otro bot, exporta `REVIEW_BOT` y `REVIEW_WORKFLOW` (por defecto `isitech-bot` y `claude-review.yml`).

2. **Corrige.** Atiende cada punto de la review, inline y del cuerpo, `obligatorio` y `opcional` por igual. Aplica el cambio, o deja el código como está si el punto es incorrecto. Verifica con los tests que toquen, haz commit y `git push`.

   Responde cada comentario inline en su hilo con lo hecho (`Hecho: …`) o el motivo para no aplicarlo:

   ```bash
   gh api repos/{owner}/{repo}/pulls/N/comments/<id>/replies -f body='…'
   ```

   Los puntos del cuerpo que no apliques, explícalos en un comentario de la PR.

3. **CI.** `gh pr checks N --watch`. Si algo falla, `gh run view <run> --log-failed`, corrige, push y espera de nuevo hasta verde.

4. **Decide.** `CHANGES_REQUESTED` o `COMMENTED`: vuelve al paso 1. `APPROVED`: el paso 2 ya aplicó sus puntos; termina sin pedir otra review.

**Hecho** cuando la última review del bot es `APPROVED`, cada uno de sus puntos está aplicado o respondido, y `gh pr checks N` sale en verde sobre el último commit.

## Retro

Si alguna review del bucle fue `CHANGES_REQUESTED` y el proyecto tiene la skill `retro`, lee y sigue su `SKILL.md` (en la carpeta hermana `../retro/`; solo se invoca a mano: léela, no la lances con la herramienta Skill). Céntrala en los puntos `obligatorio` de esas reviews: qué check, estándar de código o doc habría evitado que llegaran a la PR.
