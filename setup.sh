#!/bin/bash
# Setup script for Vimshottari Android App
# This script downloads the Gradle wrapper and sets up the project

set -e

echo "Setting up Vimshottari Android App..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're in the right directory
if [ ! -f "settings.gradle" ]; then
    print_error "Please run this script from the VimshottariApp directory"
    exit 1
fi

# Create gradle wrapper directory
print_info "Creating gradle wrapper directory..."
mkdir -p gradle/wrapper

# Download gradle wrapper jar
GRADLE_WRAPPER_URL="https://raw.githubusercontent.com/gradle/gradle/v8.5.0/gradle/wrapper/gradle-wrapper.jar"
GRADLE_WRAPPER_JAR="gradle/wrapper/gradle-wrapper.jar"

if [ -f "$GRADLE_WRAPPER_JAR" ]; then
    print_warn "Gradle wrapper already exists, skipping download"
else
    print_info "Downloading Gradle wrapper..."
    if command -v curl &> /dev/null; then
        curl -L -o "$GRADLE_WRAPPER_JAR" "$GRADLE_WRAPPER_URL"
    elif command -v wget &> /dev/null; then
        wget -O "$GRADLE_WRAPPER_JAR" "$GRADLE_WRAPPER_URL"
    else
        print_error "Neither curl nor wget found. Please install one of them."
        exit 1
    fi
    print_info "Gradle wrapper downloaded successfully"
fi

# Make gradlew executable
print_info "Making gradlew executable..."
chmod +x gradlew

# Check for Android SDK
if [ -z "$ANDROID_SDK_ROOT" ] && [ -z "$ANDROID_HOME" ]; then
    print_warn "ANDROID_SDK_ROOT or ANDROID_HOME not set"
    print_warn "Please set one of these environment variables or update local.properties"
    
    # Try to find common SDK locations
    COMMON_PATHS=(
        "$HOME/Android/Sdk"
        "$HOME/Library/Android/sdk"
        "/usr/lib/android-sdk"
        "/opt/android-sdk"
    )
    
    for path in "${COMMON_PATHS[@]}"; do
        if [ -d "$path" ]; then
            print_info "Found Android SDK at: $path"
            print_info "Updating local.properties..."
            echo "sdk.dir=$path" > local.properties
            break
        fi
    done
else
    print_info "Android SDK found"
fi

# Verify local.properties
if [ -f "local.properties" ]; then
    SDK_DIR=$(grep "sdk.dir" local.properties | cut -d'=' -f2)
    if [ -d "$SDK_DIR" ]; then
        print_info "SDK path verified: $SDK_DIR"
    else
        print_warn "SDK path in local.properties does not exist: $SDK_DIR"
        print_warn "Please update local.properties with the correct path"
    fi
else
    print_warn "local.properties not found"
    print_warn "Please create local.properties with your SDK path"
    print_warn "Example: sdk.dir=/path/to/android/sdk"
fi

print_info "Setup complete!"
print_info ""
print_info "Next steps:"
print_info "1. Open this project in Android Studio OR"
print_info "2. Build from command line: ./gradlew assembleDebug"
print_info ""
print_info "The APK will be generated at:"
print_info "  app/build/outputs/apk/debug/app-debug.apk"
