"""
Code permettant de gérer les routes concernant la vision du blog.
"""

from app.Chat import chat_bp

from flask import render_template

from app.extensions import create_whereby_meeting_admin


# Route permettant de générer le lien du chat pour l'administrateur.
@chat_bp.route('/admin_room_url')
def chat_video_session_admin():
    """
    Génère le lien de session pour l'administrateur et le rend disponible.

    Cette route appelle une fonction pour générer un lien unique pour la session de chat vidéo destinée à
    l'administrateur. Le lien est ensuite rendu disponible via un template HTML. Si la génération du lien échoue,
    une erreur est retournée.

    Returns:
        Response: Le rendu du modèle HTML 'chat/chat_session_admin.html' avec le lien de session si la génération
                  est réussie. Sinon, retourne un message d'erreur avec le code de statut 500.
    """
    # Appel de la fonction qui génère le lien administrateur.
    admin_room_url = create_whereby_meeting_admin()

    if admin_room_url:
        # Log pour vérifier le lien récupéré.
        print("Admin Host Room URL:", admin_room_url)

        # Rendu du template avec le lien admin.
        return render_template('chat/chat_session_admin.html', room_url=admin_room_url)
    else:
        # Retourne une erreur si l'URL n'a pas pu être générée.
        return "Erreur lors de la génération de la réunion whereby côté administrateur.", 500
