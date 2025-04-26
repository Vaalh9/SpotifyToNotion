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
        # Correction : l'API Notion ignore parfois le cover à la création, donc on le force après
        if photo_url:
            try:
                self.client.pages.update(page_id=page["id"], cover={"type": "external", "external": {"url": photo_url}})
            except Exception as e:
                print(f"[DEBUG][ARTIST] Impossible de mettre à jour la cover : {e}")
        return page["id"]

    def find_album(self, name: str, artist_id: Optional[str] = None, spotify_album_id: Optional[str] = None) -> Optional[str]:
        # Recherche l'album par Spotify Album ID si fourni, sinon par nom (et artiste)
        if spotify_album_id:
            filters = [{"property": "Spotify Album ID", "rich_text": {"equals": spotify_album_id}}]
            res = self.client.databases.query(
                **{"database_id": DB_ALBUMS_ID, "filter": {"and": filters}}
            )
            if res["results"]:
                return res["results"][0]["id"]
        # Sinon, fallback sur nom + artiste
        filters = [{"property": "Nom", "title": {"equals": name}}]
        if artist_id:
            filters.append({"property": "Artiste", "relation": {"contains": artist_id}})
        res = self.client.databases.query(
            **{"database_id": DB_ALBUMS_ID, "filter": {"and": filters}}
        )
        if res["results"]:
            return res["results"][0]["id"]
        return None

    def create_album(self, name: str, year: int, artist_id: str, cover_url: Optional[str] = None, listens: Optional[int] = None, label: Optional[str] = None, nb_pistes: Optional[int] = None, spotify_album_id: Optional[str] = None) -> str:
        props = {
            "Nom": {"title": [{"text": {"content": name}}]},
            "Année": {"number": year},
            "Artiste": {"relation": [{"id": artist_id}]}
        }
        if spotify_album_id:
            print(f"[DEBUG] Ajout Spotify Album ID: {spotify_album_id}")
            props["Spotify Album ID"] = {"rich_text": [{"text": {"content": spotify_album_id}}]}
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

    def update_album(self, album_id: str, year: Optional[int] = None, cover_url: Optional[str] = None, listens: Optional[int] = None, label: Optional[str] = None, nb_pistes: Optional[int] = None, spotify_album_id: Optional[str] = None):
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
        if spotify_album_id:
            print(f"[DEBUG] Update Spotify Album ID: {spotify_album_id}")
            props["Spotify Album ID"] = {"rich_text": [{"text": {"content": spotify_album_id}}]}
        print(f"[DEBUG] Mise à jour album {album_id} avec:", props)
        cover = {"type": "external", "external": {"url": cover_url}} if cover_url else None
        if props or cover:
            self.client.pages.update(page_id=album_id, properties=props, cover=cover)

    def clean_album_duplicates(self):
        print('[CLEAN] Recherche de doublons dans la base albums Notion...')
        # Récupère tous les albums
        all_albums = []
        start_cursor = None
        while True:
            query = {"database_id": DB_ALBUMS_ID}
            if start_cursor:
                query["start_cursor"] = start_cursor
            res = self.client.databases.query(**query)
            all_albums.extend(res["results"])
            if res.get("has_more"):
                start_cursor = res["next_cursor"]
            else:
                break
        print(f"[CLEAN] {len(all_albums)} albums récupérés.")
        # Indexation par (Nom, Artiste) pour trouver les vrais doublons
        album_groups = {}
        for album in all_albums:
            props = album["properties"]
            album_id = album["id"]
            # Récupération robuste du Spotify Album ID
            spotify_id = None
            if props.get("Spotify Album ID") and props["Spotify Album ID"].get("rich_text"):
                rich_texts = props["Spotify Album ID"]["rich_text"]
                if rich_texts and isinstance(rich_texts, list) and len(rich_texts) > 0:
                    spotify_id = rich_texts[0].get("plain_text")
            nom = None
            if props.get("Nom") and props["Nom"].get("title"):
                titles = props["Nom"]["title"]
                if titles and isinstance(titles, list) and len(titles) > 0:
                    nom = titles[0].get("plain_text")
            label = None
            if props.get("Label") and props["Label"].get("rich_text"):
                rich_texts = props["Label"]["rich_text"]
                if rich_texts and isinstance(rich_texts, list) and len(rich_texts) > 0:
                    label = rich_texts[0].get("plain_text")
            group_key = (nom, label)
            print(f"[CLEAN][DEBUG] Album: id={album_id}, nom={repr(nom)}, label={repr(label)}, spotify_id={repr(spotify_id)}")
            album_info = {"id": album_id, "spotify_id": spotify_id}
            if group_key in album_groups:
                album_groups[group_key].append(album_info)
            else:
                album_groups[group_key] = [album_info]
        for group, albums in album_groups.items():
            if len(albums) > 1:
                print(f"[CLEAN][DEBUG] Groupe doublon: {group} -> {[a['id'] for a in albums]}")
        # Pour chaque groupe, garder en priorité l'album avec Spotify ID, sinon le premier
        to_delete = []
        for group, albums in album_groups.items():
            if len(albums) > 1:
                # Sépare ceux avec et sans ID
                with_id = [a for a in albums if a["spotify_id"]]
                without_id = [a for a in albums if not a["spotify_id"]]
                # Garde un seul avec ID si possible, sinon un seul sans ID
                keep = None
                if with_id:
                    keep = with_id[0]["id"]
                    to_delete.extend([a["id"] for a in with_id[1:]])
                    to_delete.extend([a["id"] for a in without_id])
                else:
                    keep = without_id[0]["id"]
                    to_delete.extend([a["id"] for a in without_id[1:]])
        print(f"[CLEAN] {len(to_delete)} doublons trouvés (par nom+artiste). Suppression en cours...")
        for aid in to_delete:
            try:
                self.client.pages.update(page_id=aid, archived=True)
                print(f"[CLEAN] Album {aid} supprimé.")
            except Exception as e:
                print(f"[CLEAN][ERREUR] Impossible de supprimer {aid} : {e}")
        print('[CLEAN] Nettoyage terminé.')
        print(f"[CLEAN] {len(to_delete)} doublons trouvés. Suppression en cours...")
        for aid in to_delete:
            try:
                self.client.pages.update(page_id=aid, archived=True)
                print(f"[CLEAN] Album {aid} supprimé.")
            except Exception as e:
                print(f"[CLEAN][ERREUR] Impossible de supprimer {aid} : {e}")
        print('[CLEAN] Nettoyage terminé.')

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
