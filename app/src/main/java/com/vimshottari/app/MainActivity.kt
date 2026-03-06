package com.vimshottari.app

import android.Manifest
import android.annotation.SuppressLint
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.os.Environment
import android.os.Handler
import android.os.Looper
import android.util.Log
import android.view.View
import android.webkit.ConsoleMessage
import android.webkit.GeolocationPermissions
import android.webkit.JavascriptInterface
import android.webkit.ValueCallback
import android.webkit.WebChromeClient
import android.webkit.WebResourceRequest
import android.webkit.WebResourceResponse
import android.webkit.WebSettings
import android.webkit.WebView
import android.webkit.WebViewClient
import android.widget.Button
import android.widget.LinearLayout
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.swiperefreshlayout.widget.SwipeRefreshLayout
import com.chaquo.python.Python
import com.chaquo.python.PyObject
import java.io.File
import java.io.FileOutputStream
import java.util.concurrent.Executors

class MainActivity : AppCompatActivity() {
    
    companion object {
        private const val TAG = "MainActivity"
        private const val SERVER_PORT = 8080
        private const val PERMISSION_REQUEST_CODE = 100
        private const val INITIALIZATION_TIMEOUT = 60000L // 60 seconds
    }
    
    private lateinit var webView: WebView
    private lateinit var swipeRefresh: SwipeRefreshLayout
    private lateinit var loadingContainer: LinearLayout
    private lateinit var errorContainer: LinearLayout
    
    private val executor = Executors.newSingleThreadExecutor()
    private val mainHandler = Handler(Looper.getMainLooper())
    private var flaskServer: PyObject? = null
    private var isServerRunning = false
    private var pendingDownload: DownloadInfo? = null
    
