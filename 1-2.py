#!/usr/bin/python3

import sys

shells_with_bin_bash = []

print(" ")
print(" Recorramos el fichero /etc/passwd")
print(" ")

with open("/etc/passwd", 'r') as passwd:
    for linea in passwd:
        arrayLinea = linea.split(':')
        uid = int(arrayLinea[2])
        shell = arrayLinea[6].strip()

        if shell == "/bin/bash":
            shells_with_bin_bash.append(arrayLinea[0])
            print("* login: " + arrayLinea[0] + " ----> " + str(uid) + " " + shell + " Tiene login")

        else:
            print("* login: " + arrayLinea[0] + " ----> " + str(uid) + " " + shell + " No tiene login")

print(" ")
print(" Recorramos el fichero /etc/shadow")
print(" ")

with open("/etc/shadow", 'r') as shadow:
    for linea in shadow:
        arrayLinea = linea.split(':')
        nombre = arrayLinea[0]
        password_hash = arrayLinea[1].strip()

        if password_hash not in ("*", "!"):
            print(" * nombre: " + nombre + " " + password_hash + " " + " ----> Tiene contraseña encriptada")
        else:
            print(" * nombre: " + nombre + " " + password_hash + " " + " ----> No tiene contraseña")

sys.exit(0)

