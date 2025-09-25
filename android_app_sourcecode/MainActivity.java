package com.example.flaskapp;

import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.activity.result.ActivityResultLauncher;
import androidx.activity.result.contract.ActivityResultContracts;
import androidx.appcompat.app.AppCompatActivity;

public class MainActivity extends AppCompatActivity {

    private ValueCallback<Uri[]> filePathCallback;

    // Handles <input type="file">
    private final ActivityResultLauncher<Intent> fileChooserLauncher =
            registerForActivityResult(new ActivityResultContracts.StartActivityForResult(),
                    result -> {
                        if (filePathCallback != null) {
                            Uri[] results = null;
                            if (result.getResultCode() == RESULT_OK && result.getData() != null) {
                                results = new Uri[]{result.getData().getData()};
                            }
                            filePathCallback.onReceiveValue(results);
                            filePathCallback = null;
                        }
                    });

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        WebView webView = new WebView(this);
        setContentView(webView);

        WebSettings webSettings = webView.getSettings();
        webSettings.setJavaScriptEnabled(true);
        webSettings.setDomStorageEnabled(true);

        // Keep navigation inside WebView
        webView.setWebViewClient(new WebViewClient());

        // Support file chooser & camera input
        webView.setWebChromeClient(new WebChromeClient() {
            @Override
            public boolean onShowFileChooser(WebView webView,
                                             ValueCallback<Uri[]> filePathCallback,
                                             FileChooserParams fileChooserParams) {
                MainActivity.this.filePathCallback = filePathCallback;
                Intent intent = fileChooserParams.createIntent();
                fileChooserLauncher.launch(intent);
                return true;
            }
        });

        // Load your Flask server
        webView.loadUrl("http://209.38.197.151:5000");
    }
}
