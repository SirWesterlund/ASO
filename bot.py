#!/usr/bin/python3
# pylint: disable=unused-argument
# This program is dedicated to the public domain under the CC0 license.

"""
Simple Bot to reply to Telegram messages.

First, a few handler functions are defined. Then, those functions are passed to
the Application and registered at their respective places.
Then, the bot is started and runs until we press Ctrl-C on the command line.

Usage:
Basic Echobot example, repeats messages.
Press Ctrl-C on the command line or send a signal to the process to stop the
bot.
"""

import subprocess
import platform
import socket
import logging
import psutil
import nmap

from telegram import ForceReply, Update, Bot
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters, CallbackContext

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)


# Define a few command handlers. These usually take the two arguments update and
# context.
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /start is issued."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Hola {user.mention_html()}!",
        reply_markup=ForceReply(selective=True),
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text("Help!")


async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    await update.message.reply_text(update.message.text)


async def info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send information about the bot when the command /info is issued."""
    bot = context.bot
    bot_info = f"Nombre del Bot: {bot.name}\nNombre de Usuario: {bot.username}\nID de Usuario: {bot.id}"
    await update.message.reply_text(bot_info)

async def host_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send information about the host system when the command /host is issued."""
    os_info = platform.platform()
    await update.message.reply_text(f"Sistema Operativo: {os_info}")

async def net_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the IP address(es) of the host system when the command /net is issued."""
    try:
        host_name = socket.gethostname()
        ip_address = socket.gethostbyname(host_name)
        await update.message.reply_text(f"Nombre del Host: {host_name}\nDirección IP: {ip_address}")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a ping request to the specified IP when the command /ping is issued."""
    try:
        ip_to_ping = context.args[0]

        result = subprocess.run(['ping', '-c', '4', ip_to_ping], text=True, capture_output=True)

        if result.returncode == 0:
            response = f"Ping a la {ip_to_ping} ha sido un éxito.\n{result.stdout}"
        else:
            response = f"Ping a la {ip_to_ping} ha fallado.\n{result.stderr}"

        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

def get_recent_errors(num_errors):
    try:
        result = subprocess.run(['tail', f'-n{num_errors}', '/var/log/syslog'], capture_output=True, text=True, check=True)
        log_content = result.stdout
        errors = [line for line in log_content.split('\n') if 'error' in line.lower()]
        return "\n".join(errors)
    except subprocess.CalledProcessError:
        return "No se pudo leer el archivo de registro."

async def errorlog(update: Update, context: CallbackContext):
    num_errors = context.args[0] if context.args else '10'
    num_errors = int(num_errors)
    errors = get_recent_errors(num_errors)
    if errors:
        await update.message.reply_text(errors)
    else:
        await update.message.reply_text("No se encontraron errores en el registro.")


def is_service_running(service_name):
    try:
        result = subprocess.run(['service', service_name, 'status'], capture_output=True, text=True, check=True)
        return "Active: active (running)" in result.stdout
    except subprocess.CalledProcessError:
        return False


async def servicestatus(update, context):
    if context.args:
        service_name = context.args[0]

        try:
            result = subprocess.run(['service', service_name, 'status'], capture_output=True, text=True, check=True)
            status = result.stdout
            response = f"El servicio {service_name} existe en el sistema y su estado es:\n{status}"
        except subprocess.CalledProcessError:
            response = f"El servicio {service_name} no existe en el sistema o está detenido."

    else:
        await update.message.reply_text("Por favor, proporciona el nombre del servicio como argumento, por ejemplo: /servicestatus NOMBRE_DEL_SERVICIO")
        return

    await update.message.reply_text(response)


async def servicestart(update, context):
    if context.args:
        service_name = context.args[0]
        if not is_service_running(service_name):
            try:
                subprocess.run(['sudo', 'service', service_name, 'start'], capture_output=True, text=True, check=True)
                response = f"El servicio {service_name} se inició exitosamente."
            except subprocess.CalledProcessError as e:
                response = f"Error al iniciar el servicio {service_name}: {e.stderr}"
        else:
            response = f"El servicio {service_name} ya está en ejecución."
    else:
        await update.message.reply_text("Por favor, proporciona el nombre del servicio como argumento, por ejemplo: /servicestart NOMBRE_DEL_SERVICIO")
    await update.message.reply_text(response)


async def servicestop(update, context):
    if context.args:
        service_name = context.args[0]

        try:
            result = subprocess.run(['service', service_name, 'status'], capture_output=True, text=True, check=True)
        except subprocess.CalledProcessError:
            exists = False
        else:
            exists = True

        if exists:
            try:
                subprocess.run(['sudo', 'service', service_name, 'stop'], capture_output=True, text=True, check=True)
                response = f"El servicio {service_name} se detuvo exitosamente."
                
                try:
                    result = subprocess.run(['service', service_name, 'status'], capture_output=True, text=True, check=True)
                    status = result.stdout
                    response += f"\nEstado actual del servicio {service_name}:\n{status}"
                except subprocess.CalledProcessError:
                    response += f"\nNo se pudo obtener el estado actual del servicio {service_name}."
            except subprocess.CalledProcessError as e:
                response = f"Error al detener el servicio {service_name}: {e.stderr}"
        else:
            response = f"El servicio {service_name} no está en ejecución o no existe."
    else:
        await update.message.reply_text("Por favor, proporciona el nombre del servicio como argumento, por ejemplo: /servicestop NOMBRE_DEL_SERVICIO")
        return

    await update.message.reply_text(response)


async def nmap_scan(update: Update, context: CallbackContext):
    if not context.args:
        await update.message.reply_text("Por favor, proporciona la dirección de red como argumento, por ejemplo: /nmap 192.168.1.0/24")
        return

    network = context.args[0]

    try:
        nm = nmap.PortScanner()
        nm.scan(hosts=network, arguments='-n -sP')

        host_list = nm.all_hosts()
        response = "Hosts accesibles en la red:\n"
        for host in host_list:
            try:
                host_name = socket.gethostbyaddr(host)[0]
            except socket.herror:
                host_name = "No se pudo determinar el nombre"

            response += f"{host} ({host_name})\n"

        await update.message.reply_text(response)
    except nmap.nmap.PortScannerError:
        await update.message.reply_text("Error al escanear la red.")
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")

async def ports_in_use(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a list of open ports and the processes using them when the command /ports-in-use is issued."""
    try:
        open_ports = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == psutil.CONN_ESTABLISHED:
                local_port = conn.laddr.port
                process = psutil.Process(conn.pid)
                process_name = process.name()
                open_ports.append(f"Port: {local_port}, Process: {process_name}")

        if open_ports:
            response = "Puertos en uso:\n" + "\n".join(open_ports)
        else:
            response = "No hay puertos en uso en este momento."

        await update.message.reply_text(response)
    except Exception as e:
        await update.message.reply_text(f"Error: {str(e)}")


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token("6433690901:AAEQ7jx_oZkNrFdEZlUu-_WVU4H533YvJ2o").build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("info", info))
    application.add_handler(CommandHandler("host", host_info))
    application.add_handler(CommandHandler("net", net_info))
    application.add_handler(CommandHandler("ping", ping))
    application.add_handler(CommandHandler("errorlog", errorlog))
    application.add_handler(CommandHandler("servicestatus", servicestatus))
    application.add_handler(CommandHandler("servicestart", servicestart))
    application.add_handler(CommandHandler("servicestop", servicestop))
    application.add_handler(CommandHandler("nmap", nmap_scan))
    application.add_handler(CommandHandler("ports", ports_in_use))

    # on non command i.e message - echo the message on Telegram
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
