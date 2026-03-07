package com.vimshottari.app

import android.app.Application
import android.util.Log
import com.chaquo.python.Python
import com.chaquo.python.android.AndroidPlatform

class VimshottariApplication : Application() {
    
    companion object {
        private const val TAG = "VimshottariApp"
        var isPythonInitialized = false
            private set
    }
    
    override fun onCreate() {
        super.onCreate()
        initializePython()
    }
    
    private fun initializePython() {
        try {
            if (!Python.isStarted()) {
                Python.start(AndroidPlatform(this))
                isPythonInitialized = true
                Log.i(TAG, "Python runtime initialized successfully")
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize Python runtime", e)
            isPythonInitialized = false
        }
    }
}
