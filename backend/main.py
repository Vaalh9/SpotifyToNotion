import os
from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
import os

dotenv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
print("Chemin .env utilisé :", dotenv_path)
load_dotenv(dotenv_path)
from backend.notion_utils import NotionSync
from backend.spotify_utils import SpotifySync
from typing import Optional

load_dotenv()

app = FastAPI()

# Autoriser toutes les origines (debug CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080", "http://127.0.0.1:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

notion = NotionSync()
spotify = SpotifySync()

@app.post("/clean_album_duplicates")
def clean_album_duplicates():
    try:
        notion.clean_album_duplicates()
        return {"status": "Nettoyage des doublons terminé."}
    except Exception as e:
        import traceback
        print("Erreur dans /clean_album_duplicates :", e)
        traceback.print_exc()
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/sync_artists")
def sync_spotify_artists_to_notion():
    try:
        artists = spotify.get_followed_artists()
        created = 0
        updated = 0
        for artist in artists:
            print(f"[SYNC][DEBUG][RAW] Artiste Spotify brut : {artist}")
            artist_name = artist['name']
            photo_url = artist['images'][0]['url'] if artist.get('images') else None
            genres = artist.get('genres', [])
            popularity = artist.get('popularity')
            artist_id = notion.find_artist(artist_name)
            if artist_id:
                notion.update_artist(artist_id, photo_url=photo_url, genres=genres, popularity=popularity)
                print(f"[SYNC][UPDATE] {artist_name} mis à jour | genres: {genres}, popularité: {popularity}, photo: {photo_url}")
                updated += 1
            else:
                notion.create_artist(artist_name, photo_url=photo_url, genres=genres, popularity=popularity)
                print(f"[SYNC][CREATE] {artist_name} créé | genres: {genres}, popularité: {popularity}, photo: {photo_url}")
                created += 1
        return {"status": f"Synchronisation terminée. {created} artistes créés, {updated} artistes mis à jour."}
    except Exception as e:
        import traceback
        print("Erreur dans /sync_artists :", e)
        traceback.print_exc()
        try:
            return JSONResponse(status_code=500, content={"error": str(e)})
        except Exception as err:
            print("Erreur critique backend:", err)
            traceback.print_exc()
            return {"error": f"Erreur critique backend: {str(err)}"}

@app.post("/sync")
def sync_spotify_to_notion():
    try:
        # Exemple : synchronisation des albums sauvegardés
        albums = spotify.get_saved_albums()
        created = 0
        for item in albums:
            alb = item['album']
            artist_name = alb['artists'][0]['name']
            artist_id = notion.find_artist(artist_name)
            photo_url_artist = alb['artists'][0]['images'][0]['url'] if ('images' in alb['artists'][0] and alb['artists'][0]['images']) else None
            if not artist_id:
                artist_id = notion.create_artist(artist_name, photo_url=photo_url_artist)
            spotify_album_id = alb['id']
            album_id = notion.find_album(alb['name'], artist_id, spotify_album_id=spotify_album_id)
            label = alb.get('label')
            nb_pistes = alb.get('total_tracks')
            cover_url = alb['images'][0]['url'] if alb['images'] else None
            annee = int(alb['release_date'][:4])
            if not album_id:
                print("[DEBUG ALBUM]", alb['name'], "| label:", label, "| total_tracks:", nb_pistes)
                notion.create_album(
                    name=alb['name'],
                    year=annee,
                    artist_id=artist_id,
                    cover_url=cover_url,
                    listens=None,
                    label=label,
                    nb_pistes=nb_pistes,
                    spotify_album_id=spotify_album_id
                )
                created += 1
            else:
                print(f"[DEBUG UPDATE] Album déjà présent : {alb['name']} | Update label: {label}, nb_pistes: {nb_pistes}, cover_url: {cover_url}, annee: {annee}")
                notion.update_album(
                    album_id=album_id,
                    year=annee,
                    cover_url=cover_url,
                    label=label,
                    nb_pistes=nb_pistes,
                    spotify_album_id=spotify_album_id
                )
        return {"status": f"Synchronisation terminée. {created} albums ajoutés."}
    except Exception as e:
        import traceback
        print("Erreur dans /sync :", e)
        traceback.print_exc()
        try:
            return JSONResponse(status_code=500, content={"error": str(e)})
        except Exception as err:
            print("Erreur critique backend:", err)
            traceback.print_exc()
            return {"error": f"Erreur critique backend: {str(err)}"}

@app.post("/add_manual")
def add_manual_album(
    artist: str = Form(...),
    album: str = Form(...),
    year: int = Form(...),
    cover: Optional[UploadFile] = None,
    artist_photo: Optional[UploadFile] = None
):
    try:
        artist_id = notion.find_artist(artist)
        if not artist_id:
            # TODO: gérer l'upload de la photo artiste
            artist_id = notion.create_artist(artist, photo_url=None)
        # TODO: gérer l'upload de la pochette
        album_id = notion.find_album(album, artist_id)
        if not album_id:
            notion.create_album(name=album, year=year, artist_id=artist_id, cover_url=None)
        return {"status": "Ajout manuel effectué."}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
