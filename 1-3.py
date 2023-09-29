#!/usr/bin/python3

import sys
import os

with open('/etc/passwd', 'r') as passwd_file:
    lines = passwd_file.readlines()

for line in lines:
    fields = line.split(':')
    usr = fields[0]
    uid = int(fields[2])
    directorio = fields[5].strip()

    if uid > 1000:

        if os.path.exists(directorio) and os.path.isdir(directorio):
            print(f" \ Usuario: {usr}, UID: {uid}, Carpeta personal: {directorio} (Es un directorio y existe)")
        else:
            print(f" \ Usuario: {usr}, UID: {uid}, Carpeta personal: {directorio} (No existe o no es un directorio)")

sys.exit(0)
