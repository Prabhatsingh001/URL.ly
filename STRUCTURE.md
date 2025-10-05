# Project Structure (full)

This file contains the exact project tree for the repository. It was moved out of the README to keep the README concise and avoid large embedded sections.

```text
UrlShortner/
├── db.sqlite3
├── manage.py
├── Procfile
├── requirements.txt
├── Auth/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── mail.py
│   ├── models.py
│   ├── pipelines.py
│   ├── signals.py
│   ├── tasks.py
│   ├── tests.py
│   ├── tokens.py
│   ├── urls.py
│   ├── views.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   └── templates/
│       ├── about.html
│       ├── contact.html
│       ├── forgot_password.html
│       ├── index.html
│       ├── login.html
│       ├── profile_layout.html
│       ├── profile_setting.html
│       ├── profile_update_password.html
│       ├── profile.html
│       ├── resend_verification_email.html
│       ├── reset_password.html
│       └── signup.html
├── Biolink/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── signals.py
│   ├── tests.py
│   ├── views.py
│   ├── migrations/
│   │   ├── __init__.py
│   │   ├── 0001_initial.py
│   │   └── 0002_remove_link_user_alter_link_profile.py
│   └── templates/
│       ├── mainpage.html
│       └── public_page.html
├── Brandlink/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   ├── views.py
│   └── migrations/
│       ├── __init__.py
│       └── __pycache__/
├── static/
│   ├── 404.jpg
│   ├── dribbble_1.gif
│   ├── logo.png
│   ├── profile_image.png
│   ├── signin-image.webp
│   ├── signup.jpg
│   ├── backgrounds/
│   │   └── 404_bg.jpg
│   └── icons/
│       ├── editprofile.svg
│       ├── edittext.svg
│       ├── github.svg
│       ├── instagram.svg
│       ├── link.svg
│       └── twitter.svg
├── templates/
│   ├── alert.html
│   ├── footer.html
│   ├── layout.html
│   └── navbar.html
├── theme/
│   ├── __init__.py
│   ├── apps.py
│   ├── __pycache__/
│   ├── static/
│   └── static_src/
│       └── templates/
├── urlLogic/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── signals.py
│   ├── tasks.py
│   ├── tests.py
│   ├── urls.py
│   ├── utils.py
│   ├── views.py
│   ├── migrations/
│   └── templates/
│       ├── 404_notF.html
│       ├── components/
│       │   └── url_card.html
│       ├── email/
│       ├── home.html
│       ├── server_500.html
│       ├── update_edit_url.html
│       └── url_shortner.html
└── UrlShortner/
    ├── __init__.py
    ├── asgi.py
    ├── celery.py
    ├── settings.py
    ├── urls.py
    └── wsgi.py

```

If you'd like, I can also generate a shortened tree (only top-level folders) for quick reference and keep this full tree in `STRUCTURE.md`.
