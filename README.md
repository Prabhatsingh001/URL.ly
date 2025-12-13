
# URL.ly - Django URL Shortener & Bio Link Platform

A comprehensive platform built with **Django**, **TailwindCSS**, and **JavaScript**. URL.ly combines powerful URL shortening with bio link pages, analytics, and user management — all with a modern, responsive UI.

## Features

### URL Shortening

- Instant URL shortening with custom slug options
- Comprehensive click analytics and visitor tracking
- QR code generation with branded overlay
- Email delivery of QR codes
- Link expiration management
- Anonymous URL shortening with rate limiting

### Bio Link Pages

- Customizable profile pages for multiple links
- Public/private link toggle
- Custom profile slugs
- Profile image upload with automatic optimization
- Rich analytics for link clicks
- Mobile-responsive layouts

### User Features

- Email-based authentication
- Google OAuth2 integration
- Profile management with avatar support
- Secure password reset system
- Email verification
- Contact form with admin notifications

### Analytics & Tracking

- Geolocation tracking
- Device and browser detection
- Bot detection
- Referrer tracking
- Visit timestamps
- Click counting

### Security & Performance

- Rate limiting on API endpoints
- CSRF protection
- Secure password handling
- CDN-based asset delivery
- Mobile-first responsive design
- XSS protection
- SQL injection prevention
- Automated backup system

## Tech Stack

### Backend

- **Framework:** Django (Python)
- **Task Queue:** Celery with Redis
- **Database:** PostgreSQL (production), SQLite (development)
- **Storage:** Cloudinary for media files
- **Authentication:** Django + Social Auth

### Frontend

- **Styling:** TailwindCSS
- **Interactivity:** JavaScript
- **Templates:** Django Templates
- **Image Processing:** PIL/Pillow

### External Services

- **Email:** SMTP Integration
- **Media Storage:** Cloudinary CDN
- **Geolocation:** MaxMind GeoIP2
- **OAuth:** Google Authentication

## Live Demo

Try the app live: [https://url-ly.onrender.com/](https://url-ly.onrender.com/)

## Getting Started (Local Setup)

Follow these steps to set up the project locally:

### 1. Clone the Repository

```bash
git clone https://github.com/Prabhatsingh001/URL-SHORTNER.git
cd UrlShortner
```

### 2. Create & Activate Virtual Environment

Make sure you have Python 3.10+ installed.

```bash
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py migrate
```

### 5. Run the Development Server

```bash
python manage.py runserver
```

**Note:**
After cloning, set `DEBUG = True` in `UrlShortner/settings.py` for local development.

---

## Exposed URLs & Endpoints

Below are all the main URLs exposed by the project, grouped by app/module:

### Core Routes

- `/` — Main landing page
- `/admin/` — Admin interface
- `/auth/` — Social authentication endpoints
- `/s/<str:short_code>/` — Anonymous short URL redirects
- `/s/` — Anonymous URL shortening

### Auth App (`/a/`)

- `/a/about/` — About page
- `/a/contact/` — Contact page
- `/a/signup/` — User signup
- `/a/login/` — User login
- `/a/logout/` — User logout
- `/a/profile/<uuid:id>/` — User profile
- `/a/profile-edit/<uuid:id>/` — Edit profile
- `/a/profile-password/<uuid:id>/` — Change password
- `/a/activate/<uidb64>/<token>/` — Activate account
- `/a/forgot_password/` — Forgot password
- `/a/reset_password/<uidb64>/<token>/` — Reset password
- `/a/resend-verification/<str:email>/` — Resend verification email

### URL Management (`/u/`)

- `/u/` — User dashboard
- `/u/shortenurl/` — Create new short URL
- `/u/generateqr/` — Generate QR code
- `/u/delete/<int:id>/` — Delete URL
- `/u/updateurl/<int:id>/` — Update URL settings
- `/u/<str:slug>/` — URL redirect
- `/u/downloadqr/<int:id>/` — Download QR code
- `/u/mailqr/<int:id>/` — Email QR code

### Biolink Features

- `/my-bio-link-page/` — Your biolink page
- `/biolink-page/<uuid:id>/` — View biolink links
- `/addlink/<uuid:id>/` — Add biolink
- `/deletelink/<uuid:id>/` — Remove biolink
- `/editprofile/<uuid:id>/` — Edit biolink profile
- `/enable/` — Toggle public access
- `/p/<slug:slug>/` — Public biolink (slug)

### Development (Debug Mode Only)

- `/__reload__/` — Browser auto-reload
- `/static/` — Static files serving

> **Note:** Most endpoints require authentication. Error pages (404, 500, 403) are handled by custom views. Static file serving is only enabled in development mode.
Some endpoints require authentication (login/session). For more details, see the code or API docs.

---

## Project Structure

The full project tree is long and lives in a separate file to keep this README concise.

See the complete structure in: `STRUCTURE.md`

---

## Contributions

Pull requests and feedback are welcome! Feel free to fork the repo and submit improvements or report issues.
