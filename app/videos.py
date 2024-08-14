"""
Fichier permettant de gérer la mise à jour des vidéos de la chaîne.
"""
# -*- coding: utf-8 -*-

from app.Models.videos import Video
from app import db

from googleapiclient.discovery import build
from sqlalchemy.exc import IntegrityError

from dotenv import load_dotenv
import os
import locale
from datetime import datetime, date

# Définir la locale en français
locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8')

# Chargement des variables d'environnement
load_dotenv()

YOUTUBE_API = os.getenv('YOUTUBE_API')
ID_CHANNEL = os.getenv('ID_CHANNEL')


class YouTubeManager:
    """

    """
    def __init__(self):
        self.api_key = YOUTUBE_API
        self.channel_id = ID_CHANNEL
        self.youtube = build('youtube', 'v3', developerKey=self.api_key)

    def get_all_videos(self):
        """
        Récupère toutes les vidéos d'une chaîne YouTube.

        :return: Liste des détails des vidéos.
        """
        videos = []
        next_page_token = None

        while True:
            request = self.youtube.search().list(
                part='snippet',
                channelId=self.channel_id,
                maxResults=100,
                order='date',
                pageToken=next_page_token
            )
            response = request.execute()

            for item in response['items']:
                if item['id']['kind'] == 'youtube#video':
                    video_id = item['id']['videoId']
                    video_details = self.get_video_details(video_id)
                    videos.append(video_details)

            next_page_token = response.get('nextPageToken')

            if not next_page_token:
                break

        return videos

    def get_video_details(self, video_id):
        """
        Récupère les détails d'une vidéo spécifique.
        :param video_id: ID de la vidéo
        :return: Détails de la vidéo sous forme de dictionnaire
        """
        video_request = self.youtube.videos().list(
            part='snippet, contentDetails, statistics',
            id=video_id
        )
        video_response = video_request.execute()
        video_details = video_response['items'][0]
        published_at_display, published_at_db = self.format_date(
            video_details['snippet'].get('publishedAt', 'Date inconnue'))
        return {
            'video_id': video_id,
            'title': video_details['snippet']['title'],
            'published_at_display': published_at_display,  # Pour l'affichage
            'published_at': published_at_db,  # Pour la base de données
            'view_count': int(video_details['statistics'].get('viewCount', 0)),
            'like_count': int(video_details['statistics'].get('likeCount', 0)),
            'comment_count': int(video_details['statistics'].get('commentCount', 0)),
            'tags': video_details['snippet'].get('tags', [])
        }

    @staticmethod
    def format_date(published_at):
        """
        Formate la date en deux formats :
        - Un format chaîne de caractères pour l'affichage.
        - Un objet datetime.date pour la base de données.
        :param published_at: Date en format chaîne de caractères ou objet datetime.
        :return: tuple (str, date)
        """
        if isinstance(published_at, str):
            # Convertir une chaîne en objet datetime
            dt_object = datetime.strptime(published_at, "%Y-%m-%dT%H:%M:%SZ")
        elif isinstance(published_at, (datetime, date)):
            # Utiliser directement l'objet datetime
            dt_object = datetime.combine(published_at, datetime.min.time())
        else:
            return 'Date inconnue', None

        # Pour l'affichage en français.
        formatted_date = dt_object.strftime("%d %B %Y")
        # Pour la base de données
        date_for_db = dt_object.date()
        return formatted_date, date_for_db


def save_videos_to_db(videos):
    """
    Sauvegarde ou met à jour les vidéos dans la base de données.
    :param videos: Liste de vidéos à sauvegarder
    """
    try:
        for video in videos:
            existing_video = Video.query.filter_by(video_id=video['video_id']).first()
            if existing_video:
                # Mettre à jour les informations si nécessaire
                existing_video.title = video['title']
                existing_video.published_at = video['published_at']  # Utilisation du format date
                existing_video.view_count = video['view_count']
                existing_video.like_count = video['like_count']
                existing_video.comment_count = video['comment_count']
                existing_video.tags = video['tags']
            else:
                # Créer une nouvelle entrée
                new_video = Video(
                    video_id=video['video_id'],
                    title=video['title'],
                    published_at=video['published_at'],  # Utilisation du format date
                    view_count=video['view_count'],
                    like_count=video['like_count'],
                    comment_count=video['comment_count'],
                    tags=video['tags']
                )
                db.session.add(new_video)
        db.session.commit()
    except IntegrityError as e:
        db.session.rollback()
        print(f"Error occurred: {e}")
