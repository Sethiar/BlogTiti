"""
Fichier qui permet de gérer les demandes et les réceptions de la caméra pour le chat vidéo.
"""

from app import socketio
from flask_socketio import emit, join_room, leave_room


@socketio.on('offer')
def handle_offer(data):
    """
    :param data: Contient les informations de l'offre et l'identifiant du destinataire.
    """
    room = data['room']
    emit('offer', data, room=room)


@socketio.on('answer')
def handle_answer(data):
    """
    :param data: Contient la réponse et l'identifiant du destinataire.
    """
    room = data['room']
    emit('answer', data, room=room)


@socketio.on('ice-candidate')
def handle_candidate(data):
    """
    :param data: Contient le candidat ICE et l'identifiant du destinataire.
    """
    room = data['room']
    emit('ice-candidate', data, room=room)


@socketio.on('end-chat')
def handle_end_chat():
    """
    Logique pour gérer la fin de la session de chat.
    :return:
    """

    print("Chat session has been ended.")
