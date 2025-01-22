"""
Ce script configure la connexion à la base de données du blog.

Il se connecte à la base de données MySQL 'meth6045_db_tititechnique' en utilisant les paramètres spécifiés
(user, password, host, port, database). Ensuite, il crée un curseur pour effectuer des opérations sur la base de données.
Finalement, il affiche la version de la base de données MySQL.

Exemple d'utilisation :
    python db_tititechnique.py
"""

import pymysql

# Paramètres de la base de données
db_config = {
    "user": "meth6045_Nono",
    "password": "bloggeminips626",
    "host": "grebe.o2switch.net",
    "port": 3306,
    "database": "meth6045_db_tititechnique",
    "charset": "utf8mb4"
}

try:
    # Établir la connexion à la base de données
    with pymysql.connect(**db_config) as conn:
        # Création du curseur
        with conn.cursor() as cur:
            # Afficher la version de MySQL
            cur.execute("SELECT VERSION();")  # La requête SQL pour obtenir la version
            version = cur.fetchone()
            print("Version de MySQL :", version[0], "\n")  # Affichage plus lisible

except pymysql.MySQLError as e:
    print(f"Erreur lors de la connexion à la base de données: {e}")

except Exception as e:
    print(f"Une erreur s'est produite: {e}")


