
# URL.ly - Django URL Shortener

A modern, full-featured URL shortener built with **Django**, **TailwindCSS**, and **JavaScript**. URL.ly lets you shorten links, track analytics, manage user accounts, and more — all with a clean, responsive UI.

## Features

- Shorten long URLs instantly
- Track click analytics for each short URL
- Generate QR codes for every shortened link
- User authentication (signup, login, password reset)
- Upload and manage profile pictures
- Secure password reset via email
- User dashboard for managing links (coming soon)
- Branded/custom domain links (coming soon)

## Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, TailwindCSS, JavaScript
- **Database:** SQLite (default, easy to switch)

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

### Auth App

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

### urlLogic App

- `/u/` — Home (dashboard)
- `/u/ShortenUrl/` — Shorten a URL
- `/u/generate_qr/` — Generate QR code
- `/u/delete/<int:id>/` — Delete a short URL
- `/u/update_url/<int:id>/` — Update a short URL
- `/u/<str:slug>/` — Redirect to original URL

### Biolink App & Project-level

- `/my-bio-link-page/` — Redirect to your biolink page
- `/biolink-page/<uuid:id>/` — View your biolink links
- `/addlink/<uuid:id>/` — Add a link to your biolink
- `/deletelink/<uuid:id>/` — Delete a link from your biolink
- `/editprofile/` — Edit your biolink profile
- `/enable/` — Enable public biolink
- `/p/<slug:slug>/` — Public biolink by slug
- `/u/<uuid:public_id>/` — Public biolink by UUID

> **Note:** Some endpoints require authentication (login/session). For more details, see the code or API docs.

---

## Project Structure

The full project tree is long and lives in a separate file to keep this README concise.

See the complete structure in: `STRUCTURE.md`

---

## Contributions

Pull requests and feedback are welcome! Feel free to fork the repo and submit improvements or report issues.
