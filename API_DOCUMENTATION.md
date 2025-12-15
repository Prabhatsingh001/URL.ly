**Project Overview**
- **Name:** URL.ly — Django-based URL shortener and biolink manager.
- **Root:** `UrlShortner` Django project. See [UrlShortner/UrlShortner/urls.py](UrlShortner/UrlShortner/urls.py#L1-L120) for top-level routing.

**Apps & Responsibilities**
- **Auth:** User registration, login/logout, profile, password reset, email verification, static pages. Routes: [UrlShortner/Auth/urls.py](UrlShortner/Auth/urls.py#L1-L120).
- **urlLogic:** URL shortening, redirection, QR generation, analytics and URL management. Routes: [UrlShortner/urlLogic/urls.py](UrlShortner/urlLogic/urls.py#L1-L140).
- **Biolink:** Biolink page creation and public pages. See views referenced from the project root routing in [UrlShortner/UrlShortner/urls.py](UrlShortner/UrlShortner/urls.py#L1-L120).
- **Brandlink, theme, others:** UI/branding, static assets and theme resources; not primary API surfaces but used by templates and front-end.

**Top-level Routes (summary)**
- **`/`** — Landing page (GET). See `IndexView` in `Auth.views` and root URLs: [UrlShortner/UrlShortner/urls.py](UrlShortner/UrlShortner/urls.py#L1-L120).
- **`/health/`** — Health check endpoint (GET).
- **`/admin/`** — Django admin interface.
- **`/auth/`** — Social auth integration (routes provided by `social_django`).
- **`/preview/`** — Preview original URL (GET) — handled by `urlLogic.views.get_original_url`.
- **`/s/`** — Anonymous short URL creation and listing: `anonymousShorturl` (likely POST to create, GET for form) and `redirect_to_original` accessed as `/s/<short_code>/` for redirect (GET).
- **`/a/`** — Auth app namespace (signup, login, profile, password management). See [UrlShortner/Auth/urls.py](UrlShortner/Auth/urls.py#L1-L120).
- **`/u/`** — URL management namespace for authenticated users. See [UrlShortner/urlLogic/urls.py](UrlShortner/urlLogic/urls.py#L1-L140).

**Auth endpoints (from `Auth.urls`)**
- **`/a/about/`** — About page (GET).
- **`/a/contact/`** — Contact form (GET/POST).
- **`/a/signup/`** — Signup (GET/POST).
- **`/a/login/`** — Login (GET/POST).
- **`/a/logout/`** — Logout (POST or GET depending on view).
- **`/a/profile/<uuid:id>/`** — View profile (GET).
- **`/a/profile-edit/<uuid:id>/`** — Update profile (GET/POST).
- **`/a/profile-password/<uuid:id>/`** — Change password (GET/POST).
- **`/a/activate/<uidb64>/<token>/`** — Email activation (GET).
- **`/a/resend-verification/<email>/`** — Resend verification (GET/POST as implemented).
- **`/a/forgot_password/`** — Forgot password entry (GET/POST).
- **`/a/reset_password/<uidb64>/<token>/`** — Reset password (GET/POST).

**URL Shortening endpoints (from `urlLogic.urls`)**
- **`/u/`** — Dashboard / home (GET).
- **`/u/shortenurl/`** — Create a shortened URL (typically POST; may also accept GET form) — view `make_short_url`.
- **`/u/analytics/<int:id>/`** — Analytics dashboard for URL id (GET) — view `analytics_dashboard`.
- **`/u/generateqr/`** — Generate a QR code for a URL (POST or GET depending on view) — view `generate_qr`.
- **`/u/delete/<int:id>/`** — Delete URL (POST/DELETE) — view `delete_url`.
- **`/u/updateurl/<int:id>/`** — Update URL settings (GET/POST) — view `update_url`.
- **`/u/<str:slug>/`** — Redirect to original URL (GET) — view `redirect_url`.
- **`/u/downloadqr/<int:id>/`** — Download QR code image (GET) — view `download_qr`.
- **`/u/mailqr/<int:id>/`** — Email QR code to user (POST) — view `mail_qr`.

**Biolink & Public Pages**
- **`/my-bio-link-page/`** — User's biolink management page (GET).
- **`/biolink-page/<uuid:id>/`** — Get links for a biolink profile (GET).
- **`/addlink/<uuid:id>/`**, **`/deletelink/<uuid:id>/`**, **`/editprofile/<uuid:id>/`**, **`/enable/`** — Biolink management operations (as implemented in `Biolink.views`).
- **`/p/<slug:slug>/`** — Public biolink page by slug (GET).

**Errors & Misc**
- Custom error handlers are defined: `handler404`, `handler500`, `handler403` in [UrlShortner/UrlShortner/urls.py](UrlShortner/UrlShortner/urls.py#L1-L120).
- Static and media served in DEBUG mode via settings configuration.

**Authentication & Security**
- Django authentication for user accounts (`Auth` app). Social authentication via `social_django` mounted at `/auth/`.
- Email verification flows and password reset use tokenized URLs (`activate`, `reset_password`).
- Protect user-specific routes (dashboard, URL management) behind login — ensure Django `login_required` or equivalent is applied in views.

**Database & Files**
- Default project DB present: `db.sqlite3` in project root; migrations under each app in their `migrations/` folder.
- GeoIP DB file: `GeoLite2-City.mmdb` located in the project root — used for geolocation in analytics.
- Media files: `media/` directory. Static files: `static/` (icons, main/css, main/js) and `theme/static/`.

**Setup & Local Run (developer quickstart)**
- Create virtualenv and install deps:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r UrlShortner/requirements.txt
```

- Apply migrations and create superuser:

```bash
python UrlShortner/manage.py migrate
python UrlShortner/manage.py createsuperuser
```

- Run dev server (static/media served automatically in DEBUG):

```bash
python UrlShortner/manage.py runserver
```

**Example Requests (templates)**
- Create a short URL (example):

```bash
curl -X POST "http://localhost:8000/s/" -d "url=https://example.com" -H "Content-Type: application/x-www-form-urlencoded"
```

- Follow a short code redirect:

```bash
curl -v "http://localhost:8000/s/abcd12/"
```

- Dashboard analytics (example):

```bash
curl "http://localhost:8000/u/analytics/123/" -H "Cookie: sessionid=..."
```

Notes: adjust paths to include `/u/` or `/a/` prefixes depending on whether you're calling app-namespaced routes.

**Development & Maintenance**
- Static build assets: see `theme/static_src/` for frontend build configuration (package.json, postcss). Use node/npm if rebuilding static assets.
- Background tasks/celery: `UrlShortner/celery.py` exists — check `Procfile` for worker configuration.
- Check scheduled tasks in `Auth/pipelines.py`, `Auth/tasks.py`, and `urlLogic/tasks.py` for background jobs.

**References & Source**
- Root URLs: [UrlShortner/UrlShortner/urls.py](UrlShortner/UrlShortner/urls.py#L1-L120)
- Auth routes: [UrlShortner/Auth/urls.py](UrlShortner/Auth/urls.py#L1-L120)
- URL logic routes: [UrlShortner/urlLogic/urls.py](UrlShortner/urlLogic/urls.py#L1-L140)
- Project README and structure: [README.md](README.md)

- OpenAPI spec: [openapi.yaml](openapi.yaml)

If you want, I can now:
- add concrete request/response examples for each endpoint by reading the corresponding view functions, or
- generate an OpenAPI/Swagger spec by scanning views and serializers.

---
Generated by assistant: concise API surface based on project routing files. For full request/response contracts I can parse view functions next.
