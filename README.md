# 🎧 MUS-HUB 🎶

**Empowering Eswatini's music creators through a dedicated digital platform.**

---

## 📌 About the Project

**MUS-HUB** is a collaborative music-sharing and networking platform built to empower artists, producers, and music enthusiasts—starting with the Kingdom of Eswatini. The platform helps musicians upload and showcase their work, connect with others, and receive feedback—all in a focused, community-driven environment.

Unlike global social platforms that dilute artistic content with unrelated distractions, MUS-HUB is **music-first**, designed to promote collaboration, discovery, and career development for artists.

---

## 🎯 Mission

> “To create job opportunities through the Arts, Culture & Design sector by empowering artists in Africa to realize their potential.”

---

## 🚨 Problem Statement

While Eswatini highly values its arts and culture, it lacks infrastructure and digital platforms that support musicians in turning their talent into a career. MUS-HUB addresses this by creating a dedicated space for music creators to collaborate, share their work, and grow together professionally.

---

## 🛠️ Tech Stack

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3 (Glassmorphic design)
- **Database:** SQLite (for now), scalable to MySQL/PostgreSQL
- **Hosting:** Gunicorn + Nginx (or local Flask dev server)
- **APIs:** RESTful (Flask routes)

---

## 🔑 Features

- 🎤 **User Registration & Login**
- 🧑‍🎤 **Profile Management** (bio, contact details, music links)
- ⬆️ **Audio/Video Uploads**
- 📰 **Latest Uploads Feed**
- 💬 **Commenting System**
- 🤝 **Collaboration Opportunities** (discover and contact other artists)
- 📱 **Responsive Design** for mobile and desktop

---

## 📸 Screenshots

### 🏠 Home Page
![Home Page 1](https://github.com/user-attachments/assets/573286b0-ff1e-417e-8df5-2200c9aac760)
![Home Page 2](https://github.com/user-attachments/assets/12cc0f57-e05c-466b-8ba2-851367893e42)

### 👤 Profile Page
![Profile Page](https://github.com/user-attachments/assets/14ae0954-2148-4bb4-822f-57ede6c98927)

### ⬆️ Upload Page
![Upload Page](https://github.com/user-attachments/assets/f62aad22-522f-4535-b95c-0e90b9ecc2a5)


---

## 🧪 Agile Development Model

The project follows an **Agile development process**:
1. **Planning** – Define goals and prioritize based on artist feedback.
2. **Design** – Wireframes and UI prototypes created with musicians in mind.
3. **Development** – Built in sprints using Python & Flask.
4. **Testing** – Features tested for usability and performance.
5. **Deployment** – Live via Gunicorn server with continuous iteration.
6. **Feedback Loop** – User feedback shapes future updates.

---

## 🚀 Getting Started

### Prerequisites

- Python 3.x
- Flask
- Virtualenv (recommended)

### Installation

```bash
git clone https://github.com/your-username/mus-hub.git
cd mus-hub
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
flask run

