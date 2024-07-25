# Export poetry dependencies to requirements.txt
requirements:
	poetry export --without-hashes -o requirements.txt

django-superuser:
	DJANGO_SUPERUSER_USERNAME=admin \
	DJANGO_SUPERUSER_PASSWORD=qwerty \
	DJANGO_SUPERUSER_EMAIL=admin@kekek.kek \
	python  ./app/manage.py createsuperuser --noinput || true

translation:
	@poetry run django-admin makemessages -i "venv" -i ".venv" -l en -l ru

compile-translation:
	@poetry run django-admin compilemessages -i "venv" -i ".venv" -l en -l ru

.PHONY: \
	translation \
	compile-translation \
	requirements \
	django-superuser
