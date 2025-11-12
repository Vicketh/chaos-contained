# Android APK Build Guide for Chaos Contained

This guide provides the steps to build an Android APK from the existing Flutter web project.

## 1. Prerequisites

- You must have the Flutter SDK installed on your local machine.
- You must have the Android SDK installed and configured. You can check your setup by running `flutter doctor`.

## 2. Add Android Platform to the Project

The current project is configured for Flutter Web. To build an Android APK, you need to add the Android platform to the project.

Open your terminal in the `frontend/chaos_contained` directory and run the following command:

```bash
flutter create .
```

This command will create the `android` directory and other necessary files without overwriting your existing Dart code.

## 3. Get Dependencies

After adding the Android platform, you need to get all the Flutter dependencies. Run the following command:

```bash
flutter pub get
```

## 4. Configure Signing for Release Build

To build a release APK, you need to sign it.

### 4.1. Create a Keystore

If you don't have a keystore, you can create one using the following command:

```bash
keytool -genkey -v -keystore ~/keystore.jks -keyalg RSA -keysize 2048 -validity 10000 -alias chaos-contained
```

This will create a file named `keystore.jks` in your home directory. You will be prompted to enter a password and other information. Remember the password.

### 4.2. Create `key.properties` file

Create a file named `key.properties` in the `frontend/chaos_contained/android` directory with the following content:

```
storePassword=<your_store_password>
keyPassword=<your_key_password>
keyAlias=chaos-contained
storeFile=/path/to/your/keystore.jks
```

Replace `<your_store_password>` and `<your_key_password>` with the passwords you set in the previous step, and `/path/to/your/keystore.jks` with the actual path to your keystore file.

### 4.3. Configure Gradle

Open the `frontend/chaos_contained/android/app/build.gradle` file and add the following code before the `android` block:

```groovy
def keystoreProperties = new Properties()
def keystorePropertiesFile = rootProject.file('key.properties')
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))
}
```

Then, inside the `android` block, add the following `signingConfigs` block:

```groovy
android {
    ...
    signingConfigs {
        release {
            if (keystoreProperties.getProperty('storeFile') != null) {
                storeFile file(keystoreProperties.getProperty('storeFile'))
                storePassword keystoreProperties.getProperty('storePassword')
                keyAlias keystoreProperties.getProperty('keyAlias')
                keyPassword keystoreProperties.getProperty('keyPassword')
            }
        }
    }
    buildTypes {
        release {
            ...
            signingConfig signingConfigs.release
        }
    }
}
```

## 5. Build the APK

Now you are ready to build the APK. Run the following command:

```bash
flutter build apk --release
```

The APK will be generated at `frontend/chaos_contained/build/app/outputs/flutter-apk/app-release.apk`.

## 6. Automated Build Script

An automated build script `build_apk.sh` is provided to simplify this process. You can run it from the `frontend/chaos_contained` directory:

```bash
bash build_apk.sh
```

This script will guide you through the process, and will automatically generate a keystore if you don't have one.
