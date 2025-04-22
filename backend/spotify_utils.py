import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI")

SCOPE = "user-library-read user-read-recently-played user-top-read"

class SpotifySync:
    def __init__(self):
        # Pour compatibilité avec 127.0.0.1:8000/callback
        try:
            self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
                client_id=SPOTIFY_CLIENT_ID,
                client_secret=SPOTIFY_CLIENT_SECRET,
                redirect_uri=SPOTIFY_REDIRECT_URI,
                scope=SCOPE,
                open_browser=True
            ))
        except Exception as e:
            print("[ERREUR Spotipy] Impossible d’ouvrir automatiquement le navigateur pour l’authentification Spotify.")
            try:
                auth_manager = SpotifyOAuth(
                    client_id=SPOTIFY_CLIENT_ID,
                    client_secret=SPOTIFY_CLIENT_SECRET,
                    redirect_uri=SPOTIFY_REDIRECT_URI,
                    scope=SCOPE,
                    open_browser=False
                )
                auth_url = auth_manager.get_authorize_url()
                print(f"[INFO] Ouvre manuellement cette URL pour t’authentifier Spotify : {auth_url}")
                self.sp = spotipy.Spotify(auth_manager=auth_manager)
            except Exception as err:
                print(f"[ERREUR Spotipy critique] {err}")
                raise

    def get_saved_albums(self):
        # Récupère les albums sauvegardés
        results = self.sp.current_user_saved_albums(limit=50)
        return results['items']

    def get_top_artists(self):
        # Récupère les artistes favoris
        results = self.sp.current_user_top_artists(limit=20)
        return results['items']

    def get_recently_played(self):
        # Récupère les titres récemment écoutés
        results = self.sp.current_user_recently_played(limit=50)
        return results['items']

    # TODO: Méthodes pour extraire infos album/artiste/titre, pochettes, etc.
