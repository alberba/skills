# PWA

Toda app con interfaz es una PWA: cubre iOS y Android sin tienda. Escribir el código con la documentación oficial del momento: en TanStack con Vite, la de [Vite PWA](https://vite-pwa-org.netlify.app/); en Astro, la de `@vite-pwa/astro`. En TanStack Start, comprobar la integración con SSR y registrar el service worker solo en el cliente.

## 1. Base

- Manifest con nombre, `short_name`, `start_url`, `display: standalone`, `theme_color` y `background_color` tomados de `DESIGN.md`. Servir `public/manifest.webmanifest` y enlazarlo desde el documento raíz o layout; si el plugin PWA lo genera, configurarlo allí.
- Iconos de 192 y 512 con propósito `any`, un icono aparte `maskable` y un `apple-touch-icon`.
- Un componente que explique la instalación en iOS cuando el navegador es Safari y la app aún no corre en modo `standalone`: «Compartir → Añadir a pantalla de inicio». iOS no ofrece botón de instalar.
- Un test de Playwright que pide el manifest y comprueba que responde 200 con JSON válido (`application/manifest+json`), que tiene nombre y `display: standalone`, y que los iconos de 192 y 512 existen.

Hecho = el test pasa y la app se sirve por HTTPS.

## 2. Sin conexión (opcional)

Solo si el arranque lo pidió. TanStack con Vite: `vite-plugin-pwa`; comprobar su compatibilidad con el build y SSR del proyecto. Astro: `@vite-pwa/astro`. Definir qué rutas y datos pueden guardarse sin conexión, excluyendo respuestas privadas del caché compartido.

Hecho = con el service worker activo, recargar la página sin red muestra la app.

## 3. Push (opcional)

Solo si el arranque lo pidió. Añadir los manejadores de push al service worker; si lo genera un plugin PWA, usar su modo de worker personalizado (`injectManifest`) para integrar caché y push en un solo worker. Usar `web-push` en el backend propio o un servicio externo compatible, y documentar las claves VAPID en `.env.example`. En iOS funciona desde la versión 16.4 y solo con la app instalada. `sw.js` se sirve con `Cache-Control: no-cache, no-store, must-revalidate`.

Hecho = una notificación de prueba llega a un navegador con la app instalada.

## 4. Comprobación en iPhone

Ninguna prueba automática cubre la instalación en iOS. Pedir al usuario que instale la app desde Safari, la abra desde la pantalla de inicio y confirme que se ve a pantalla completa.

Hecho = el usuario ha confirmado la instalación, o consta que queda pendiente.
