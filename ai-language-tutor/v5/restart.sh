docker compose down --remove-orphans
sudo pkill -9 python
sudo pkill -9 uvicorn
sudo pkill -9 fastapi
sudo systemctl stop redis
sudo lsof -t -i:8001 | xargs -r sudo kill -9
docker compose up --build --remove-orphans