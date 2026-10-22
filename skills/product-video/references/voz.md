# Voz y caché

## API key e identidad de voz

Son valores distintos: `ELEVENLABS_API_KEY` autentica la cuenta y es secreta;
`ELEVENLABS_VOICE_ID` selecciona la voz y no sustituye a la clave. El modelo
se configura aparte con `ELEVENLABS_MODEL_ID`.

Antes de pedirlos, reutiliza los valores autorizados para este vídeo en la
conversación y su configuración. Comprueba que la clave está definida sin
mostrar su contenido. El script carga el entorno y `<proyecto>/.env.local`;
para voz/modelo, los argumentos `--voz`/`--modelo` prevalecen sobre el entorno,
y el entorno sobre el archivo. Un `.env.local` en la raíz del repo no se
carga automáticamente: usa el entorno o señala la configuración del vídeo.

Si falta la clave, pide al usuario que la configure en el entorno o en el
archivo local ignorado por Git; comunica solo si está disponible, nunca su
valor. Si falta el id, pide el id de una voz de su cuenta. Guarda la elección
de voz/modelo/idioma en el brief para futuras sesiones. La clave permanece en
su fuente de secretos, fuera de guiones, comandos, logs, benchmarks y
entregables; no copies archivos de secretos de otro proyecto para trasladar
la skill.

Usa una voz accesible en esa cuenta y un modelo con alineación en
`convert_with_timestamps`. El acento depende de la voz: `--idioma es` no
convierte una voz latinoamericana en peninsular. Ante un rechazo de acceso,
conserva el guion y pide resolver el permiso; cambiar la voz requiere una
decisión del usuario.

### Continuar los vídeos de origen

La voz aprobada de `demo-video` era `Q7B7hOf48aY6RculD5H7`, con modelo
`eleven_v4_turbo`, idioma `es` y velocidad `1`. Si el usuario pide continuar
esos vídeos o usar la misma voz, conserva esa elección y comprueba el acceso
con la API key configurada. Es una referencia de continuidad, no una voz
predeterminada para cualquier cuenta o producto. La API key no forma parte
de la skill.

## Generación y reutilización

`voz.py` escribe `assets/vo/NN.raw.mp3`, `NN.mp3` y `vo.json` con palabras,
tiempos y metadatos por escena. Repetir el mismo texto, voz, modelo e idioma
reutiliza el audio crudo. `--velocidad` (0,5–2, por defecto 1) transforma ese
audio con FFmpeg y ajusta los tiempos sin otra petición al proveedor. Mantén
el mismo valor al repetir; un cambio invalida las tomas afectadas.

`--escuchar` genera `locucion-completa.mp3` en el orden del storyboard. Revisa
acento, pronunciación y ritmo antes de grabar. Una frase mal dicha se corrige
en el guion y solo se regenera esa frase. Si se cambió voz/modelo/idioma,
revisa el coste antes de regenerar todo. Consulta la tarifa de esa cuenta si
hace falta estimarlo: no presupongas créditos por carácter de otro plan.

Los `vo.json` antiguos sin audio crudo solo se adoptan si su identidad de
proveedor coincide. La migración de otro formato puede requerir regenerar
voz; no asumas que una caché histórica demuestra el idioma/modelo usados.

Si el usuario aporta una locución ya ajustada a la velocidad solicitada,
conserva ese audio y sus tiempos vigentes. `--velocidad` se aplica al audio
crudo del proveedor, no otra vez a un archivo ya ralentizado. Recupera los
tiempos de ese audio antes de regrabar; no estires dos veces la misma entrega.
