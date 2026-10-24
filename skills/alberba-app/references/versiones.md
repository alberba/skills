# Versiones

Resolver cada versión el día de la generación. Una plantilla con una versión escrita a mano ya está vieja.

| Marcador | Cómo resolverlo |
| --- | --- |
| `{{checkout}}`, `{{setup-node}}`, `{{pnpm-action}}`, `{{setup-python}}`, `{{setup-uv}}`, `{{upload-artifact}}`, `{{setup-java}}`, `{{flutter-action}}` | `gh api repos/<dueño>/<repo>/releases/latest --jq .tag_name` y quedarse con la mayor (`v7`). Repos: `actions/checkout`, `actions/setup-node`, `pnpm/action-setup`, `actions/setup-python`, `astral-sh/setup-uv`, `actions/upload-artifact`, `actions/setup-java`, `subosito/flutter-action` |
| `{{node}}` | `curl -s https://nodejs.org/dist/index.json \| jq -r '.[0].version'`, la mayor (`26`) |
| `{{python}}` | `uv python list --only-downloads`: la versión estable más alta, sin `b`, `rc` ni `freethreaded` (`3.14`) |
| `{{java}}` | `curl -s https://api.adoptium.net/v3/info/available_releases \| jq -r .most_recent_lts` (`25`) |
| `{{postgres}}` | `curl -s 'https://hub.docker.com/v2/repositories/library/postgres/tags?page_size=100&ordering=last_updated' \| jq -r '.results[].name' \| grep -E '^[0-9]+$' \| sort -n \| tail -1` |

Librerías: instalarlas con `pnpm add <paquete>` o `uv add <paquete>` sin versión. Los generadores se ejecutan con `@latest`.

Una versión que no instala o rompe otra herramienta se trata así: fijar solo esa pieza, con un comentario junto a la línea que diga la causa y la condición para quitarla. Ejemplo: `scripts/eslint-typescript-api.mjs` en `nas-dashboard`, que mantiene la app en TypeScript 7 y redirige solo el proceso de ESLint a la API de TypeScript 6.

La ventana de edad manda sobre «última»: si una versión tiene menos de un día, pnpm instala la anterior y está bien así. Si `pnpm install` rechaza un paquete que fijaste, o necesitas hoy una versión concreta (un arreglo de seguridad), añadir su versión exacta a `minimumReleaseAgeExclude` en `pnpm-workspace.yaml` con un comentario, como hace `nas-dashboard`.
