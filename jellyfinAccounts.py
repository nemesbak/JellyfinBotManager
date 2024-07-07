import os
import requests
import random
import string
import socket
import json
import aiohttp
import logging
from telegram import Update, InputFile, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes, ConversationHandler, MessageHandler, filters, CallbackQueryHandler

# Configurar logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de Jellyfin
JELLYFIN_URL = 'url servidor'
JELLYFIN_API_KEY = 'api de jellyfin'
JELLYFIN_ADMIN_USERNAME = 'usuario admin'
JELLYFIN_ADMIN_PASSWORD = 'contraseña del admin'
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

# Credenciales de Telegram Bot
TELEGRAM_TOKEN = 'token del bot aqui'

# URL de la imagen del logo de Jellyfin
JELLYFIN_LOGO_URL = "url de imagen si quieres para cuando de la bienvenida y el saluda inicial"

# Estados para la conversación
ESPERANDO_NOMBRE_USUARIO = 1
ESPERANDO_USUARIO_MODIFICAR = 2
ESPERANDO_PARAMETRO_MODIFICAR = 3
ESPERANDO_USUARIO_PASSWORD = 4
ESPERANDO_NUEVA_PASSWORD = 5
ESPERANDO_USUARIO_BORRAR = 6
ESPERANDO_SELECCION_ESTADO = 7
ESPERANDO_ACTIVAR_DESACTIVAR = 8
ESPERANDO_CONFIRMACION_BORRAR = 9

# Funciones auxiliares
def make_password(length):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

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
        logger.error(f'Error al autenticar en Jellyfin: {e}')
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
        logger.error(f'Error al crear usuario en Jellyfin: {e}')
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
        logger.error(f'Error al establecer la contraseña del usuario en Jellyfin: {e}')
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
        logger.error(f'Error al actualizar la política del usuario en Jellyfin: {e}')
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
        logger.error(f'Error al obtener el ID del usuario: {e}')
        return None

def get_user_policy(user_id, token):
    headers = {'X-Emby-Token': token}
    try:
        res = requests.get(f'{JELLYFIN_URL}/Users/{user_id}', headers=headers)
        res.raise_for_status()
        user_info = res.json()
        
        if 'Policy' in user_info:
            return user_info['Policy']
        else:
            logger.error(f'No se encontró la política en la información del usuario: {user_info}')
            return None
    except Exception as e:
        logger.error(f'Error al obtener la información del usuario: {e}')
        return None

def update_user_parameter(user_id, parameter, value, token):
    headers = {
        'X-Emby-Token': token,
        'Content-Type': 'application/json'
    }
    try:
        # Primero, obtener la política completa del usuario
        res = requests.get(f'{JELLYFIN_URL}/Users/{user_id}/Policy', headers=headers)
        res.raise_for_status()
        user_policy = res.json()
        
        # Modificar el parámetro específico
        user_policy[parameter] = value
        
        # Enviar la política completa actualizada
        res = requests.post(f'{JELLYFIN_URL}/Users/{user_id}/Policy', headers=headers, json=user_policy)
        res.raise_for_status()
        
        # Verificar si el cambio se aplicó correctamente
        res = requests.get(f'{JELLYFIN_URL}/Users/{user_id}/Policy', headers=headers)
        res.raise_for_status()
        updated_policy = res.json()
        
        if updated_policy.get(parameter) == value:
            logger.info(f'Parámetro {parameter} actualizado correctamente a {value}')
            return True
        else:
            logger.error(f'El parámetro {parameter} no se actualizó correctamente. Valor actual: {updated_policy.get(parameter)}')
            return False
    except Exception as e:
        logger.error(f'Error al actualizar el parámetro del usuario: {e}')
        return False

def get_all_users(token):
    headers = {'X-Emby-Token': token}
    try:
        res = requests.get(f'{JELLYFIN_URL}/Users', headers=headers)
        res.raise_for_status()
        return res.json()
    except Exception as e:
        logger.error(f'Error al obtener la lista de usuarios: {e}')
        return None

