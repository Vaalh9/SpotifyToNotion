# SpotifyToNotion

Synchronisez automatiquement vos albums Spotify favoris avec une base de données Notion, via une interface web simple et un backend FastAPI.

---
<<<<<<< HEAD
=======
- Interface web simple
- Déploiement Docker
>>>>>>> f164bf2 (Commit complet : synchronisation Spotify ↔ Notion, debug, doc et automatisation)

## 🚀 Présentation

**SpotifyToNotion** est une application qui permet de :
- Synchroniser vos albums Spotify sauvegardés dans une base Notion
- Ajouter manuellement des albums dans Notion via le frontend
- Visualiser l'état de la synchronisation (progression, erreurs, succès)

Idéal pour garder une trace organisée de votre collection musicale dans Notion !

---

## ✨ Fonctionnalités principales

- Authentification sécurisée avec Spotify et Notion
- Synchronisation automatique des albums Spotify → Notion
- Ajout manuel d'albums depuis l'interface web
- Gestion des artistes et des pochettes
- Feedback utilisateur (succès/erreur) en temps réel
- Lancement simplifié backend + frontend

---

## 🛠️ Prérequis

- Python 3.8+
- Un compte Spotify
- Un compte Notion
- Un token d'intégration Notion et les IDs de vos bases Notion (voir ci-dessous)

---

## ⚙️ Installation & Configuration

1. **Clonez le dépôt :**
   ```sh
   git clone https://github.com/Vaalh9/SpotifyToNotion.git
   cd SpotifyToNotion
   ```
2. **Installez les dépendances :**
   ```sh
   pip install -r requirements.txt
   ```
3. **Configurez les variables d'environnement :**
   - Copiez `.env.example` en `.env` et renseignez :
     - `NOTION_TOKEN` : token d'intégration Notion
     - `NOTION_DB_ALBUMS_ID` : ID de la base Notion Albums
     - `NOTION_DB_ARTISTS_ID` : ID de la base Notion Artistes
     - `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, `SPOTIPY_REDIRECT_URI` : infos Spotify

---

## ▶️ Lancement rapide

### 1. Lancer le backend
```sh
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```
### 2. Lancer le frontend
```sh
python -m http.server 8080 --directory frontend
```
### 3. (Optionnel) Lancement automatique
Double-cliquez sur `start_all.bat` pour ouvrir deux terminaux (backend + frontend).

- Frontend : [http://localhost:8080](http://localhost:8080)
- Backend (API docs) : [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 💡 Utilisation

- Cliquez sur "Synchroniser Spotify" pour importer vos albums dans Notion
- Ajoutez un album manuellement via le formulaire dédié
- Les feedbacks (succès/erreur) s'affichent sous le bouton

---

## 🧰 Dépannage / FAQ

- **Erreur "API token is invalid"** : Vérifiez les variables dans `.env` et les droits de l'intégration Notion
- **Erreur "... is not a property that exists"** : Ajoutez la propriété manquante dans la base Notion
- **0 albums ajoutés** : Les albums existent déjà ou la liste Spotify est vide
- **Le frontend est inaccessible** : Relancez le serveur avec la commande ci-dessus

---

## 📄 Licence & Crédits

- Projet open-source (MIT)
- Développé par Vaalh9 et contributeurs
- Utilise [FastAPI](https://fastapi.tiangolo.com/), [Spotipy](https://spotipy.readthedocs.io/), [notion-client](https://github.com/ramnes/notion-sdk-py)

---

## 🔗 Liens utiles

- [Créer une intégration Notion](https://www.notion.so/my-integrations)
- [Créer une app Spotify](https://developer.spotify.com/dashboard)
- [API Notion](https://developers.notion.com/)
- [API Spotify](https://developer.spotify.com/documentation/web-api/)
