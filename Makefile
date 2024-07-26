superuser:
	docker compose exec auth-api make create-superuser

run:
	docker compose up -d

stop:
	docker compose down