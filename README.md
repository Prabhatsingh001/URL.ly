
# 🔗 URL.ly - Django URL Shortener

A modern, full-featured URL shortener built with **Django**, **TailwindCSS**, and **JavaScript**. URL.ly lets you shorten links, track analytics, manage user accounts, and more—all with a clean, responsive UI.

## 🚀 Features

- 🔗 Shorten long URLs instantly
- 📊 Track click analytics for each short URL
- 📸 Generate QR codes for every shortened link
- 👤 User authentication (signup, login, password reset)
- 🖼️ Upload and manage profile pictures
- 🛡️ Secure password reset via email
- � User dashboard for managing links (coming soon)
- 🌐 Branded/custom domain links (coming soon)

## 🧰 Tech Stack

- **Backend:** Django (Python)
- **Frontend:** HTML, TailwindCSS, JavaScript
- **Database:** SQLite (default, easy to switch)

## 🌍 Live Demo

Try the app live: [https://url-ly.onrender.com/](https://url-ly.onrender.com/)

## 🛠️ Getting Started (Local Setup)

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

## 📦 API Endpoints

The project exposes several API endpoints for core functionality. Here are some of the main endpoints:

| Endpoint                        | Method | Description                                 |
|----------------------------------|--------|---------------------------------------------|
| `/api/shorten/`                 | POST   | Shorten a long URL                          |
| `/api/expand/`                  | POST   | Expand a short URL to its original form     |
| `/api/analytics/<short_code>/`  | GET    | Get analytics for a specific short URL      |
| `/api/user/register/`           | POST   | Register a new user                         |
| `/api/user/login/`              | POST   | User login                                  |
| `/api/user/logout/`             | POST   | User logout                                 |
| `/api/user/profile/`            | GET    | Get user profile info                       |
| `/api/user/update/`             | POST   | Update user profile                         |
| `/api/user/change-password/`    | POST   | Change user password                        |
| `/api/user/reset-password/`     | POST   | Request password reset email                |
| `/api/user/reset-password/<uidb64>/<token>/` | POST | Reset password using token         |

> **Note:** Some endpoints may require authentication (token/session). For more details, see the code or API docs.

---

## 📂 Project Structure

<details>
<summary>Click to view the basic structure</summary>

```text
UrlShortner/
├── Auth/                  # User authentication app
├── Biolink/               # Biolink (profile/landing page) app
├── urlLogic/              # URL shortening and analytics logic
├── static/                # Static files (CSS, JS, images)
├── templates/             # HTML templates
├── manage.py
├── requirements.txt
└── ...
```
</details>

---

## 💡 Contributions

Pull requests and feedback are welcome! Feel free to fork the repo and submit improvements or report issues.
