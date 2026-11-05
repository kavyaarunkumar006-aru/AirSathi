package com.airsathi.app

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import com.airsathi.app.widget.RefreshWorker
import org.osmdroid.config.Configuration
import java.util.concurrent.TimeUnit

class AirSathiApp : Application() {
    override fun onCreate() {
        super.onCreate()
        // notification channel for air-quality alerts
        val ch = NotificationChannel("air_alerts", getString(R.string.notif_channel), NotificationManager.IMPORTANCE_HIGH)
        getSystemService(NotificationManager::class.java).createNotificationChannel(ch)
        // OpenStreetMap asks every app to identify itself
        Configuration.getInstance().userAgentValue = packageName
        // refresh the home-screen widget about once an hour
        WorkManager.getInstance(this).enqueueUniquePeriodicWork(
            "widget_refresh", ExistingPeriodicWorkPolicy.KEEP,
            PeriodicWorkRequestBuilder<RefreshWorker>(1, TimeUnit.HOURS).build(),
        )
    }
}
