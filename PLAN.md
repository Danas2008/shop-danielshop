# DanielsPrints Implementation Plan

## Phase 1: Django Setup — done
- [x] Django project + apps (products, orders, cart)
- [x] Dependencies installed (django, gunicorn, stripe, pillow, django-jazzmin, python-dotenv)
- [x] .env with SECRET_KEY, STRIPE keys, DEBUG
- [x] settings.py configured (apps, DB, MEDIA/STATIC, ALLOWED_HOSTS, Jazzmin)
- [x] Models: Product, Order, CartItem
- [x] Migrations + seed data migration (5 ready-made, 3 STL, 1 builder product)
- [x] Superuser created

## Phase 2: Base Templates & Homepage — done
- [x] base.html (nav, footer, responsive)
- [x] style.css (DanielsPrints palette)
- [x] SVG logo
- [x] Homepage: hero, ready-made grid, builder CTA, STL grid

## Phase 3: Product Pages — done
- [x] Listing page with category filter + pagination
- [x] Detail page (ready-made form fields, STL static info, size selector, magnets, related products)

## Phase 4: Custom Builder — done
- [x] Builder page: form (template selector, items, message, date, height, magnets)
- [x] Live 3D CSS-transform receipt preview
- [x] POST /api/builder/preview/ endpoint (debounced sync)

## Phase 5: Cart & Checkout — done
- [x] Session-based cart (add/remove/update)
- [x] Cart page
- [x] Checkout page + customer info form
- [x] Stripe Checkout Session creation
- [x] Success page

## Phase 6: Stripe Webhooks — done
- [x] /stripe-webhook/ endpoint, verifies signature
- [x] Marks Order as paid on checkout.session.completed / payment_intent.succeeded

## Phase 7: Admin Dashboard — done
- [x] ProductAdmin (image preview, filters, search)
- [x] OrderAdmin (JSON items pretty-print, bulk actions, filters)
- [x] Custom Jazzmin dashboard: revenue, orders, status pie, top products, 30-day revenue chart, recent orders

## Phase 8: Legal Pages — done
- [x] /terms/ /privacy/ /shipping/ /about/ /contact/

## Phase 9: Deployment — done
- [x] deploy/shop.service (gunicorn systemd unit)
- [x] deploy/nginx_shop.conf (reverse proxy, SSL, static/media)
- [ ] Actual server provisioning (run on Hetzner box, DNS, certbot) — pending real deploy

## Phase 10: Testing & Polish — done (local)
- [x] Manual e2e smoke test: home, shop, detail, builder, cart add, checkout GET, builder preview API, admin dashboard
- [ ] Live Stripe payment test (needs real API keys)
- [ ] Production hardening pass once deployed
