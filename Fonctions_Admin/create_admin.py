"""Ce script crée un administrateur pour le blog.

Il utilise bcrypt pour hacher le mot de passe et stocker de manière sécurisée les identifiants de
l'administrateur dans la base de données.
Il faut s'assurer d'avoir configuré la connexion à la base de données correctement et
d'avoir les autorisations nécessaires pour insérer des données.

Exemple d'utilisation :
    python create_admin.py
"""
import sys
import os
import bcrypt
import pymysql

# Chemin absolu du répertoire courant
current_dir = os.path.abspath(os.path.dirname(__file__))

# Chemin absolu du répertoire parent
parent_dir = os.path.abspath(os.path.join(current_dir, os.pardir))

# Ajouter le répertoire parent au sys.path
sys.path.append(parent_dir)

# Importer la fonction conn() depuis db_tititechnique.py
from database_config.db_tititechnique import db_config


# Si vous voulez changer votre identifiant et votre mot de passe, c'est ici.
pseudo = "Tititechnique"
password = "bloggeminips626"
role = "Admin"

# Génération d'un sel aléatoire pour le hachage du mot de passe.
salt = bcrypt.gensalt()

# Hachage du mot de passe avec le sel généré.
password_hash = bcrypt.hashpw(password.encode("utf-8"), salt)

print("Le processus de hachage a bien fonctionné.")

# Établir la connexion à la base de données
try:
    conn = pymysql.connect(**db_config)  # Utilise la configuration importée

    # Sélection d'un curseur pour action sur la base de données.
    with conn.cursor() as cur:
        # Insertion de l'identifiant et du mot de passe hashé dans la base de données.
        cur.execute(
            "INSERT INTO admin (role, pseudo, password_hash, salt) VALUES (%s, %s, %s, %s)",
            (role, pseudo, password_hash.decode('utf-8'), salt.decode('utf-8'))
        )
        print("Les identifiants et le rôle de l'administrateur ont bien été enregistrés dans la base de données.")

        # Validation de la procédure et enregistrement au sein de la base de données.
        conn.commit()

except pymysql.MySQLError as e:
    print(f"Erreur lors de l'insertion dans la base de données: {e}")
except Exception as e:
    print(f"Une erreur s'est produite: {e}")
finally:
    if conn:
        conn.close()  # Assurez-vous de fermer la connexion
        print("Connexion à la base de données fermée.")

# Génération d'un message affirmant que la procédure s'est bien passée.
print("Les identifiants de l'administrateur ont bien été enregistrés et sont sécurisés.")