    data class DownloadInfo(
        val url: String,
        val userAgent: String,
        val contentDisposition: String,
        val mimeType: String,
        val contentLength: Long
    )
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        initializeViews()
        checkPermissions()
    }
    
    private fun initializeViews() {
        webView = findViewById(R.id.webView)
        swipeRefresh = findViewById(R.id.swipeRefresh)
        loadingContainer = findViewById(R.id.loadingContainer)
        errorContainer = findViewById(R.id.errorContainer)
        
        swipeRefresh.setOnRefreshListener {
            webView.reload()
        }
        
        findViewById<Button>(R.id.retryButton).setOnClickListener {
            showLoading()
            startFlaskServer()
        }
        
        findViewById<Button>(R.id.exitButton).setOnClickListener {
            finish()
        }
    }
    
    private fun checkPermissions() {
        val permissions = mutableListOf<String>()
        
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) 
            != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.ACCESS_FINE_LOCATION)
        }
        
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) 
            != PackageManager.PERMISSION_GRANTED) {
            permissions.add(Manifest.permission.ACCESS_COARSE_LOCATION)
        }
        
        if (Build.VERSION.SDK_INT <= Build.VERSION_CODES.P) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.WRITE_EXTERNAL_STORAGE) 
                != PackageManager.PERMISSION_GRANTED) {
                permissions.add(Manifest.permission.WRITE_EXTERNAL_STORAGE)
            }
        }
        
        if (permissions.isNotEmpty()) {
            ActivityCompat.requestPermissions(this, permissions.toTypedArray(), PERMISSION_REQUEST_CODE)
        } else {
            initializeApp()
        }
    }
    
    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_REQUEST_CODE) {
            initializeApp()
        }
    }
    
    private fun initializeApp() {
        if (!VimshottariApplication.isPythonInitialized) {
            showError()
            return
        }
        
        showLoading()
        startFlaskServer()
    }
    
    private fun startFlaskServer() {
        executor.execute {
            try {
                val python = Python.getInstance()
                val flaskModule = python.getModule("flask_server")
                
                // Start the Flask server
                flaskServer = flaskModule.callAttr("start_server", SERVER_PORT)
                isServerRunning = true
                
                Log.i(TAG, "Flask server started on port $SERVER_PORT")
                
                // Wait a moment for server to be ready
                Thread.sleep(2000)
                
                mainHandler.post {
                    setupWebView()
                    loadApplication()
                }
                
            } catch (e: Exception) {
                Log.e(TAG, "Failed to start Flask server", e)
                mainHandler.post {
                    showError()
                }
            }
        }
    }
    
    @SuppressLint("SetJavaScriptEnabled")
    private fun setupWebView() {
        webView.settings.apply {
            javaScriptEnabled = true
            domStorageEnabled = true
            databaseEnabled = true
            cacheMode = WebSettings.LOAD_DEFAULT
            allowFileAccess = true
            allowContentAccess = true
            mixedContentMode = WebSettings.MIXED_CONTENT_ALWAYS_ALLOW
            useWideViewPort = true
            loadWithOverviewMode = true
            setSupportZoom(true)
            builtInZoomControls = true
            displayZoomControls = false
            javaScriptCanOpenWindowsAutomatically = true
            mediaPlaybackRequiresUserGesture = false
            geolocationEnabled = true
        }
        
        webView.webViewClient = object : WebViewClient() {
            override fun shouldOverrideUrlLoading(view: WebView?, request: WebResourceRequest?): Boolean {
                return false // Let WebView handle all URLs
            }
            
            override fun onPageFinished(view: WebView?, url: String?) {
                super.onPageFinished(view, url)
                swipeRefresh.isRefreshing = false
                showWebView()
            }
            
            override fun onReceivedError(view: WebView?, errorCode: Int, description: String?, failingUrl: String?) {
                super.onReceivedError(view, errorCode, description, failingUrl)
                Log.e(TAG, "WebView error: $description")
                if (errorCode == ERROR_CONNECT || errorCode == ERROR_HOST_LOOKUP) {
                    // Retry loading
                    mainHandler.postDelayed({ loadApplication() }, 2000)
                }
            }
        }
        
        webView.webChromeClient = object : WebChromeClient() {
            override fun onConsoleMessage(consoleMessage: ConsoleMessage?): Boolean {
                consoleMessage?.let {
                    Log.d(TAG, "Console [${it.sourceId()}:${it.lineNumber()}] ${it.message()}")
                }
                return true
            }
            
            override fun onGeolocationPermissionsShowPrompt(origin: String?, callback: GeolocationPermissions.Callback?) {
                callback?.invoke(origin, true, false)
            }
            
            override fun onShowFileChooser(
                webView: WebView?,
                filePathCallback: ValueCallback<Array<Uri>>?,
                fileChooserParams: FileChooserParams?
            ): Boolean {
                // Handle file chooser if needed
                return false
            }
        }
        
        // Add JavaScript interface for native communication
        webView.addJavascriptInterface(WebAppInterface(), "AndroidInterface")
    }
    
    private fun loadApplication() {
        webView.loadUrl("http://127.0.0.1:$SERVER_PORT/")
    }
    
    private fun showLoading() {
        loadingContainer.visibility = View.VISIBLE
        webView.visibility = View.GONE
        errorContainer.visibility = View.GONE
    }
    
    private fun showWebView() {
        loadingContainer.visibility = View.GONE
        webView.visibility = View.VISIBLE
        errorContainer.visibility = View.GONE
    }
    
    private fun showError() {
        loadingContainer.visibility = View.GONE
        webView.visibility = View.GONE
        errorContainer.visibility = View.VISIBLE
    }
    
    override fun onBackPressed() {
        if (webView.canGoBack()) {
            webView.goBack()
        } else {
            super.onBackPressed()
        }
    }
    
    override fun onDestroy() {
        super.onDestroy()
        executor.execute {
            try {
                flaskServer?.callAttr("stop")
                isServerRunning = false
            } catch (e: Exception) {
                Log.e(TAG, "Error stopping server", e)
            }
        }
        executor.shutdown()
    }
    
    // JavaScript Interface for communication between WebView and native code
    inner class WebAppInterface {
        
        @JavascriptInterface
        fun showToast(message: String) {
            Toast.makeText(this@MainActivity, message, Toast.LENGTH_SHORT).show()
        }
        
        @JavascriptInterface
        fun getDeviceInfo(): String {
            return """{
                "platform": "Android",
                "version": "${Build.VERSION.RELEASE}",
                "model": "${Build.MODEL}",
                "manufacturer": "${Build.MANUFACTURER}"
            }""".trimIndent()
        }
        
        @JavascriptInterface
        fun downloadPDF(base64Data: String, filename: String) {
            try {
                val downloadsDir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS)
                val file = File(downloadsDir, filename)
                
                val decodedBytes = android.util.Base64.decode(base64Data, android.util.Base64.DEFAULT)
                FileOutputStream(file).use { it.write(decodedBytes) }
                
                val uri = FileProvider.getUriForFile(
                    this@MainActivity,
                    "${packageName}.fileprovider",
                    file
                )
                
                val intent = android.content.Intent(android.content.Intent.ACTION_VIEW).apply {
                    setDataAndType(uri, "application/pdf")
                    addFlags(android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION)
                    addFlags(android.content.Intent.FLAG_ACTIVITY_NEW_TASK)
                }
                
                startActivity(intent)
                
            } catch (e: Exception) {
                Log.e(TAG, "Error downloading PDF", e)
                mainHandler.post {
                    Toast.makeText(this@MainActivity, "Download failed: ${e.message}", Toast.LENGTH_LONG).show()
                }
            }
        }
    }
}
