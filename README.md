# Foodgram

Foodgram is an educational thesis project in Yandex.Practicum. This is a website for sharing recipes. The frontend is provided by Yandex, it is built on React. The backend is made by me on the basis of Django Rest Framework.

## Installation

The project is deployed using the Docker-compose. From the infra folder, run:

```bash
docker-compose up --build

docker exec -it <DOCKER_CONTAINER_ID> python manage.py migrate

docker exec -it <DOCKER_CONTAINER_ID> python manage.py createsuperuser
```
The project will be available at localhost
