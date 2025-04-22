import os
from notion_client import Client
from typing import Optional

NOTION_TOKEN = os.getenv("NOTION_TOKEN")
DB_ALBUMS_ID = os.getenv("NOTION_DB_ALBUMS_ID")
DB_ARTISTS_ID = os.getenv("NOTION_DB_ARTISTS_ID")

class NotionSync:
    def __init__(self):
        print("NOTION_TOKEN utilisé:", NOTION_TOKEN)
        print("DB_ALBUMS_ID:", DB_ALBUMS_ID)
        print("DB_ARTISTS_ID:", DB_ARTISTS_ID)
        self.client = Client(auth=NOTION_TOKEN)

    def find_artist(self, name: str) -> Optional[str]:
        # Recherche l'artiste par nom, retourne l'ID de page si trouvé
        res = self.client.databases.query(
            **{"database_id": DB_ARTISTS_ID, "filter": {"property": "Nom", "title": {"equals": name}}}
        )
        if res["results"]:
            return res["results"][0]["id"]
        return None

    def create_artist(self, name: str, photo_url: Optional[str] = None, genres: Optional[list] = None, popularity: Optional[int] = None) -> str:
        # Crée une page artiste
        props = {"Nom": {"title": [{"text": {"content": name}}]}}
        if photo_url:
            props["Photo"] = {"files": [{"type": "external", "name": name, "external": {"url": photo_url}}]}
        if genres:
            props["Genres"] = {"multi_select": [{"name": g} for g in genres if g]}
        if popularity is not None:
            props["Popularité"] = {"number": popularity}
        print("[DEBUG] Propriétés envoyées à Notion pour l'artiste:", props)
        cover = {"type": "external", "external": {"url": photo_url}} if photo_url else None
        page = self.client.pages.create(parent={"database_id": DB_ARTISTS_ID}, properties=props, cover=cover)
        return page["id"]

    def find_album(self, name: str, artist_id: Optional[str] = None) -> Optional[str]:
        # Recherche l'album par nom (et artiste si précisé)
        filters = [{"property": "Nom", "title": {"equals": name}}]
        if artist_id:
            filters.append({"property": "Artiste", "relation": {"contains": artist_id}})
        res = self.client.databases.query(
            **{"database_id": DB_ALBUMS_ID, "filter": {"and": filters}}
        )
        if res["results"]:
            return res["results"][0]["id"]
        return None

    def create_album(self, name: str, year: int, artist_id: str, cover_url: Optional[str] = None, listens: Optional[int] = None, label: Optional[str] = None, nb_pistes: Optional[int] = None) -> str:
        props = {
            "Nom": {"title": [{"text": {"content": name}}]},
            "Année": {"number": year},
            "Artiste": {"relation": [{"id": artist_id}]}
        }
        if cover_url:
            props["Pochette"] = {"files": [{"type": "external", "name": name, "external": {"url": cover_url}}]}
        if listens is not None:
            props["Écoutes"] = {"number": listens}
        if label:
            props["Label"] = {"rich_text": [{"text": {"content": label}}]}
        if nb_pistes is not None:
            props["Nb pistes"] = {"number": nb_pistes}
        print("[DEBUG] Propriétés envoyées à Notion pour l'album:", props)
        cover = {"type": "external", "external": {"url": cover_url}} if cover_url else None
        page = self.client.pages.create(parent={"database_id": DB_ALBUMS_ID}, properties=props, cover=cover)
        return page["id"]

    def update_album(self, album_id: str, year: Optional[int] = None, cover_url: Optional[str] = None, listens: Optional[int] = None, label: Optional[str] = None, nb_pistes: Optional[int] = None):
        props = {}
        if year is not None:
            props["Année"] = {"number": year}
        if cover_url:
            props["Pochette"] = {"files": [{"type": "external", "name": "cover", "external": {"url": cover_url}}]}
        if listens is not None:
            props["Écoutes"] = {"number": listens}
        if label:
            props["Label"] = {"rich_text": [{"text": {"content": label}}]}
        if nb_pistes is not None:
            props["Nb pistes"] = {"number": nb_pistes}
        print(f"[DEBUG] Mise à jour album {album_id} avec:", props)
        cover = {"type": "external", "external": {"url": cover_url}} if cover_url else None
        if props or cover:
            self.client.pages.update(page_id=album_id, properties=props, cover=cover)

    def update_artist(self, artist_id: str, photo_url: Optional[str] = None, genres: Optional[list] = None, popularity: Optional[int] = None):
        props = {}
        if photo_url:
            props["Photo"] = {"files": [{"type": "external", "name": "photo", "external": {"url": photo_url}}]}
        if genres:
            props["Genres"] = {"multi_select": [{"name": g} for g in genres if g]}
        if popularity is not None:
            props["Popularité"] = {"number": popularity}
        print(f"[DEBUG] Mise à jour artiste {artist_id} avec:", props)
        cover = {"type": "external", "external": {"url": photo_url}} if photo_url else None
        if props or cover:
            self.client.pages.update(page_id=artist_id, properties=props, cover=cover)
