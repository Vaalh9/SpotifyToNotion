import os
from notion_utils import NotionSync
from spotify_utils import SpotifySync

notion = NotionSync()
spotify = SpotifySync()

def get_all_notion_artists():
    all_artists = []
    start_cursor = None
    while True:
        query = {"database_id": os.getenv("NOTION_DB_ARTISTS_ID")}
        if start_cursor:
            query["start_cursor"] = start_cursor
        res = notion.client.databases.query(**query)
        all_artists.extend(res["results"])
        if res.get("has_more"):
            start_cursor = res["next_cursor"]
        else:
            break
    return all_artists

def has_photo(artist_props):
    files = artist_props.get("Photo", {}).get("files", [])
    return bool(files)

def patch_artists_photos():
    all_artists = get_all_notion_artists()
    print(f"[PATCH] {len(all_artists)} artistes trouvés dans Notion.")
    patched = 0
    for artist in all_artists:
        props = artist["properties"]
        artist_id = artist["id"]
        name = None
        if props.get("Nom") and props["Nom"].get("title"):
            titles = props["Nom"]["title"]
            if titles and isinstance(titles, list) and len(titles) > 0:
                name = titles[0].get("plain_text")
        if not name:
            continue
        if has_photo(props):
            continue  # Déjà une photo
        print(f"[PATCH] Artiste sans photo : {name}")
        # Cherche l'artiste sur Spotify
        sp_artist = spotify.search_artist_by_name(name)
        if not sp_artist:
            print(f"[PATCH] Pas trouvé sur Spotify : {name}")
            continue
        photo_url = sp_artist['images'][0]['url'] if sp_artist.get('images') else None
        if not photo_url:
            print(f"[PATCH] Pas de photo sur Spotify : {name}")
            continue
        try:
            notion.update_artist(artist_id, photo_url=photo_url)
            print(f"[PATCH] Photo ajoutée à {name}")
            patched += 1
        except Exception as e:
            print(f"[PATCH][ERREUR] Impossible de mettre à jour {name} : {e}")
    print(f"[PATCH] {patched} artistes corrigés.")

if __name__ == "__main__":
    patch_artists_photos()
