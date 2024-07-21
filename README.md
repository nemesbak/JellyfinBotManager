### Version 2.0 de un bot simple para manejo de usuarios a traves de telegram

-------------------------------------------------------------
## Uso con Docker Compose en local
1. Clona este repositorio
2. Ajusta las variables en `docker-compose.yml` según sea necesario
3. Ejecuta `docker-compose up -d`

## Uso con Docker
1. Clona este repositorio
2. Crea un archivo `.env` con las variables necesarias
3. Construye la imagen:
```
`docker build -t jfa-bot .`
```
4. Ejecuta el contenedor:
```
`docker run --env-file .env -d jfa-bot`
```
------------------------------------------------------------
## Use with Docker Compose on local
1. Clone this repository
```
git clone https://github.com/nemesbak/jellyfinbotmanager
cd jellyfinbotmanager
```
2. Adjust variables in `docker-compose.yml` as needed
3. Run
```
`docker-compose up -d`
```

## Use with Docker
1. Clone this repository
2. Create a `.env` file with the necessary variables
3. Build the image: ``` `docker build -t jfa-bot .` ```
4. Run the container: ``` `docker run --env-file .env -d jfa-bot` ```

-------------------------------------------------------------
## Use with Docker Compose Online
```
version: '3.8'
services:
  bot:
    image: nemesbak/jfa-bot:latest
    container_name: jfa-bot
    environment:
      - TELEGRAM_TOKEN=
      - JELLYFIN_URL=
      - JELLYFIN_API_KEY=
      - JELLYFIN_ADMIN_USERNAME=
      - JELLYFIN_ADMIN_PASSWORD=
      - JELLYFIN_LOGO_URL=
    restart: unless-stopped
    volumes:
      - /patch/of/config:/app/config
      - /patch/of/config:/app/logs
```
-----------------------------------------------------------
# JellyfinBotManager
 Script Python para controlar el manejo de usuarios con bot de telegram

### Configuración del Script
Antes de ejecutar el script, asegúrate de configurar correctamente el .env en los siguientes parámetros dentro del código:

- **JELLYFIN_URL**: URL de tu servidor Jellyfin.
- **JELLYFIN_API_KEY**: API Key de Jellyfin utilizada para la autenticación.
- **JELLYFIN_ADMIN_USERNAME**: Nombre de usuario del administrador de Jellyfin.
- **JELLYFIN_ADMIN_PASSWORD**: Contraseña del administrador de Jellyfin.
- **TELEGRAM_TOKEN**: Token del bot de Telegram que se obtiene al crear un nuevo bot con el BotFather.
- **JELLYFIN_LOGO_URL:** Puedes personalizar mensaje bienvenida para que muestre un logo o imagen personalizada



#### Sugerencias
Si tienes alguna sugerencia, mejora, critica o simplemente puedes corregir y mejorar algo adelante, puedes contactarme por telegram @nemesfpv
y comentarme lo que sea :)

### Uso del Bot en Telegram
Una vez que el bot está en funcionamiento, puedes interactuar con él a través de comandos en Telegram:
> /start: Inicia la conversación y muestra los comandos disponibles.
>
> /crear_usuario: Comienza el proceso para crear un nuevo usuario en Jellyfin.
>
> /password: Cambia la contraseña de un usuario.
>
> /borrar: Elimina un usuario existente.


## Notas Adicionales

- Asegúrate de configurar correctamente los permisos y la configuración de Jellyfin para el funcionamiento correcto del bot.
- Este bot utiliza la API de Jellyfin para la gestión de usuarios y la API de Telegram para la interacción con los usuarios.
- Revisa los logs y mensajes de error en caso de cualquier problema durante la ejecución del bot.

---

## Descripción del Repositorio

Este repositorio contiene un bot de Telegram diseñado para gestionar usuarios de Jellyfin de manera eficiente. Facilita diversas acciones administrativas directamente desde Telegram en tu servidor Jellyfin.

### Agradecimientos Especiales

Agradezco a [nwithan8](https://gist.github.com/nwithan8) por sus contribuciones que han inspirado y enriquecido este proyecto. Sus Gists en GitHub, especialmente [reset_jf_user](https://gist.github.com/nwithan8/399d3fae2d9d8639d633fbfbbafb8c91) y [create_jf_user](https://gist.github.com/nwithan8/34c36c615a347dd576e0a8d157f69fc0), han sido fundamentales durante el desarrollo de este bot, mejorando significativamente la experiencia del usuario.

---
