import os
import requests
import random
import string
import socket
import aiohttp
from dotenv import load_dotenv
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Configuración de Jellyfin
JELLYFIN_URL = os.getenv('JELLYFIN_URL')
JELLYFIN_API_KEY = os.getenv('JELLYFIN_API_KEY')
JELLYFIN_ADMIN_USERNAME = os.getenv('JELLYFIN_ADMIN_USERNAME')
JELLYFIN_ADMIN_PASSWORD = os.getenv('JELLYFIN_ADMIN_PASSWORD')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
JELLYFIN_LOGO_URL = os.getenv('JELLYFIN_LOGO_URL')

JELLYFIN_USER_POLICY = {
    "IsAdministrator": False,
    "IsHidden": True,
    "IsHiddenRemotely": True,
    "IsDisabled": False,
    "EnableRemoteControlOfOtherUsers": False,
    "EnableSharedDeviceControl": False,
    "EnableRemoteAccess": True,
    "EnableLiveTvManagement": False,
    "EnableLiveTvAccess": False,
    "EnableMediaPlayback": True,
    "EnableAudioPlaybackTranscoding": False,
    "EnableVideoPlaybackTranscoding": False,
    "EnablePlaybackRemuxing": True,
    "EnableContentDeletion": False,
    "EnableContentDownloading": False,
    "EnableSyncTranscoding": False,
    "EnableMediaConversion": False,
    "EnableAllDevices": True,
    "EnableAllChannels": True,
    "EnableAllFolders": True,
    "InvalidLoginAttemptCount": 0,
    "LoginAttemptsBeforeLockout": -1,
    "RemoteClientBitrateLimit": 0,
    "EnablePublicSharing": False,
    "AuthenticationProviderId": "Jellyfin.Server.Implementations.Users.DefaultAuthenticationProvider",
    "PasswordResetProviderId": "Jellyfin.Server.Implementations.Users.DefaultPasswordResetProvider"
}

# Estados para la conversación
ESPERANDO_NOMBRE_USUARIO = 1
ESPERANDO_USUARIO_PASSWORD = 2
ESPERANDO_NUEVA_PASSWORD = 3
ESPERANDO_USUARIO_BORRAR = 4
ESPERANDO_CONFIRMACION_BORRAR = 5

# Funciones auxiliares
def make_password():
    return ''.join(random.choices(string.digits, k=6))

def authenticate():
    xEmbyAuth = {
        'X-Emby-Authorization': 'Emby UserId="", Client="account-automation", '
                                f'Device="{socket.gethostname()}", DeviceId="{hash(socket.gethostname())}", '
                                'Version="1", Token=""'
    }
    data = {
        'Username': JELLYFIN_ADMIN_USERNAME,
        'Password': JELLYFIN_ADMIN_PASSWORD,
        'Pw': JELLYFIN_ADMIN_PASSWORD
    }
    try:
        res = requests.post(f'{JELLYFIN_URL}/Users/AuthenticateByName', headers=xEmbyAuth, json=data)
        res.raise_for_status()
        return res.json()['AccessToken']
    except Exception as e:
        return None

def make_user(username, token):
    headers = {
        'X-Emby-Token': token,
        'Content-Type': 'application/json'
    }
    data = {'Name': username}
    try:
        res = requests.post(f'{JELLYFIN_URL}/Users/New', headers=headers, json=data)
        res.raise_for_status()
        return res.json()['Id']
    except Exception as e:
        return None

def set_user_password(user_id, new_password, token):
    headers = {
        'X-Emby-Token': token,
        'Content-Type': 'application/json'
    }
    data = {
        'Id': user_id,
        'CurrentPw': '',
        'NewPw': new_password
    }
    try:
        res = requests.post(f'{JELLYFIN_URL}/Users/{user_id}/Password', headers=headers, json=data)
        res.raise_for_status()
        return True
    except Exception as e:
        return False

def update_user_policy(user_id, token):
    headers = {
        'X-Emby-Token': token,
        'Content-Type': 'application/json'
    }
    try:
        res = requests.post(f'{JELLYFIN_URL}/Users/{user_id}/Policy', headers=headers, json=JELLYFIN_USER_POLICY)
        res.raise_for_status()
        return True
    except Exception as e:
        return False

def get_user_id(username, token):
    headers = {'X-Emby-Token': token}
    try:
        res = requests.get(f'{JELLYFIN_URL}/Users', headers=headers)
        res.raise_for_status()
        users = res.json()
        for user in users:
            if user['Name'] == username:
                return user['Id']
        return None
    except Exception as e:
        return None

