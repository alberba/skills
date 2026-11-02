# Betas

Reglas que se añaden a [create-release](../SKILL.md) en modo beta.

- **Tag:** la versión destino seguida de `-beta.N`, con N igual al mayor contador existente para esa versión más uno. Cuenta también los tags sin release para no colisionar.
- **Salto de versión:** si la versión destino cambia respecto de betas anteriores, explica el salto. Las betas anteriores se conservan.
- **Notas:** cubren todo el rango desde la última estable, identifican la subida y añaden los cambios desde la beta anterior de esa versión. Si no hay cambios incrementales, avisa antes de publicar.
- **Propuesta:** indica el contador, las betas previas y el rango incremental.
- **Publicación:** la beta se marca como prerelease.
- **Despliegue:** si el proyecto documenta cómo desplegar un tag beta en pruebas, comunica el comando; ejecútalo solo si el usuario lo pide.
