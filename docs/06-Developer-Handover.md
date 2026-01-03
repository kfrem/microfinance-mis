# Developer Handover
## How to continue
1) Ensure Docker Desktop is running
2) docker compose up -d
3) App container logs: docker compose logs -f web
4) Database container logs: docker compose logs -f db
5) Apply migrations: docker compose exec web python manage.py migrate
6) Create admin user: docker compose exec web python manage.py createsuperuser

## Checkpoints
- PROJECT_BOOTSTRAP_CREATED
