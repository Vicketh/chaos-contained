DoChaos Contained - Flutter frontend

This folder contains the Flutter mobile app for Chaos Contained.

Quick start (local):

1. Install Flutter (https://flutter.dev/docs/get-started/install).
2. From this folder run:

```bash
flutter pub get
flutter run
```

Notes for deployment:
- Android: build an APK/AAB with `flutter build apk --release` or `flutter build appbundle --release`.
- iOS: build from macOS with Xcode or use CI to produce an archive for TestFlight.

Environment & services:
- Backend API base URL: set at build/run time using `--dart-define=API_BASE_URL="https://api.yourdomain.com/api/v1"`.
- Firebase: configure Firebase for Android & iOS and generate `google-services.json` / `GoogleService-Info.plist`.
- Music APIs: register apps with Spotify/YouTube Music/Apple Music and store client keys in your CI/CD secrets or backend.

CI/CD:
- A GitHub Actions workflow is included `.github/workflows/flutter.yml` to run analyze/tests and build an Android APK.

Design & UX:
- Uses pastel color palette and Google Fonts (Poppins/Nunito via google_fonts).
- Focus on minimal UI, rounded cards, and low-friction interactions.

Next steps:
- Run `flutter pub get` locally.
- Wire Firebase and backend URL.
- Implement deeper screens and integrate auth flows.
