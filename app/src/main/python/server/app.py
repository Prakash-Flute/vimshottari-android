#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Flask Application for Android
Modified version of the original WEB-VIM server for running inside Android.
"""

import os
import sys
from flask import Flask

# Get the base directory (where this file is located)
basedir = os.path.dirname(os.path.abspath(__file__))

# For Android, templates and static files are in assets
# Check if we're running in Android (Chaquopy environment)
def get_android_files_dir():
    """Get the Android files directory for storing data"""
    try:
        # Try to get Android context
        from com.chaquo.python import Python
        context = Python.getPlatform().getApplication()
        return context.getFilesDir().getAbsolutePath()
    except:
        return basedir

def get_template_folder():
    """Get the template folder path"""
    # First check if templates exist in the same directory (development)
    local_templates = os.path.join(basedir, 'client', 'templates')
    if os.path.exists(local_templates):
        return local_templates
    
    # For Android, templates should be in assets
    # In Chaquopy, we need to extract assets to a accessible location
    android_dir = get_android_files_dir()
    asset_templates = os.path.join(android_dir, 'server', 'client', 'templates')
    if os.path.exists(asset_templates):
        return asset_templates
    
    # Fallback to local templates
    return local_templates

def get_static_folder():
    """Get the static folder path"""
    local_static = os.path.join(basedir, 'client', 'static')
    if os.path.exists(local_static):
        return local_static
    
    android_dir = get_android_files_dir()
    asset_static = os.path.join(android_dir, 'server', 'client', 'static')
    if os.path.exists(asset_static):
        return asset_static
    
    return local_static

# Create Flask app with proper paths
template_folder = get_template_folder()
static_folder = get_static_folder()

app = Flask(
    __name__,
    template_folder=template_folder,
    static_folder=static_folder
)

app.secret_key = 'supersecretkey'

# Import and register routes
try:
    from apps.routes import register_routes
    register_routes(app)
except Exception as e:
    print(f"Error registering routes: {e}")
    import traceback
    traceback.print_exc()

# Tree manager is disabled for Android (no file watching needed)
# from apps.tree_manager import tree_manager
# tree_manager.start()

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)
