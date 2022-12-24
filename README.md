# read-api

## Install
```bash
    docker compose up
    docker exec -it server sh
    python manage.py migrate
    python manage.py createsuperuser
```

## OpenAPI Documentation
```bash
    http://localhost:8000/api/docs
```
* logout and logoutAll views are not part of the documentation
* api.http file contains sample requests
```bash
    http://localhost:8000/api/auth/logout/
    http://localhost:8000/api/auth/logoutall/
```
