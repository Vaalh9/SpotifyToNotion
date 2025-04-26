import requests

BACKEND_URL = "http://127.0.0.1:8000/clean_album_duplicates"

if __name__ == "__main__":
    print(f"Envoi de la requête POST à {BACKEND_URL} ...")
    try:
        response = requests.post(BACKEND_URL)
        print("Réponse:", response.status_code)
        print(response.json())
    except Exception as e:
        print("Erreur lors de la requête:", e)
