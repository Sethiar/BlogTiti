"""
Fichier principal de l'application du blog de Titi
"""
import os

from flask import render_template

from app import create_app

app = create_app()


@app.route("/")
def landing_page():
    """

    :return:
    """
    return render_template("frontend/accueil.html")


if __name__ == '__main__':
    app.run(debug=True)
