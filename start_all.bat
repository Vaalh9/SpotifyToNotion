start cmd /k "uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000"
start cmd /k "python -m http.server 8080 --directory frontend"
