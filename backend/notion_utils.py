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

    def create_artist(self, name: str, photo_url: Optional[str] = None) -> str:
        # Crée une page artiste
        props = {"Nom": {"title": [{"text": {"content": name}}]}}
        if photo_url:
            props["Photo"] = {"files": [{"type": "external", "name": name, "external": {"url": photo_url}}]}
        page = self.client.pages.create(parent={"database_id": DB_ARTISTS_ID}, properties=props)
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

    def create_album(self, name: str, year: int, artist_id: str, cover_url: Optional[str] = None, listens: Optional[int] = None) -> str:
        props = {
            "Nom": {"title": [{"text": {"content": name}}]},
            "Année": {"number": year},
            "Artiste": {"relation": [{"id": artist_id}]}
        }
        if cover_url:
            props["Pochette"] = {"files": [{"type": "external", "name": name, "external": {"url": cover_url}}]}
        if listens is not None:
            props["Écoutes"] = {"number": listens}
        page = self.client.pages.create(parent={"database_id": DB_ALBUMS_ID}, properties=props)
        return page["id"]

    # TODO: Méthodes pour titres, update, etc.
