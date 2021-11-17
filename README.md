# Foodgram

Foodgram is an educational graduation project in Yandex.Practicum. This is a website for sharing recipes. The frontend is provided by Yandex, it is built on React. The backend is made by me on the basis of Django Rest Framework.

![NNbGpwJKqAs](https://user-images.githubusercontent.com/74203877/142297264-21e07116-c3e4-47e3-a35d-0e37f05f162b.jpg)


## Installation

The project is deployed using the Docker-compose. From the infra folder, run:

```bash
docker-compose up --build

docker exec -it <DOCKER_CONTAINER_ID> python manage.py migrate

docker exec -it <DOCKER_CONTAINER_ID> python manage.py createsuperuser
```
The project will be available at localhost

## Author

Georgy Satkov
* [github/Satkov](https://github.com/Satkov)
