# ArtHub backend

# Режим запуска
```bash
    docker stop <container id>
    docker build -t art_hub-backend:latest .
    docker run --rm --name art_hub-backend -d -p 0.0.0.0:8087:8080 art_hub-backend
```