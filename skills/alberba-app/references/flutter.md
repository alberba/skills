# Flutter (Android)

La app Flutter vive en `mobile/` del mismo repo que la web y usa la misma API. iOS se cubre con la PWA.

## 1. Crear

Actualizar Flutter a la última estable (`flutter upgrade`) y generar:

```sh
flutter create --platforms=android --org <org> --project-name <nombre_snake_case> mobile
cd mobile
flutter pub add flutter_riverpod go_router http flutter_secure_storage
flutter pub upgrade --major-versions
```

Hecho = `flutter analyze` y `flutter test` pasan, y `flutter build apk --debug` genera el APK.

## 2. Convenciones

- Estado con Riverpod y su API `Notifier`, sin generación de código: sin `riverpod_generator` ni `build_runner`.
- Navegación con `go_router`, lint con `flutter_lints` (viene con `flutter create`) y tests con `flutter_test`.
- Diseño: los tokens de `DESIGN.md` pasan a `lib/theme/` (esquema de color, tipografía, radios y espaciado). Las fuentes van en `assets/fonts/` declaradas en `pubspec.yaml`.

## 3. Autenticación

El servidor activa el plugin `bearer()` de Better Auth; leer su documentación para la versión instalada. El cliente es una capa fina sobre `http`: tras iniciar sesión lee la cabecera `set-auth-token`, guarda el token con `flutter_secure_storage` y lo envía en `Authorization: Bearer`. La web sigue con cookies.

Hecho = iniciar sesión, cerrar la app y volver a abrirla mantiene la sesión.

## 4. Capa común

- Dependabot: añadir [assets/dependabot/pub.yml](../assets/dependabot/pub.yml). Mientras el ecosistema `pub` siga en beta, `dependabot.yml` lleva `enable-beta-ecosystems: true` bajo `version: 2`; comprobarlo en la documentación de Dependabot.
- CI: [assets/ci.flutter.yml](../assets/ci.flutter.yml) como `.github/workflows/mobile-ci.yml`. Las pruebas `integration_test` en emulador se ejecutan en local.
- La auditoría semanal no aplica a Flutter.

## 5. Firma y entrega

- Generar el keystore con `keytool` fuera del repo. `.gitignore` incluye `key.properties` y `*.jks`.
- Configurar `signingConfigs` en `android/app/build.gradle.kts` leyendo `key.properties`, según la guía «Build and release an Android app» de Flutter.
- Copiar [assets/release.flutter.yml](../assets/release.flutter.yml) a `.github/workflows/mobile-release.yml`. Un tag `vX.Y.Z` publica el APK firmado en GitHub Releases.
- Los secretos `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS` y `ANDROID_KEY_PASSWORD` los crea el usuario; crearlos es una acción remota de la sección 7 de `SKILL.md`.

Hecho = `flutter build apk --release` firma con el keystore local, y el workflow de release está en el repo con sus secretos listados para el usuario.
