#!/usr/bin/python3

import sys
import os
import re
from termcolor import colored, cprint

# Some useful values
DATE_FORMAT = "\'YYYY-MM-DD\'"
THIS_VERSION = "20231006-v5"

# Some sanity checks

cprint(" * Script version " + THIS_VERSION, 'green')

if len(sys.argv) < 4:
    cprint(" USAGE : oraclize.py ORIG.sql DEST.sql TABLESPACE", 'red', attrs=['underline'])
    sys.exit(1)

orig = open(sys.argv[1], 'r')
if os.path.exists(sys.argv[2]):
    cprint(" * Old file present...removing it!", 'green')
    os.remove(sys.argv[2])

destinosql = open(sys.argv[2], 'x')

elultimoinsertbueno = ""
alter_columns = []
alter_table_name = None

for line in orig:
    auxp = line

    # Tipos de datos
    if auxp.startswith(") ENGINE"):
        auxp = ") TABLESPACE " + sys.argv[3] + ";\n"

    if "VARCHAR" in auxp:
        auxp = auxp.replace("VARCHAR", "VARCHAR2")

    if "varchar" in auxp:
        auxp = auxp.replace("varchar", "VARCHAR2")

    if "FLOAT" in auxp:
        auxp = auxp.replace("FLOAT", "NUMBER")

    if "float" in auxp:
        auxp = auxp.replace("float", "NUMBER")

    if " INT " in auxp:
        auxp = auxp.replace(" INT ", " NUMBER ")

    if " int(" in auxp:
        auxp = auxp.replace(" int(", " NUMBER(")

    if auxp.startswith("INSERT INTO") and auxp.endswith("VALUES\n"):
        # Me la guardo
        elultimoinsertbueno = auxp
        auxp = ""

    if auxp.endswith(",\n") and auxp.startswith("("):
        auxp = auxp.replace(",\n", ";\n")
        if "`" in auxp:
            auxp = auxp.replace("`", "'")

    if auxp.startswith("("):
        pattern = "\d{4}-\d{2}-\d{2}"
        fechasencontradas = re.findall(pattern, auxp)
        if len(fechasencontradas) > 0:
            for fecha in fechasencontradas:
                auxp = auxp.replace('\'' + fecha + '\'', f'TO_DATE(\'{fecha}\',' + DATE_FORMAT + ')')
        auxp = elultimoinsertbueno.strip() + auxp

    # THE MOTHER OF THE LAMB
    auxp = auxp.replace("`", "")

    destinosql.write(auxp)

    if auxp.startswith("CREATE TABLE"):
        alter_columns = []
        alter_table_name = re.search(r'CREATE TABLE (\S+)', auxp).group(1)
    
    if auxp.strip().endswith(",") and alter_table_name:
        if "PRIMARY KEY" in auxp:
            primary_key_sql = f"ALTER TABLE {alter_table_name}\n"
            primary_key_sql += f"  ADD PRIMARY KEY ({auxp.split('(')[1].strip().rstrip(',')});\n"
            destinosql.write(primary_key_sql)
        elif "UNIQUE KEY" in auxp:
            unique_key_sql = f"ALTER TABLE {alter_table_name}\n"
            unique_key_sql += f"  ADD UNIQUE ({auxp.split('(')[1].strip().rstrip(',')});\n"
            destinosql.write(unique_key_sql)
        elif "KEY" in auxp:
            key_name = re.search(r'KEY (\S+)', auxp).group(1)
            key_sql = f"ALTER TABLE {alter_table_name}\n"
            key_sql += f"  ADD CONSTRAINT {key_name} FOREIGN KEY ({auxp.split('(')[1].strip().rstrip(',')});\n"
            destinosql.write(key_sql)

    if auxp.startswith(")") and alter_columns:
        alter_sql = f"ALTER TABLE {alter_table_name}\n"
        alter_sql += "  ADD (\n"
        for column in alter_columns:
            alter_sql += f"    {column},\n"
        alter_sql = alter_sql.rstrip(",\n")  # Remove trailing comma and newline
        alter_sql += "\n  );"
        destinosql.write(alter_sql + "\n")
        alter_columns = []
        alter_table_name = None

destinosql.close()
sys.exit(0)