# Funciones del bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    welcome_message = (
        "¡Bienvenido al Bot de Gestión de Usuarios de Jellyfin! 🎉\n\n"
        "Este bot te ayudará a gestionar las cuentas de usuario en nuestro servidor Jellyfin.\n\n"
        "Comandos disponibles:\n"
        "/crear_usuario - Crear un nuevo usuario\n"
        "/modificar - Modificar parámetros de un usuario existente\n"
        "/password - Cambiar la contraseña de un usuario\n"
        "/borrar - Eliminar un usuario existente\n"
        "/estado - Ver el estado de los usuarios"
    )
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(JELLYFIN_LOGO_URL) as response:
                if response.status == 200:
                    logo_bytes = await response.read()
                    await update.message.reply_photo(
                        photo=InputFile(logo_bytes, filename="jellyfin_logo.png"),
                        caption=welcome_message
                    )
                else:
                    await update.message.reply_text(welcome_message)
    except Exception as e:
        logger.error(f"Error al obtener la imagen del logo: {e}")
        await update.message.reply_text(welcome_message)

async def crear_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Por favor, proporciona un nombre de usuario para crear en Jellyfin. 🆕\n'
        'El nombre debe ser único y fácil de recordar.'
    )
    return ESPERANDO_NOMBRE_USUARIO

async def procesar_nombre_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    token = authenticate()
    if not token:
        await update.message.reply_text(
            '❌ Error al autenticar en Jellyfin.\nPor favor, intenta más tarde o contacta al administrador.'
        )
        return ConversationHandler.END

    user_id = make_user(username, token)
    if not user_id:
        await update.message.reply_text(
            '❌ Error al crear el usuario en Jellyfin.\nPor favor, intenta más tarde o contacta al administrador.'
        )
        return ConversationHandler.END

    password = make_password(12)
    if not set_user_password(user_id, password, token):
        await update.message.reply_text(
            '❌ Error al establecer la contraseña del usuario.\nPor favor, contacta al administrador.'
        )
        return ConversationHandler.END

    if not update_user_policy(user_id, token):
        await update.message.reply_text(
            '⚠️ Advertencia: No se pudo actualizar la política del usuario.'
        )

    mensaje = f"""
🎉 ¡Cuenta creada exitosamente! 🎉

📺 Servidor: {JELLYFIN_URL}
👤 Usuario: {username}
🔑 Contraseña: {password}

🔐 Por favor, cambia tu contraseña después del primer inicio de sesión.

📞 En caso de problemas con la cuenta, contacta con el administrador.

¡Disfruta de tu nueva cuenta de Jellyfin! 🍿🎬
"""
    await update.message.reply_text(mensaje)
    return ConversationHandler.END

async def modificar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Por favor, proporciona el nombre de usuario que deseas modificar. 🔧\n'
        'O escribe "cancelar" para terminar el proceso.'
    )
    return ESPERANDO_USUARIO_MODIFICAR

async def procesar_usuario_modificar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    if username.lower() == "cancelar":
        await update.message.reply_text("Proceso cancelado.")
        return ConversationHandler.END
    
    token = authenticate()
    if not token:
        await update.message.reply_text('Error al autenticar en Jellyfin.')
        return ConversationHandler.END
    
    user_id = get_user_id(username, token)
    if not user_id:
        await update.message.reply_text('Usuario no encontrado.')
        return ConversationHandler.END
    
    logger.info(f'Obteniendo política para el usuario: {username}, ID: {user_id}')
    parametros = get_user_policy(user_id, token)
    if not parametros:
        await update.message.reply_text('Error al obtener la política del usuario. Por favor, verifica los logs para más detalles.')
        return ConversationHandler.END
    
    context.user_data['usuario_modificar'] = username
    context.user_data['parametros'] = parametros
    
    mensaje = f"Parámetros actuales para el usuario {username}:\n"
    for key, value in parametros.items():
        if isinstance(value, bool):
            mensaje += f"{key}: {value}\n"
    mensaje += "\nEscribe el nombre del parámetro que deseas modificar o 'cancelar' para terminar:"
    
    await update.message.reply_text(mensaje)
    return ESPERANDO_PARAMETRO_MODIFICAR

