#!/usr/bin/python3

import sys
import os
import subprocess
import urllib.request
from termcolor import colored, cprint

def imprimir_mensaje(mensaje, color):
    cprint(mensaje, color)

def verificar_superuser():
    id_usuario = os.getuid()
    if id_usuario == 0:
        imprimir_mensaje('-Eres un superusuario válido\n', 'green')
    else:
        imprimir_mensaje('[ERROR] - Debes ser un superusuario. Saliendo...\n', 'red')
        sys.exit(1)

def instalar_paquete(nombre_paquete, url_paquete, ruta_paquete, comando_instalacion, comando_desinstalacion):
    imprimir_mensaje(f'*Bienvenido al Instalador de {nombre_paquete}\n', 'blue')

    verificar_superuser()

    paquetes_instalados = subprocess.check_output(["dpkg", "-l"], text=True)

    if nombre_paquete in paquetes_instalados:
        imprimir_mensaje('-El paquete ya está instalado\n', 'green')
        print('--¿Quieres reinstalarlo? [s/n]')
        respuesta = input()

        if respuesta.lower() in ('s', 'si'):
            subprocess.run(comando_desinstalacion, shell=True, check=True)
            if os.path.exists(ruta_paquete):
                os.remove(ruta_paquete)

            urllib.request.urlretrieve(url_paquete, ruta_paquete)
            subprocess.run(comando_instalacion, shell=True)
        else:
            print('¡Adiós! :)')
            sys.exit(0)
    else:
        imprimir_mensaje('-El paquete no está instalado\n', 'red')
        print('--¿Quieres instalarlo? [s/n]')
        respuesta = input()

        if respuesta.lower() in ('s', 'si'):
            urllib.request.urlretrieve(url_paquete, ruta_paquete)
            subprocess.run(comando_instalacion, shell=True)
        else:
            print('¡Adiós! :)')
            sys.exit(0)

if __name__ == "__main__":
    nombre_programa = 'itaca'
    url_paquete = 'http://lliurex.net/focal/pool/main/i/itaca/itaca_1.0.8_amd64.deb'
    ruta_paquete = '/home/dd/Descargas/itaca_1.0.8_amd64.deb'
    comando_instalacion = "sudo dpkg -i " + ruta_paquete
    comando_desinstalacion = "sudo dpkg -P " + nombre_programa

    instalar_paquete(nombre_programa, url_paquete, ruta_paquete, comando_instalacion, comando_desinstalacion)

    sys.exit(0)

