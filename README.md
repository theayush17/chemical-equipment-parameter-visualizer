
# Chemical Equipment Parameter Visualizer

A hybrid system (Web + Desktop) for chemical equipment data analytics.

## Tech Stack
- **Backend**: Django, DRF, Pandas, SQLite, ReportLab
- **Web**: React 18, Tailwind CSS, Recharts
- **Desktop**: PyQt5, Matplotlib, Requests

## Setup Instructions

### 1. Backend Setup
```bash
cd backend
pip install -r requirements.txt
python manage.py makemigrations api
python manage.py migrate
# Create a superuser for Basic Auth
python manage.py createsuperuser --username admin --email admin@example.com
# Start server (default: localhost:8000)
python manage.py runserver
```

### 2. Web Frontend Setup
The web frontend is integrated into the root provided by this environment.
Ensure the backend is running at `http://localhost:8000`.
Open `index.html` in your browser.
*Note: In a standard local environment, you would use `npm install && npm start`.*

### 3. Desktop Frontend Setup
```bash
cd frontend-desktop
pip install -r requirements.txt
python app.py
```

## Demo Credentials
- **Username**: `admin`
- **Password**: `admin` (or whatever you set during `createsuperuser`)

## API Endpoints
- `POST /api/upload/`: Upload CSV and get real-time stats.
- `GET /api/history/`: Fetch last 5 upload summaries.
- `GET /api/report/<id>/`: Download PDF summary.

## Features
- **CSV Validation**: Checks for missing columns and empty files using Pandas.
- **Analytics**: Calculates averages and distribution of equipment types.
- **Persistence**: SQLite database stores JSON summaries; automatically rotates and keeps only the latest 5 datasets.
- **Reporting**: ReportLab generated PDFs for professional documentation.
- **Visualization**: Interactive charts on web and static plots on desktop.
