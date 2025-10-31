# Chaos Contained

An ADHD-friendly task management and routine-building mobile app that helps users maintain consistent daily routines, manage time consciously, and stay motivated without anxiety or burnout.

## Features

- 🎯 Smart task management with AI-powered scheduling
- 🎵 Focus mode with music integration (Spotify, YouTube Music, Apple Music)
- 🔔 Adaptive notifications and voice reminders
- 📊 Progress tracking and insights
- 🤖 AI-powered motivational assistant
- 🌙 Dark mode support
- 📱 Cross-platform (iOS & Android)

## Tech Stack

- Frontend: Flutter
- Backend: Django REST Framework
- Database: PostgreSQL
- AI: OpenAI GPT API
- Auth: JWT
- Notifications: Firebase Cloud Messaging
- CI/CD: GitHub Actions

## Getting Started

### Prerequisites

- Python 3.8+
- Flutter 3.0+
- PostgreSQL 13+
- Node.js 16+ (for development tools)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Frontend Setup

```bash
cd frontend
flutter pub get
flutter run
```

## Documentation

- [API Reference](docs/API_REFERENCE.md)
- [Installation Guide](docs/INSTALLATION_GUIDE.md)
- [UX Guidelines](docs/UX_GUIDELINES.md)

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please read our [Contributing Guidelines](CONTRIBUTING.md) first.