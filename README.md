# Verte - AI Recycling Assistant

Verte is an AI-powered recycling assistant that makes waste sorting simple and engaging. By using a TensorFlow image classification model based on MobileNetV2, the application identifies everyday waste items from a live camera feed or uploaded image and classifies them into the correct disposal category: **Recycling**, **Compost**, or **Landfill**.

Beyond classification, Verte encourages sustainable habits through a gamified experience. Users can create an account or continue as a guest, earn XP for correctly sorting waste, maintain daily streaks, and monitor their environmental impact through a personal dashboard.

## Features

- AI-powered waste classification using TensorFlow and MobileNetV2
- Supports camera capture and image uploads
- Categorizes waste into Recycling, Compost, and Landfill
- XP and streak system to encourage consistent recycling habits
- User accounts with guest access support
- Personal dashboard for tracking progress and sorting history
- Responsive web interface built with HTML, CSS, and JavaScript
- SQLite database for user accounts, scan history, and statistics

## Technology Stack

**Frontend**
- HTML
- CSS
- JavaScript

**Backend**
- Python
- Flask

**AI**
- TensorFlow
- MobileNetV2

**Database**
- SQLite

## Project Structure

```text
verte/
├── backend/
│   ├── app.py
│   └── database/
├── frontend/
│   ├── index.html
│   ├── dashboard.html
│   ├── auth.html
│   ├── css/
│   ├── js/
│   └── assets/
├── ai_model/
│   ├── models/
│   ├── scripts/
│   ├── utils/
│   └── results/
├── requirements.txt
├── .gitignore
└── README.md
```

## Running the Project

The application runs on Python **3.11** or **3.12**, as TensorFlow currently has limited support for newer Python versions on Windows.

After installing the dependencies from `requirements.txt`, start the Flask server:

```bash
python backend/app.py
```

The application will be available at:

```
http://localhost:5000
```

## Deployment

Verte can be deployed on platforms such as Render using Gunicorn as the production server.

**Build Command**

```bash
pip install -r requirements.txt && python backend/database/init_db.py
```

**Start Command**

```bash
cd backend && gunicorn app:app
```

The application automatically uses the `PORT` environment variable provided by the hosting platform.