# Funciones del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "¡Bienvenido al Bot de Gestión de Usuarios de Jellyfin! 🎉\n\n"
        "Este bot te ayudará a gestionar las cuentas de usuario en nuestro servidor Jellyfin.\n\n"
        "Comandos disponibles:\n"
        "/crear_usuario - Crear un nuevo usuario\n"
        "/password - Cambiar la contraseña de un usuario\n"
        "/borrar - Eliminar un usuario existente"
    )
    
    if JELLYFIN_LOGO_URL:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(JELLYFIN_LOGO_URL) as response:
                    if response.status == 200:
                        logo_bytes = await response.read()
                        await update.message.reply_photo(
                            photo=InputFile(logo_bytes, filename="jellyfin_logo.png"),
                            caption=welcome_message
                        )
                        return
        except Exception as e:
            pass  # Si hay algún error, continuamos con el mensaje de texto
    
    await update.message.reply_text(welcome_message)

async def crear_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Por favor, proporciona el nombre del nuevo usuario.')
    return ESPERANDO_NOMBRE_USUARIO

async def nombre_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    token = authenticate()
    
    if not token:
        await update.message.reply_text('No se pudo autenticar con Jellyfin. Inténtalo de nuevo más tarde.')
        return ConversationHandler.END

    user_id = make_user(username, token)
    
    if user_id:
        password = make_password()
        if set_user_password(user_id, password, token) and update_user_policy(user_id, token):
            await update.message.reply_text(f'Usuario "{username}" creado y configurado correctamente. Contraseña: {password}')
        else:
            await update.message.reply_text(f'Usuario "{username}" creado, pero hubo un error al configurar la contraseña o la política.')
    else:
        await update.message.reply_text(f'No se pudo crear el usuario "{username}".')
    
    return ConversationHandler.END

async def password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Por favor, proporciona el nombre del usuario para cambiar la contraseña.')
    return ESPERANDO_USUARIO_PASSWORD

async def usuario_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    token = authenticate()
    
    if not token:
        await update.message.reply_text('No se pudo autenticar con Jellyfin. Inténtalo de nuevo más tarde.')
        return ConversationHandler.END
    
    user_id = get_user_id(username, token)
    
    if user_id:
        await update.message.reply_text('Por favor, proporciona la nueva contraseña para el usuario.')
        context.user_data['user_id'] = user_id
        return ESPERANDO_NUEVA_PASSWORD
    else:
        await update.message.reply_text(f'No se encontró el usuario "{username}".')
        return ConversationHandler.END

async def nueva_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_password = update.message.text
    user_id = context.user_data.get('user_id')
    token = authenticate()
    
    if not token:
        await update.message.reply_text('No se pudo autenticar con Jellyfin. Inténtalo de nuevo más tarde.')
        return ConversationHandler.END
    
    if set_user_password(user_id, new_password, token):
        await update.message.reply_text('La contraseña se ha cambiado correctamente.')
    else:
        await update.message.reply_text('Error al cambiar la contraseña.')
    
    return ConversationHandler.END

async def borrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Por favor, proporciona el nombre del usuario a eliminar.')
    return ESPERANDO_USUARIO_BORRAR

async def usuario_borrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    token = authenticate()
    
    if not token:
        await update.message.reply_text('No se pudo autenticar con Jellyfin. Inténtalo de nuevo más tarde.')
        return ConversationHandler.END
    
    user_id = get_user_id(username, token)
    
    if user_id:
        await update.message.reply_text(f'¿Estás seguro de que deseas eliminar el usuario "{username}"? (sí/no)')
        context.user_data['user_id'] = user_id
        return ESPERANDO_CONFIRMACION_BORRAR
    else:
        await update.message.reply_text(f'No se encontró el usuario "{username}".')
        return ConversationHandler.END

async def confirmacion_borrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    confirmation = update.message.text.lower()
    user_id = context.user_data.get('user_id')
    token = authenticate()
    
    if not token:
        await update.message.reply_text('No se pudo autenticar con Jellyfin. Inténtalo de nuevo más tarde.')
        return ConversationHandler.END
    
    if confirmation == 'sí':
        headers = {'X-Emby-Token': token}
        try:
            res = requests.delete(f'{JELLYFIN_URL}/Users/{user_id}', headers=headers)
            res.raise_for_status()
            await update.message.reply_text('El usuario ha sido eliminado correctamente.')
        except Exception as e:
            await update.message.reply_text('Error al eliminar el usuario.')
    else:
        await update.message.reply_text('El proceso de eliminación ha sido cancelado.')
    
    return ConversationHandler.END

def main() -> None:
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('crear_usuario', crear_usuario),
                      CommandHandler('password', password),
                      CommandHandler('borrar', borrar)],
        states={
            ESPERANDO_NOMBRE_USUARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, nombre_usuario)],
            ESPERANDO_USUARIO_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, usuario_password)],
            ESPERANDO_NUEVA_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, nueva_password)],
            ESPERANDO_USUARIO_BORRAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, usuario_borrar)],
            ESPERANDO_CONFIRMACION_BORRAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmacion_borrar)],
        },
        fallbacks=[CommandHandler('cancelar', lambda update, context: update.message.reply_text('Operación cancelada.'))]
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('start', start))

    application.run_polling()

if __name__ == '__main__':
    main()