async def procesar_parametro_modificar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    parametro = update.message.text
    if parametro.lower() == "cancelar":
        await update.message.reply_text("Proceso cancelado.")
        return ConversationHandler.END
    
    if parametro not in context.user_data['parametros'] or not isinstance(context.user_data['parametros'][parametro], bool):
        await update.message.reply_text("Parámetro no válido. Por favor, intenta de nuevo o escribe 'cancelar'.")
        return ESPERANDO_PARAMETRO_MODIFICAR
    
    
    valor_actual = context.user_data['parametros'][parametro]
    nuevo_valor = not valor_actual
    
    token = authenticate()
    if not token:
        await update.message.reply_text('Error al autenticar en Jellyfin.')
        return ConversationHandler.END
    
    user_id = get_user_id(context.user_data['usuario_modificar'], token)
    if not user_id:
        await update.message.reply_text('Usuario no encontrado.')
        return ConversationHandler.END
    
    if update_user_parameter(user_id, parametro, nuevo_valor, token):
        context.user_data['parametros'][parametro] = nuevo_valor
        await update.message.reply_text(f"Parámetro {parametro} actualizado correctamente de {valor_actual} a {nuevo_valor}")
    else:
        await update.message.reply_text(f"Error al actualizar el parámetro {parametro}. El valor no ha cambiado.")
    
    # Verificar el estado actual del parámetro
    parametros_actualizados = get_user_policy(user_id, token)
    if parametros_actualizados:
        valor_actual = parametros_actualizados.get(parametro)
        await update.message.reply_text(f"Estado actual del parámetro {parametro}: {valor_actual}")
    else:
        await update.message.reply_text("No se pudo verificar el estado actual del parámetro.")
    
    return ConversationHandler.END

async def cambiar_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Por favor, proporciona el nombre de usuario cuya contraseña deseas cambiar. 🔑'
    )
    return ESPERANDO_USUARIO_PASSWORD

async def procesar_usuario_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    context.user_data['usuario_password'] = username
    await update.message.reply_text(
        'Ahora, proporciona la nueva contraseña para este usuario. 🔐'
    )
    return ESPERANDO_NUEVA_PASSWORD

async def procesar_nueva_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    new_password = update.message.text
    username = context.user_data['usuario_password']
    
    token = authenticate()
    if not token:
        await update.message.reply_text('Error al autenticar en Jellyfin.')
        return ConversationHandler.END
    
    user_id = get_user_id(username, token)
    if not user_id:
        await update.message.reply_text('Usuario no encontrado.')
        return ConversationHandler.END
    
    if set_user_password(user_id, new_password, token):
        await update.message.reply_text(f'Contraseña cambiada exitosamente para el usuario {username}. ✅')
    else:
        await update.message.reply_text(f'Error al cambiar la contraseña para el usuario {username}.')
    
    return ConversationHandler.END

async def borrar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        'Por favor, proporciona el nombre de usuario que deseas eliminar. 🗑️'
    )
    return ESPERANDO_USUARIO_BORRAR

