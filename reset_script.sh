docker compose down -v
docker compose up db -d
sleep 2.0
python manage.py migrate
python manage.py createsuperuser
sleep 0.5
admin
admin@admin.nl
adminadmin
adminadmin
y
python manage.py runserver 0.0.0.0:8000
