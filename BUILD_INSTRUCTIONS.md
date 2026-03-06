# Build Instructions for Vimshottari Android App

## Quick Start

### Option 1: Build with Android Studio (Recommended)

1. **Install Prerequisites:**
   ```bash
   # Install Android Studio from https://developer.android.com/studio
   # Install JDK 17
   sudo apt-get install openjdk-17-jdk  # Linux
   brew install openjdk@17               # macOS
   ```

2. **Open Project:**
   - Launch Android Studio
   - Select "Open an existing project"
   - Choose the `VimshottariApp` folder

3. **Update SDK Path:**
   - Open `local.properties`
   - Update `sdk.dir` to your Android SDK location

4. **Sync and Build:**
   - Click "Sync Now" in the notification bar
   - Select `Build > Build Bundle(s) / APK(s) > Build APK(s)`

5. **Find APK:**
   - Debug APK: `app/build/outputs/apk/debug/app-debug.apk`

### Option 2: Build from Command Line

1. **Set Environment Variables:**
   ```bash
   export ANDROID_SDK_ROOT=/path/to/android/sdk
   export JAVA_HOME=/path/to/jdk17
   ```

2. **Download Gradle Wrapper:**
   ```bash
   cd VimshottariApp
   
   # Download gradle wrapper jar
   mkdir -p gradle/wrapper
   curl -L -o gradle/wrapper/gradle-wrapper.jar \
     https://raw.githubusercontent.com/gradle/gradle/v8.5.0/gradle/wrapper/gradle-wrapper.jar
   ```

3. **Build Debug APK:**
   ```bash
   ./gradlew assembleDebug
   ```

4. **Build Release APK:**
   ```bash
   ./gradlew assembleRelease
   ```

## Detailed Setup

### Step 1: Install Android SDK

**Linux:**
```bash
# Download command line tools
mkdir -p ~/Android/Sdk/cmdline-tools
cd ~/Android/Sdk/cmdline-tools
wget https://dl.google.com/android/repository/commandlinetools-linux-11076708_latest.zip
unzip commandlinetools-linux-11076708_latest.zip
mv cmdline-tools latest

# Set environment
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_SDK_ROOT/cmdline-tools/latest/bin

# Install required packages
sdkmanager "platforms;android-34"
sdkmanager "build-tools;34.0.0"
sdkmanager "platform-tools"
```

**macOS:**
```bash
# Using Homebrew
brew install android-sdk

# Or download from Android Studio website
```

**Windows:**
- Download Android Studio from https://developer.android.com/studio
- Install with default settings

### Step 2: Configure local.properties

Create or edit `local.properties`:

```properties
# Linux/macOS
sdk.dir=/home/username/Android/Sdk
ndk.dir=/home/username/Android/Sdk/ndk/25.2.9519653

# Windows
sdk.dir=C:\\Users\\username\\AppData\\Local\\Android\\Sdk
ndk.dir=C:\\Users\\username\\AppData\\Local\\Android\\Sdk\\ndk\\25.2.9519653
```

### Step 3: Install NDK (Required for Chaquopy)

```bash
sdkmanager "ndk;25.2.9519653"
```

### Step 4: Build the Project

```bash
# Make gradlew executable (Linux/macOS)
chmod +x gradlew

# Build debug APK
./gradlew assembleDebug

# Build release APK (requires signing config)
./gradlew assembleRelease
```

## Build Variants

### Debug Build
```bash
./gradlew assembleDebug
```
- Output: `app/build/outputs/apk/debug/app-debug.apk`
- Debug symbols included
- No code optimization
- Larger file size

### Release Build
```bash
./gradlew assembleRelease
```
- Output: `app/build/outputs/apk/release/app-release-unsigned.apk`
- Code optimized and obfuscated
- Requires signing for installation

## Signing the Release APK

1. **Generate Keystore:**
   ```bash
   keytool -genkey -v -keystore vimshottari.keystore \
     -alias vimshottari -keyalg RSA -keysize 2048 -validity 10000
   ```

2. **Configure Signing:**
   Add to `app/build.gradle`:
   ```gradle
   android {
       signingConfigs {
           release {
               storeFile file("vimshottari.keystore")
               storePassword "your_password"
               keyAlias "vimshottari"
               keyPassword "your_password"
           }
       }
       buildTypes {
           release {
               signingConfig signingConfigs.release
           }
       }
   }
   ```

3. **Build Signed APK:**
   ```bash
   ./gradlew assembleRelease
   ```

## Troubleshooting

### Error: "SDK location not found"
**Solution:** Update `local.properties` with correct SDK path

### Error: "Could not find com.chaquo.python:gradle"
**Solution:** Ensure Chaquopy repository is in `settings.gradle`:
```gradle
maven { url "https://chaquo.com/maven" }
```

### Error: "Python build failed"
**Solution:** 
- Check Python 3.11 is installed
- Verify `buildPython` path in `app/build.gradle`

### Error: "NDK not found"
**Solution:** Install NDK via SDK Manager:
```bash
sdkmanager "ndk;25.2.9519653"
```

### Build takes too long
**Solution:** 
- First build downloads Python packages (normal)
- Subsequent builds are faster
- Use `./gradlew --daemon` for faster builds

## Verification

After building, verify the APK:

```bash
# Check APK contents
unzip -l app/build/outputs/apk/debug/app-debug.apk | head -30

# Check file size
ls -lh app/build/outputs/apk/debug/app-debug.apk

# Install and test
adb install app/build/outputs/apk/debug/app-debug.apk
```

## Expected Build Times

- **First build:** 10-20 minutes (downloads dependencies)
- **Subsequent builds:** 2-5 minutes
- **Clean build:** 5-10 minutes

## Output Files

After successful build:

```
app/build/outputs/apk/
├── debug/
│   ├── app-debug.apk           # Debug APK
│   └── output-metadata.json
└── release/
    ├── app-release-unsigned.apk # Unsigned release APK
    └── output-metadata.json
```

## Next Steps

1. **Test on device:** Install the debug APK on an Android device
2. **Verify functionality:** Test all features match the web app
3. **Sign for distribution:** Create signed release APK for distribution
