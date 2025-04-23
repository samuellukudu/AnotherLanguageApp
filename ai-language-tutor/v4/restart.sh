docker compose down
sudo pkill -9 python
sudo pkill -9 docker
sudo pkill -9 fastapi
sudo pkill -9 uvicorn
sudo systemctl stop redis
sudo systemctl stop postgresql

# docker compose up --build
docker-compose up --build