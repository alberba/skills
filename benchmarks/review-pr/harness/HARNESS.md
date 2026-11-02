# Condiciones del benchmark (mandan sobre la skill)

Revisas una PR siguiendo la skill que te indican. Estas condiciones prevalecen sobre ella:

- **Checkout**: tu directorio `wt/` está en el head de la PR. La base es la rama `origin/<base>` de ese mismo checkout (ya apunta al commit correcto); úsala siempre que la skill hable de la base. El diff es `git diff origin/<base>...HEAD`. No uses `gh pr diff` ni `gh api .../files`: pueden incluir commits posteriores.
- **GitHub**: solo `gh pr view <N> --repo <owner/repo> --json title,body,author,baseRefName,isDraft,commits`. Nada más de GitHub (reviews, comentarios, checks, issues), ni Sentry, ni historia posterior al head: se mide lo que encuentras por tu cuenta. Ignora `wt/.claude/skills/` y `wt/.agents/skills/`.
- **Entorno**: no levantes servicios (Docker, base de datos, servidores). Lo que solo se pueda probar con BD, menciónalo en el resumen de la review.
- **Salida, en el directorio del run** (padre de `wt/`):
  1. `findings.md`, escrito en cuanto cierres tu lista: una línea por hallazgo (`fichero:línea · gravedad · obligatorio/opcional · una frase`), y una sección `## Descartados` con lo que miraste y descartaste, y por qué.
  2. `payload.json`: la review exacta que habrías enviado (`commit_id`, `event`, `body`, `comments`). **No hagas el POST ni publiques nada.**
- **Respuesta final**: una sola línea, `hecho: N obligatorios, M opcionales`.
