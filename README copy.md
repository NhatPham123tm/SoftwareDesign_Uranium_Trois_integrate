## Run the backend

```shell
python -m venv venv
```
For windows
```shell
.\venv\Scripts\activate
```

For MacOS
```shell
source venv/bin/activate
```
Continue
```shell
cd backend
pip install -r requirements.txt
python manage.py runserver
```
## Frontend
```shell
cd frontend
npm install
npm run dev
```

## Docker
Create .env file from .env-example in backend directory

docker-compose up -d
docker-compose run backend python manage.py migrate
docker-compose run backend python manage.py createsuperuser
