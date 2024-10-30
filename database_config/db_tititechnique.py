"""Ce script configure la connexion à la base de données du blog.

Il se connecte à la base de données PostgreSQL 'meth6045_db_tititechnique' en utilisant les paramètres spécifiés
(user, password, host, port, database). Ensuite, il crée un curseur pour effectuer des opérations sur la base de données.
Finalement, il affiche la version de la base de données PostgreSQL.

Exemple d'utilisation :
    python db_tititechnique.py
"""

import psycopg2

# Paramètres de la base de données db_tititechnique.

conn = psycopg2.connect(
    user="postgres",
    password="bloggeminips626",
    host="localhost",
    port="5432",
    database="meth6045_db_tititechnique"
    )

# Création du curseur pour pouvoir faire agir sur la database

cur = conn.cursor()


# Afficher la version de la base de PostgreSQL

cur.execute("SELECT version();")
version = cur.fetchone()
print("Version : ", version, "\n")

