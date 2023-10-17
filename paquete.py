#!/usr/bin/python3

import os
import sys
import subprocess
import requests

if os.geteuid() != 0:
    print("* Tienes que ser root para ejecutar este script.")
    sys.exit(1)

paquete = "itaca"

try:
    subprocess.check_output(["dpkg", "-l", paquete])
    print("* El paquete " + str(paquete) + " está instalado.")
    opcion = input("(!) Desea continuar (y/n) ")

    if opcion.lower() == "n":
        print("* Saliendo...")
    else:
        print("Hola, " + opcion + "! Bienvenido a Python.")

except subprocess.CalledProcessError:
    print("* El paquete " + str(paquete) + " no está instalado.")
    opcion = input("(!) Desea continuar (y/n) ")

    if opcion.lower() == "n":
        print("* Saliendo...")
    else:
	print("* Instalando el paquete...")
	response = requests.get(url)

    if response.status_code == 200:
    with open(nombre_archivo_local, 'wb') as archivo_local:
        archivo_local.write(response.content)
    print(f"El archivo {nombre_archivo_local} se ha descargado correctamente.")
    else:
    print(f"No se pudo descargar el archivo. Código de estado: {response.status_code}")

sys.exit(0)

