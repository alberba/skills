# PWA

Toda app con interfaz es una PWA: cubre iOS y Android sin tienda. Escribir el código con la documentación oficial del momento: en Next, la guía `node_modules/next/dist/docs/01-app/02-guides/progressive-web-apps.md`; en Astro, la de `@vite-pwa/astro`.

## 1. Base

- Manifest con nombre, `short_name`, `start_url`, `display: standalone`, `theme_color` y `background_color` tomados de `DESIGN.md`. En Next, `app/manifest.ts`; en Astro, `public/manifest.webmanifest` enlazado desde el layout.
- Iconos de 192 y 512 con propósito `any`, un icono aparte `maskable` y un `apple-touch-icon`.
- Un componente que explique la instalación en iOS cuando el navegador es Safari y la app aún no corre en modo `standalone`: «Compartir → Añadir a pantalla de inicio». iOS no ofrece botón de instalar.
- Un test de Playwright que pide el manifest y comprueba que responde 200 con JSON válido (`application/manifest+json`), que tiene nombre y `display: standalone`, y que los iconos de 192 y 512 existen.

Hecho = el test pasa y la app se sirve por HTTPS.

## 2. Sin conexión (opcional)

Solo si el arranque lo pidió. Next: service worker con Serwist; comprobar en su documentación que funciona con el bundler que Next usa hoy. Astro: `@vite-pwa/astro`.

Hecho = con el service worker activo, recargar la página sin red muestra la app.

## 3. Push (opcional)

Solo si el arranque lo pidió. Service worker escrito a mano como en la guía de Next, `web-push` y claves VAPID en `.env.example`. En iOS funciona desde la versión 16.4 y solo con la app instalada. `sw.js` se sirve con `Cache-Control: no-cache, no-store, must-revalidate`.

Hecho = una notificación de prueba llega a un navegador con la app instalada.

## 4. Comprobación en iPhone

Ninguna prueba automática cubre la instalación en iOS. Pedir al usuario que instale la app desde Safari, la abra desde la pantalla de inicio y confirme que se ve a pantalla completa.

Hecho = el usuario ha confirmado la instalación, o consta que queda pendiente.
