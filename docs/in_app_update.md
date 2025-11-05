# In-App Update System

This document describes how the Chaos Contained app notifies users about new versions and guides them to download updates from GitHub Releases.

## Overview

On app startup (and any time you manually trigger a check), the app queries the GitHub Releases API for the repository `Vicketh/chaos-contained`. If the `tag_name` of the latest release is greater than the current app version (from `package_info_plus`), the user is shown an "Update Available" dialog. Tapping "Update Now" opens the APK asset download URL in the device browser.

- API endpoint: `https://api.github.com/repos/Vicketh/chaos-contained/releases/latest`
- Version scheme: `vMAJOR.MINOR.PATCH` (Release tags). The app strips the leading `v` and compares semantic version numerically.
- Polling: Currently checked on first frame after app start.

## Implementation

### Flutter

File: `lib/services/update_service.dart`

- Fetches the latest release metadata from GitHub.
- Compares app version (from `package_info_plus`) with release `tag_name`.
- Finds an APK asset in the release and uses `url_launcher` to open its `browser_download_url`.
- Presents an AlertDialog with "Later" and "Update Now" actions.

Hooked in `lib/app.dart` using `WidgetsBinding.instance.addPostFrameCallback`.

### CI Workflow

Workflow: `.github/workflows/release.yml`

- Trigger: push a tag matching `v*`
- Steps:
  - Build release APK.
  - Create a GitHub Release and upload the APK.
  - Generate `latest_release.json` metadata and attach it to the same release (optional convenience artifact).

`latest_release.json` example:
```
{
  "tag_name": "v0.1.2",
  "published_at": "2025-02-01T12:00:00Z",
  "apk_asset_name": "app-release.apk"
}
```

The app reads directly from GitHub Releases API and does not require `latest_release.json`. The JSON is provided for external tooling or future enhancements.

## Testing

1. Bump version in `frontend/chaos_contained/pubspec.yaml` (e.g., `0.1.2+2`).
2. Commit and tag a release: `git tag -a v0.1.2 -m "Release v0.1.2" && git push origin v0.1.2`.
3. Wait for GitHub Actions to create the Release and upload the APK.
4. Install an older APK on a device/emulator and launch the app. You should see the update dialog.

## Considerations

- Rate limits: Unauthenticated GitHub API requests are rate-limited. If needed, we can add an authenticated request path or proxy through our backend.
- Android installation: Direct APK installation may require enabling installs from unknown sources. For Play Store distribution, integrate the Play In-App Updates API.
- iOS: iOS users will not use APKs; consider TestFlight or App Store updates.
