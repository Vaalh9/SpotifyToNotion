import subprocess
import webbrowser
import time
import sys
import os

# Démarre le backend
backend_cmd = [sys.executable, '-m', 'uvicorn', 'backend.main:app', '--reload', '--host', '0.0.0.0', '--port', '8000']
backend_proc = subprocess.Popen(backend_cmd, cwd=os.path.dirname(__file__))

# Démarre le frontend
frontend_cmd = [sys.executable, '-m', 'http.server', '8080', '--directory', 'frontend']
frontend_proc = subprocess.Popen(frontend_cmd, cwd=os.path.dirname(__file__))

# Attend quelques secondes que les serveurs démarrent
print('Lancement du backend et du frontend...')
time.sleep(3)

# Ouvre le frontend dans le navigateur par défaut
webbrowser.open('http://localhost:8080')

print('Application SpotifyToNotion lancée !')
print('Fermez cette fenêtre pour arrêter les serveurs.')

# Attend la fermeture des serveurs (Ctrl+C ou fermeture de la console)
try:
    backend_proc.wait()
    frontend_proc.wait()
except KeyboardInterrupt:
    print('Arrêt de l\'application...')
    backend_proc.terminate()
    frontend_proc.terminate()
