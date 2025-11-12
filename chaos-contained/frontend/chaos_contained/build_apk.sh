#!/bin/bash

# This script automates the process of building a release APK for the Chaos Contained app.
# It assumes that you have already run `flutter create .` to generate the android directory.

set -e

# Function to add signing configuration to build.gradle
add_signing_config() {
  echo "Adding signing configuration to android/app/build.gradle..."
  if ! grep -q "signingConfigs" android/app/build.gradle; then
    sed -i "/android {/a \
    signingConfigs {\\
        release {\\
            if (keystoreProperties.getProperty('storeFile') != null) {\\
                storeFile file(keystoreProperties.getProperty('storeFile'))\\
                storePassword keystoreProperties.getProperty('storePassword')\\
                keyAlias keystoreProperties.getProperty('keyAlias')\\
                keyPassword keystoreProperties.getProperty('keyPassword')\\
            }\\
        }\\
    }\\
" android/app/build.gradle

    sed -i "/buildTypes {/a \
        release {\\
            signingConfig signingConfigs.release\\
        }\\
" android/app/build.gradle

    sed -i "/android {/i \
def keystoreProperties = new Properties()\\
def keystorePropertiesFile = rootProject.file('key.properties')\\
if (keystorePropertiesFile.exists()) {\\
    keystoreProperties.load(new FileInputStream(keystorePropertiesFile))\\
}\\
" android/app/build.gradle
  fi
}

# 1. Check for android directory
if [ ! -d "android" ]; then
  echo "Android directory not found. Please run 'flutter create .' in this directory first."
  exit 1
fi

# 2. Get dependencies
echo "Running 'flutter pub get'..."
flutter pub get

# 3. Check for key.properties
if [ ! -f "android/key.properties" ]; then
  echo "key.properties not found. A new keystore will be generated."

  # Generate keystore
  KEYSTORE_PATH="$HOME/keystore.jks"
  echo "Generating keystore at $KEYSTORE_PATH..."
  keytool -genkey -v -keystore "$KEYSTORE_PATH" -keyalg RSA -keysize 2048 -validity 10000 -alias chaos-contained -dname "CN=Chaos Contained, OU=Development, O=Chaos, L=Chaos, S=Chaos, C=XX" -storepass password -keypass password

  # Create key.properties
  echo "Creating android/key.properties..."
  echo "storePassword=password" > android/key.properties
  echo "keyPassword=password" >> android/key.properties
  echo "keyAlias=chaos-contained" >> android/key.properties
  echo "storeFile=$KEYSTORE_PATH" >> android/key.properties
fi

# 4. Add signing config to build.gradle
add_signing_config

# 5. Build APK
echo "Running 'flutter build apk --release'..."
flutter build apk --release

echo "Build complete! The APK can be found at build/app/outputs/flutter-apk/app-release.apk"
