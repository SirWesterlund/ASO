#!/usr/bin/python3

import sys
import os
import getpass

id = os.getuid()
usr = getpass.getuser()
ps1 = os.environ.get("PS1")
carpeta_personal = os.path.expanduser("~")

if id == 1000 or id < 1000:
	print(" Eres usuario especial. No puedes ejecutar este script. Tu ID es: "+str(id))
	sys.exit(1)
else:
	print(" Eres un usuario estandar. Tu ID es: "+str(id))
	print(" Tu nombre es: "+str(usr))

with open('/etc/passwd', 'r') as passwd_file:
    username = usr
    for line in passwd_file:
        fields = line.strip().split(':')
        if fields[0] == username:
            gecos = fields[4]
            print(f" El campo GECOS para el usuario {username} es: {gecos}")
            break
    else:
        print(f" No se encontró el usuario {usr} en /etc/passwd")
        print(" Tu carpeta personal es: "+str(carpeta_personal))

if ps1 == None:
        print(" La variable PS1 no existe ")

