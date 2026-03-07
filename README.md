# Vimshottari Dasha - Android Application

## Overview

This is the Android conversion of the WEB-VIM Python web application. The app embeds a complete Flask server with Python astronomical calculations (using Swiss Ephemeris) inside an Android application using Chaquopy Python runtime.

## Features

- **Complete Vimshottari Dasha calculations** - Birth chart analysis with planetary positions
- **Chakra calculations** - Sapt Nadi, Mandal, and Duar calculations
- **Live planetary positions** - Real-time planet tracking with GPS support
- **PDF generation** - Download full cycle dasha reports
- **Offline functionality** - Works without internet for local calculations
- **WebView interface** - Identical UI to the original web application

## Architecture

```
Android App (Kotlin)
    ↓
Chaquopy Python Runtime
    ↓
Flask Server (Embedded)
    ↓
Swiss Ephemeris (pyswisseph)
    ↓
HTML Templates + JavaScript (WebView)
```

## Project Structure

```
VimshottariApp/
├── app/
│   ├── src/main/
│   │   ├── java/com/vimshottari/app/
│   │   │   ├── MainActivity.kt          # Main Android activity with WebView
│   │   │   └── VimshottariApplication.kt # Application class with Python init
│   │   ├── python/
│   │   │   ├── flask_server.py          # Python server wrapper
│   │   │   └── server/                  # Original Flask application
│   │   │       ├── app.py               # Flask app entry point
│   │   │       ├── apps/                # App modules
│   │   │       └── modules/             # Calculation modules
│   │   ├── assets/server/client/        # Templates and static files
│   │   └── res/                         # Android resources
│   └── build.gradle                     # App-level build config with Chaquopy
├── build.gradle                         # Project-level build config
├── settings.gradle
├── gradle.properties
└── local.properties                     # SDK paths (update this)
```

## Prerequisites

1. **Android Studio** - Latest stable version (Hedgehog or newer)
2. **Android SDK** - API 34, minimum API 29
3. **JDK** - Version 17 or newer
4. **Python** - Version 3.11 (for Chaquopy)

## Build Instructions

### Step 1: Update SDK Path

Edit `local.properties` and update the SDK path:

```properties
sdk.dir=/path/to/your/Android/Sdk
ndk.dir=/path/to/your/Android/Sdk/ndk/25.2.9519653
```

### Step 2: Sync Project

Open the project in Android Studio and sync:

```bash
# Or from command line:
./gradlew sync
```

### Step 3: Build APK

```bash
# Debug APK
./gradlew assembleDebug

# Release APK
./gradlew assembleRelease
```

The APK will be generated at:
- Debug: `app/build/outputs/apk/debug/app-debug.apk`
- Release: `app/build/outputs/apk/release/app-release-unsigned.apk`

### Step 4: Install

```bash
# Install debug APK
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Key Dependencies

### Android (Kotlin)
- AndroidX Core KTX
- AppCompat
- Material Design
- ConstraintLayout
- WebKit
- SwipeRefreshLayout

### Python (via Chaquopy)
- Flask 3.0.0
- Jinja2 3.1.2
- swisseph 2.10.3.2 (Swiss Ephemeris)
- fpdf 1.7.2

## Configuration

### Python Packages

Python packages are configured in `app/build.gradle`:

```gradle
python {
    pip {
        install "Flask==3.0.0"
        install "swisseph==2.10.3.2"
        install "fpdf==1.7.2"
        // ... other packages
    }
}
```

### Server Port

The Flask server runs on port 8080 by default. To change:

1. Edit `MainActivity.kt`:
   ```kotlin
   private const val SERVER_PORT = 8080
   ```

2. Update `flask_server.py` accordingly.

## Permissions

The app requires these permissions:

- `INTERNET` - For live planetary data
- `ACCESS_FINE_LOCATION` - For GPS coordinates
- `ACCESS_COARSE_LOCATION` - For approximate location
- `WRITE_EXTERNAL_STORAGE` - For PDF downloads (Android 9 and below)

## Login Credentials

Default login credentials (same as original web app):
- **Username:** Prakash
- **Password:** 12345

## Routes

The following routes are available:

| Route | Description |
|-------|-------------|
| `/` | Login page |
| `/page1` - `/page15` | Content pages |
| `/infinite-vimshottari` | Main dasha calculator |
| `/api/live-planets` | Live planetary positions API |
| `/calculate-chakras` | Chakra calculation API |
| `/receive-gps` | GPS data receiver |
| `/download-full-cycle-pdf` | PDF download endpoint |
| `/article/<filename>` | Article viewer |

## Offline Functionality

The app works offline for:
- All template rendering
- Dasha calculations
- Chakra calculations
- Page navigation
- PDF generation

Internet is only required for:
- Live planetary position updates
- GPS coordinate acquisition

## Troubleshooting

### Build Errors

1. **Chaquopy not found:**
   - Ensure `maven { url "https://chaquo.com/maven" }` is in repositories

2. **Python packages fail to install:**
   - Check `buildPython` path in `app/build.gradle`
   - Ensure Python 3.11 is installed

3. **SDK not found:**
   - Update `local.properties` with correct SDK path

### Runtime Errors

1. **Server not starting:**
   - Check logcat for Python errors
   - Verify all Python files are in `src/main/python/server/`

2. **Templates not found:**
   - Ensure templates are in `src/main/assets/server/client/templates/`

3. **WebView shows blank page:**
   - Check that server is running on correct port
   - Verify `usesCleartextTraffic="true"` in AndroidManifest.xml

## Performance Notes

- **Startup time:** 5-10 seconds (Python runtime initialization)
- **Memory usage:** ~150-200 MB (includes Python runtime)
- **APK size:** ~50-80 MB (includes Python libraries and Swiss Ephemeris data)

## Compatibility

- **Minimum Android:** 10 (API 29)
- **Target Android:** 14 (API 34)
- **Architectures:** arm64-v8a, armeabi-v7a, x86_64

## Original Project

This Android app is a conversion of the WEB-VIM project:
- Original: Python Flask web application
- Conversion: Android app with embedded Python runtime
- UI: Preserved exactly via WebView

## License

Same as original WEB-VIM project.

## Support

For issues related to:
- **Android app:** Check this README and build instructions
- **Calculations:** Refer to original WEB-VIM documentation
- **Chaquopy:** Visit https://chaquo.com/chaquopy/doc/
