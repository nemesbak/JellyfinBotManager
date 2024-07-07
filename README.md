# JellyfinBotManager
 Script Python para controlar el manejo de usuarios con bot de telegram

###Dependencias a Instalar
Esta es una biblioteca de Python para interactuar con la API de Telegram. Se puede instalar usando pip:
`pip install python-telegram-bot`

Para realizar solicitudes HTTP a la API de Jellyfin. Se puede instalar usando pip:
`pip install requests`

Aiohttp (opcional, pero usado en el script):
Para manejar solicitudes asíncronas de manera eficiente. Se puede instalar usando pip:
`pip install aiohttp`

###Configuración del Script
Antes de ejecutar el script, asegúrate de configurar correctamente los siguientes parámetros dentro del código:

JELLYFIN_URL: URL de tu servidor Jellyfin.
JELLYFIN_API_KEY: API Key de Jellyfin para la autenticación.
JELLYFIN_ADMIN_USERNAME: Nombre de usuario administrador de Jellyfin.
JELLYFIN_ADMIN_PASSWORD: Contraseña del administrador de Jellyfin.
TELEGRAM_TOKEN: Token del bot de Telegram que obtienes al crear un nuevo bot con el BotFather.


####Ejecución del Bot
Una vez que hayas configurado las dependencias y los parámetros, puedes ejecutar el bot:
Ejecuta el script Python en tu entorno local:
`python nombre_del_script.py`


###Uso del Bot en Telegram
Una vez que el bot está en funcionamiento, puedes interactuar con él a través de comandos en Telegram:

>/start: Inicia la conversación y muestra los comandos disponibles.
/crear_usuario: Comienza el proceso para crear un nuevo usuario en Jellyfin.
/modificar: Permite modificar parámetros de un usuario existente.
/password: Cambia la contraseña de un usuario.
/borrar: Elimina un usuario existente.
/estado: Muestra el estado actual de todos los usuarios y permite realizar acciones adicionales mediante botones interactivos.

Notas Adicionales
Asegúrate de tener correctamente configurados los permisos y la configuración de Jellyfin para que el bot funcione correctamente.
Este bot maneja la autenticación, creación de usuarios, modificación de políticas y eliminación de usuarios a través de la API de Jellyfin y utiliza la API de Telegram para la interacción con los usuarios.
*Con estos pasos, deberías poder configurar y ejecutar el bot de Telegram para la gestión de usuarios de Jellyfin sin problemas. Asegúrate de revisar los logs y mensajes de error en caso de cualquier problema durante la ejecución.*











Descripción del Repositorio:

Este repositorio alberga un bot de Telegram diseñado para gestionar usuarios de Jellyfin de manera eficiente. El bot permite realizar diversas acciones administrativas y facilita la gestión de usuarios en tu servidor Jellyfin directamente desde Telegram.

Agradecimientos Especiales:

Quiero expresar mi profundo agradecimiento a [nwithan8](https://gist.github.com/nwithan8 "nwithan8") por sus valiosas contribuciones que han inspirado y enriquecido este proyecto. Sus Gists en GitHub, especialmente [reset_jf_user](https://gist.github.com/nwithan8/399d3fae2d9d8639d633fbfbbafb8c91 "reset_jf_user") y [create_jf_user](https://gist.github.com/nwithan8/34c36c615a347dd576e0a8d157f69fc0 "create_jf_user"), han sido fuentes cruciales de inspiración y referencia durante el desarrollo de este bot. Su trabajo ha sido fundamental para implementar funcionalidades clave y mejorar la experiencia del usuario.
