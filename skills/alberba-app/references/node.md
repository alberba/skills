# Node

- `package.json` fija `packageManager` con la versión de pnpm actual (`pnpm -v`). Los scripts `typecheck` (`tsc --noEmit --incremental false`), `lint`, `test` (`vitest run`), `build`, `test:e2e` (`playwright test`) y `audit:prod` existen con esos nombres.
- `pnpm-workspace.yaml`: añadir las claves de [assets/pnpm-workspace.yml](../assets/pnpm-workspace.yml) al fichero que ya hay, sin reemplazarlo.
- TypeScript 7 con ESLint: si `pnpm lint` falla al cargar `typescript`, instalar `pnpm add -D typescript-api@npm:typescript@6`, copiar [assets/eslint-typescript-api.mjs](../assets/eslint-typescript-api.mjs) a `scripts/` y definir `lint` como `node --import ./scripts/eslint-typescript-api.mjs ./node_modules/eslint/bin/eslint.js`. Quitarlo cuando ESLint lea TypeScript 7.
- Dependabot: bloques [assets/dependabot/pnpm.yml](../assets/dependabot/pnpm.yml) y, si hay `Dockerfile`, [docker.yml](../assets/dependabot/docker.yml); siempre [actions.yml](../assets/dependabot/actions.yml). Ajustar los `patterns` de los grupos a las dependencias reales del proyecto: un grupo por familia que se rompe junta (React; Next o Astro con sus adaptadores; Better Auth). Una dependencia entra en el primer grupo que coincide.
- Auditoría: [assets/audit.pnpm.yml](../assets/audit.pnpm.yml), con el script `audit:prod` (`pnpm audit --prod --audit-level high`) en `package.json`.
- CI: [assets/ci.pnpm.yml](../assets/ci.pnpm.yml). Añadir el servicio de Postgres solo si el proyecto lo usa, con la imagen `{{postgres}}`.
- Tests: Vitest para unitarios y Playwright para E2E. Instalar el navegador en CI con `pnpm exec playwright install --with-deps chromium`.
