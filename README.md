# DanielsPrints — 3D Printed Receipts E-Shop

Django e-commerce store for custom 3D printed keepsake receipts, with Stripe checkout and a Jazzmin admin dashboard.

## Local setup

```bash
python -m venv venv
source venv/Scripts/activate   # Windows Git Bash; use `venv\Scripts\activate` in cmd
pip install -r requirements.txt
cp .env.example .env            # then fill in real SECRET_KEY / Stripe keys
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver 127.0.0.1:8005
```

Visit http://127.0.0.1:8005/ for the storefront and http://127.0.0.1:8005/admin/ for the dashboard.

## Environment variables (`.env`)

| Variable | Purpose |
|---|---|
| `SECRET_KEY` | Django secret key |
| `DEBUG` | `True`/`False` |
| `ALLOWED_HOSTS` | comma-separated hostnames |
| `STRIPE_PUBLIC_KEY` / `STRIPE_SECRET_KEY` | Stripe API keys |
| `STRIPE_WEBHOOK_SECRET` | signing secret for `/stripe-webhook/` |

## Stripe webhook (local testing)

```bash
stripe listen --forward-to localhost:8005/stripe-webhook/
```

## Deployment (Hetzner)

Config templates live in `deploy/`:
- `shop.service` — systemd unit running Gunicorn on `127.0.0.1:8005`
- `nginx_shop.conf` — reverse proxy + TLS for `shop.danielhavlicek.cz`

```bash
python manage.py collectstatic --noinput
sudo cp deploy/shop.service /etc/systemd/system/shop.service
sudo cp deploy/nginx_shop.conf /etc/nginx/sites-available/shop
sudo ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/
sudo systemctl daemon-reload
sudo systemctl enable --now shop
sudo nginx -t && sudo systemctl reload nginx
```

## Project structure

See `PLAN.md` for the phase-by-phase implementation checklist.
