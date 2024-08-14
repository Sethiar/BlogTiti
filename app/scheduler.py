"""
Fichier permettant de créer la tâche pour la mise à jour des informations des vidéos.
"""
import os
from apscheduler.schedulers.background import BackgroundScheduler

YOUTUBE_API = os.getenv('YOUTUBE_API')
ID_CHANNEL = os.getenv('ID_CHANNEL')


def create_scheduler(app):
    """
    Crée et retourne une instance de BackgroundScheduler.
    :param app: Instance de l'application Flask.
    :return:
    """
    scheduler = BackgroundScheduler()

    # Ajout de la tâche au planificateur.
    scheduler.add_job(
        func=lambda: scheduled_task(app),
        trigger='interval',
        hours=12,
        id='scheduled_task_job',
        name='Execute scheduled task every hour',
        replace_existing=True
    )

    return scheduler


def scheduled_task(app):
    """
    Tâche programmée qui s'exécute avec le contexte de l'application.
    :param app: Instance de l'application Flask.
    """
    # Utilisation du contexte d'application.
    with app.app_context():
        from app.videos import save_videos_to_db, YouTubeManager

        yt_manager = YouTubeManager()
        videos = yt_manager.get_all_videos()
        save_videos_to_db(videos)
