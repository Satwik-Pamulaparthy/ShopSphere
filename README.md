# Django E‑Shop (Ready-to-run)

A minimal but production-minded **Django e-commerce** project showcasing:
- Products catalog (list/detail)
- Session-based cart
- Checkout to Orders/OrderItems
- Auth (register/login/logout)
- Admin
- A tiny JSON API (`/api/products/`)
- Tests
- Dockerfile

## Quickstart (Mac/Linux)

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

cd eshop
python manage.py migrate
python manage.py createsuperuser  # optional for admin
python manage.py seed_products    # sample products
python manage.py runserver
```

Open: http://127.0.0.1:8000/

## Run tests
```bash
cd eshop
python manage.py test
```

## Docker (dev)
```bash
cd eshop
docker build -t django-eshop .
docker run --rm -it -p 8000:8000 django-eshop
```

## SDE Relevance

- **Backend architecture**: models, views, urls, middleware/context processors
- **State management**: session cart
- **Data modeling**: Orders, OrderItems, Products
- **Security**: Django auth, CSRF, admin
- **API thinking**: `/api/products/` JSON endpoint
- **Quality**: unit tests, seed command, Dockerfile

Extend with: payments (Stripe), DRF APIs, search, pagination, caching, Celery for async tasks.
