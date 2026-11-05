package com.airsathi.app.widget

import android.content.Context
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.glance.GlanceId
import androidx.glance.GlanceModifier
import androidx.glance.action.actionStartActivity
import androidx.glance.action.clickable
import androidx.glance.appwidget.GlanceAppWidget
import androidx.glance.appwidget.GlanceAppWidgetReceiver
import androidx.glance.appwidget.cornerRadius
import androidx.glance.appwidget.provideContent
import androidx.glance.appwidget.updateAll
import androidx.glance.background
import androidx.glance.layout.Alignment
import androidx.glance.layout.Column
import androidx.glance.layout.fillMaxSize
import androidx.glance.layout.padding
import androidx.glance.text.FontWeight
import androidx.glance.text.Text
import androidx.glance.text.TextStyle
import androidx.glance.unit.ColorProvider
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters
import com.airsathi.app.MainActivity
import com.airsathi.app.data.Api
import com.airsathi.app.data.Prefs
import com.airsathi.app.data.StationDetail
import com.google.gson.Gson
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

/** Home-screen widget: AQI number, category and station, coloured by the CPCB category. Tap to open the app. */
class AqiWidget : GlanceAppWidget() {
    override suspend fun provideGlance(context: Context, id: GlanceId) {
        val (json, time) = Prefs.cache(context)
        val d = json?.let { runCatching { Gson().fromJson(it, StationDetail::class.java) }.getOrNull() }
        provideContent { WidgetBody(d, time) }
    }

    companion object {
        suspend fun refresh(context: Context) = AqiWidget().updateAll(context)
    }
}

@Composable
private fun WidgetBody(d: StationDetail?, time: String?) {
    val hex = d?.now?.category?.color ?: "#9E9E9E"
    val bg = Color(android.graphics.Color.parseColor(hex))
    val dark = (d?.now?.category?.index ?: 0) <= 3
    val fg = ColorProvider(if (dark) Color(0xFF1B1B1B) else Color.White)
    Column(
        GlanceModifier.fillMaxSize().background(bg).cornerRadius(20.dp).padding(12.dp).clickable(actionStartActivity<MainActivity>()),
        horizontalAlignment = Alignment.CenterHorizontally, verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("AirSathi", style = TextStyle(color = fg, fontSize = 12.sp))
        Text(d?.now?.aqi?.toInt()?.toString() ?: "–", style = TextStyle(color = fg, fontSize = 40.sp, fontWeight = FontWeight.Bold))
        Text(d?.now?.category?.name ?: "", style = TextStyle(color = fg, fontSize = 14.sp, fontWeight = FontWeight.Medium))
        Text(d?.station?.name ?: "", style = TextStyle(color = fg, fontSize = 12.sp))
        if (d?.now?.tier == "estimate") Text("Estimated", style = TextStyle(color = fg, fontSize = 10.sp))
        if (d?.mode == "demo") Text("Demo", style = TextStyle(color = fg, fontSize = 10.sp))
        Text(time ?: "", style = TextStyle(color = fg, fontSize = 10.sp))
    }
}

class AqiWidgetReceiver : GlanceAppWidgetReceiver() {
    override val glanceAppWidget: GlanceAppWidget = AqiWidget()
}

/** Runs about once an hour: fetches the home station and redraws the widget. */
class RefreshWorker(ctx: Context, params: WorkerParameters) : CoroutineWorker(ctx, params) {
    override suspend fun doWork(): Result {
        val s = Prefs.load(applicationContext)
        if (!s.onboarded) return Result.success()
        return try {
            val d = Api.create(s.server).station(s.station, if (s.demo) "demo" else "live", s.demoPeriod, s.demoAt)
            Prefs.saveCache(applicationContext, Gson().toJson(d), LocalDateTime.now().format(DateTimeFormatter.ofPattern("d MMM, h:mm a")))
            AqiWidget.refresh(applicationContext)
            Result.success()
        } catch (e: Exception) {
            Result.retry()
        }
    }
}