async def confirmar_borrar_usuario(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = update.message.text
    context.user_data['usuario_a_borrar'] = username
    await update.message.reply_text(
        f'¿Estás seguro de que quieres eliminar al usuario {username}?\n'
        'Responde "SI" para confirmar o cualquier otra cosa para cancelar.'
    )
    return ESPERANDO_CONFIRMACION_BORRAR

async def procesar_confirmacion_borrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.text.upper() == "SI":
        return await procesar_usuario_borrar(update, context)
    else:
        await update.message.reply_text('Operación cancelada.')
        return ConversationHandler.END

async def procesar_usuario_borrar(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = context.user_data['usuario_a_borrar']
    
    token = authenticate()
    if not token:
        await update.message.reply_text('Error al autenticar en Jellyfin.')
        return ConversationHandler.END
    
    user_id = get_user_id(username, token)
    if not user_id:
        await update.message.reply_text('Usuario no encontrado.')
        return ConversationHandler.END
    
    headers = {'X-Emby-Token': token}
    try:
        logger.info(f'Intentando eliminar usuario: {username}, ID: {user_id}')
        res = requests.delete(f'{JELLYFIN_URL}/Users/{user_id}', headers=headers)
        res.raise_for_status()
        logger.info(f'Respuesta del servidor: {res.status_code} - {res.text}')
        await update.message.reply_text(f'Usuario {username} eliminado exitosamente. ✅')
    except requests.exceptions.RequestException as e:
        logger.error(f'Error al eliminar el usuario: {e}')
        logger.error(f'URL: {JELLYFIN_URL}/Users/{user_id}')
        logger.error(f'Headers: {headers}')
        logger.error(f'Respuesta: {res.text if "res" in locals() else "No response"}')
        await update.message.reply_text(f'Error al eliminar el usuario {username}. Por favor, verifica los logs para más detalles.')
    
    return ConversationHandler.END

async def estado(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    token = authenticate()
    if not token:
        await update.message.reply_text('Error al autenticar en Jellyfin.')
        return ConversationHandler.END
    
    users = get_all_users(token)
    if not users:
        await update.message.reply_text('Error al obtener la lista de usuarios.')
        return ConversationHandler.END
    
    mensaje = "🗝️ Usuarios:\n"
    for user in users:
        mensaje += f"[{user['Name']}](tg://user?id={user['Id']})\n"
    
    keyboard = [
        [InlineKeyboardButton("Activar/Desactivar", callback_data='activar_desactivar')],
        [InlineKeyboardButton("Cambiar ajustes", callback_data='cambiar_ajustes')],
        [InlineKeyboardButton("Cambiar contraseña", callback_data='cambiar_contraseña')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(mensaje, reply_markup=reply_markup, parse_mode='MarkdownV2')
    return ESPERANDO_SELECCION_ESTADO

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    
    if query.data == 'activar_desactivar':
        keyboard = [
            [InlineKeyboardButton("Activar", callback_data='activar')],
            [InlineKeyboardButton("Desactivar", callback_data='desactivar')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("Selecciona una opción:", reply_markup=reply_markup)
        return ESPERANDO_ACTIVAR_DESACTIVAR
    elif query.data == 'cambiar_ajustes':
        await query.edit_message_text("Por favor, usa el comando /modificar para cambiar ajustes específicos.")
        return ConversationHandler.END
    elif query.data == 'cambiar_contraseña':
        await query.edit_message_text("Por favor, usa el comando /password para cambiar la contraseña de un usuario.")
        return ConversationHandler.END
    elif query.data in ['activar', 'desactivar']:
        # Implementar la lógica para activar o desactivar usuarios
        await query.edit_message_text(f"Has seleccionado {query.data} usuarios. Esta función aún no está implementada.")
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Operación cancelada. ❌\nPuedes iniciar una nueva acción cuando lo desees.'
    )
    return ConversationHandler.END

def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(f"Exception while handling an update: {context.error}")

def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('crear_usuario', crear_usuario),
            CommandHandler('modificar', modificar),
            CommandHandler('password', cambiar_password),
            CommandHandler('borrar', borrar_usuario),
            CommandHandler('estado', estado)
        ],
        states={
            ESPERANDO_NOMBRE_USUARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_nombre_usuario)],
            ESPERANDO_USUARIO_MODIFICAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_usuario_modificar)],
            ESPERANDO_PARAMETRO_MODIFICAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_parametro_modificar)],
            ESPERANDO_USUARIO_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_usuario_password)],
            ESPERANDO_NUEVA_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_nueva_password)],
            ESPERANDO_USUARIO_BORRAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, confirmar_borrar_usuario)],
            ESPERANDO_CONFIRMACION_BORRAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, procesar_confirmacion_borrar)],
            ESPERANDO_SELECCION_ESTADO: [CallbackQueryHandler(button_callback)],
            ESPERANDO_ACTIVAR_DESACTIVAR: [CallbackQueryHandler(button_callback)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(conv_handler)
    application.add_error_handler(error_handler)

    logger.info("Bot iniciado y en ejecución...")
    print("Bot de Jellyfin iniciado y en ejecución. Presiona Ctrl+C para detener.")
    application.run_polling()

if __name__ == '__main__':
    main()