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
            if not artist_id:
                artist_id = notion.create_artist(artist_name, photo_url=None)  # TODO: photo
            album_id = notion.find_album(alb['name'], artist_id)
            if not album_id:
                notion.create_album(
                    name=alb['name'],
                    year=int(alb['release_date'][:4]),
                    artist_id=artist_id,
                    cover_url=alb['images'][0]['url'] if alb['images'] else None,
                    listens=None
                )
                created += 1
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
