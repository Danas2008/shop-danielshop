# Deploying DanielsPrints to shop.danielhavlicek.cz (Hetzner)

Assumes: repo lives at `/var/www/shop`, app runs on `127.0.0.1:8005` behind
nginx, and you're reusing the existing `danielhavlicek.cz` Let's Encrypt cert
(add `shop.danielhavlicek.cz` as a SAN, or issue a new cert — see step 6).

## 1. Get the code onto the server

```bash
ssh youruser@your-server-ip
sudo mkdir -p /var/www/shop
sudo chown $USER:$USER /var/www/shop
git clone <your-repo-url> /var/www/shop
cd /var/www/shop
```

## 2. Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## 3. Environment file

```bash
cp .env.example .env
nano .env
```

Fill in for real:
- `SECRET_KEY` — generate one: `python -c "import secrets; print(secrets.token_urlsafe(50))"`
- `DEBUG=False`
- `ALLOWED_HOSTS=shop.danielhavlicek.cz`
- `STRIPE_PUBLIC_KEY` / `STRIPE_SECRET_KEY` — from your Stripe dashboard (live or test)
- `STRIPE_WEBHOOK_SECRET` — from the webhook endpoint you create in step 7

## 4. Database + static files

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
```

## 5. Gunicorn systemd service

```bash
sudo cp deploy/shop.service /etc/systemd/system/shop.service
sudo nano /etc/systemd/system/shop.service   # fix User/Group and paths if not www-data/id matches your setup
sudo systemctl daemon-reload
sudo systemctl enable --now shop
sudo systemctl status shop     # confirm "active (running)"
```

## 6. TLS certificate

If your existing `danielhavlicek.cz` cert does NOT already cover this
subdomain, issue a new one (requires DNS for `shop.danielhavlicek.cz`
already pointing at this server):

```bash
sudo certbot certonly --nginx -d shop.danielhavlicek.cz
```

Then update `deploy/nginx_shop.conf`'s `ssl_certificate` /
`ssl_certificate_key` paths to point at
`/etc/letsencrypt/live/shop.danielhavlicek.cz/...` instead of the shared
`danielhavlicek.cz` cert, if you issued a dedicated one.

## 7. Nginx

```bash
sudo cp deploy/nginx_shop.conf /etc/nginx/sites-available/shop
sudo ln -s /etc/nginx/sites-available/shop /etc/nginx/sites-enabled/shop
sudo nginx -t
sudo systemctl reload nginx
```

## 8. Stripe webhook

In the Stripe dashboard, add an endpoint:
`https://shop.danielhavlicek.cz/stripe-webhook/`, subscribe to
`checkout.session.completed` (and/or `payment_intent.succeeded`), copy the
signing secret into `.env` as `STRIPE_WEBHOOK_SECRET`, then:

```bash
sudo systemctl restart shop
```

## 9. Smoke test

```bash
curl -I https://shop.danielhavlicek.cz/
curl -I https://shop.danielhavlicek.cz/admin/
```

Then in a browser: place a real test-mode order through checkout and
confirm the order shows as "Paid" in `/admin/orders/order/` after Stripe
redirects back.

## Redeploying after code changes

```bash
cd /var/www/shop
git pull
source venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --noinput
sudo systemctl restart shop
```
