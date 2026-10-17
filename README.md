# CareOS — Healthcare Records Controller

A complete, production-grade **Healthcare Backend** and **Kuber-OS-Style UI** built with Django 5, Django REST Framework (DRF), PostgreSQL, and SimpleJWT.

```
healthcare_backend/
├── manage.py
├── requirements.txt
├── .env.example
├── .gitignore
├── README.md
├── postman_collection.json
├── config/
├── accounts/
├── patients/
├── doctors/
├── mappings/
├── core/
├── templates/
└── static/
```

For full documentation, architectural details, API reference tables, and setup instructions, see [healthcare_backend/README.md](healthcare_backend/README.md).

---

## Quickstart

```bash
cd healthcare_backend
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver 127.0.0.1:8000
```

Run test suite (29/29 tests passing):
```bash
python manage.py test
```
