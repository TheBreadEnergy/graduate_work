# Export poetry dependencies to requirements.txt
requirements:
	poetry export --without-hashes -o requirements.txt

django-superuser:
	DJANGO_SUPERUSER_USERNAME=admin \
	DJANGO_SUPERUSER_PASSWORD=qwerty \
	DJANGO_SUPERUSER_EMAIL=admin@kekek.kek \
	python  ./app/manage.py createsuperuser --noinput || true


.PHONY: \
	requirements \
	django-superuser
