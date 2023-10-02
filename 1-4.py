#!/usr/bin/python3

import sys
import netifaces

lista_interfaces = netifaces.interfaces()

for inter in lista_interfaces:
	print(" Nombre de la Interfaz: " + inter + " ")
	print(" Direccion IP: " + netifaces.ifaddresses(inter)[2][0]['addr'])
	print(" ")

sys.exit(0)
