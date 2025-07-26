# 🔗 URL Shortener Project

A sleek and simple URL shortener built using **Django**, **TailwindCSS**, and **JavaScript**.

## 🚀 Features

- 🔗 Shorten long URLs with ease  
- 📊 Track the number of clicks  
- 📸 Generate QR codes for shortened URLs  
- 🖼️ Custom brand logo on QR codes (**coming soon**)  
- 📈 User dashboard with analytics (**coming soon**)  
- 🌐 Branded/custom domain links (**coming soon**)  

## 🧰 Tech Stack

- **Backend**: Django  
- **Frontend**: HTML, TailwindCSS, JavaScript  

## 🌍 Live Demo

Check out the deployed version here:  
🔗 [https://url-ly.onrender.com/](https://url-ly.onrender.com/)

## 🛠️ Getting Started (Local Setup)

Follow these steps to set up the project on your local machine:

### 1. Clone the Repository

```bash
git clone https://github.com/Prabhatsingh001/URL-SHORTNER.git
cd UrlShortner
```

### 2. Create & Activate Virtual Environment

Make sure you have Python 3.10 installed:

```bash
python3.10 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4.Apply migrations

```bash
python manage.py migrate
```

### 5.Run the Development Server

```bash
python manage.py runserver
```

## Note:-

After cloning the repo chnage the debug to True in settings.py file

# 📂 Project Structure

<details>
<summary>Click to view the basic structure</summary>

```text
URL-SHORTNER/
├── Auth/                  # User authentication app
├── urlLogic/              # URL handling logic (shortening, tracking, etc.)
├── static/                # Static files (CSS, JS)
├── templates/             # HTML templates
├── manage.py
├── requirements.txt
└── ...
```
</details>

# 💡Contributions

Pull requests and feedback are welcome! Feel free to fork the repo and submit improvements or report issues.
