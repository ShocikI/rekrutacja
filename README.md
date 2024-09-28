# Budowanie aplikacji
Aby zbudować aplikację należy użyć komendy  
`docker build -t rekrutacja:latest .`

# Uruchomienie aplikacji 
Aby uruchomić aplikację, po zbudowaniu kontenera, należy użyć komendy  
`docker run --rm -p 8000:8000 rekrutacja:latest`

Aplikacja powinna być dostępna z poziomu przeglądarki pod adresem  
`127.0.0.1:8000`