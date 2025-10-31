# Installation Guide

## Development Environment Setup

### Prerequisites

1. Install Python 3.8+
2. Install Flutter 3.0+
3. Install PostgreSQL 13+
4. Install Node.js 16+ (for development tools)
5. Install Git

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chaos-contained.git
cd chaos-contained
```

2. Set up Python virtual environment:
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run migrations:
```bash
python manage.py migrate
```

6. Start the development server:
```bash
python manage.py runserver
```

### Frontend Setup

1. Install Flutter dependencies:
```bash
cd frontend
flutter pub get
```

2. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Run the app:
```bash
flutter run
```

## Production Deployment

### Backend Deployment (Railway/Render)

1. Create a new project on Railway/Render
2. Connect your GitHub repository
3. Set environment variables
4. Deploy the backend

### Frontend Deployment

1. Build the Flutter app:
```bash
flutter build apk --release  # For Android
flutter build ios --release  # For iOS
```

2. Submit to app stores following their respective guidelines

## Common Issues and Solutions

### Backend Issues

- Database connection errors: Check PostgreSQL credentials
- Migration errors: Try resetting migrations
- Permission issues: Check file permissions

### Frontend Issues

- Build errors: Update Flutter and dependencies
- API connection issues: Verify backend URL
- Platform-specific issues: Check platform requirements