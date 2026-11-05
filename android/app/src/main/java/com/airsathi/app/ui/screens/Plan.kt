package com.airsathi.app.ui.screens

import android.graphics.drawable.GradientDrawable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import com.airsathi.app.R
import com.airsathi.app.data.Station
import com.airsathi.app.ui.MainViewModel
import com.airsathi.app.ui.UiState
import com.airsathi.app.ui.components.AqiDot
import com.airsathi.app.ui.components.SectionCard
import com.airsathi.app.ui.components.categoryName
import com.airsathi.app.ui.components.niceTime
import org.osmdroid.tileprovider.tilesource.TileSourceFactory
import org.osmdroid.util.GeoPoint
import org.osmdroid.views.MapView
import org.osmdroid.views.overlay.Marker

private val ACTIVITIES = listOf("walk" to R.string.act_walk, "school_run" to R.string.act_school_run,
    "exercise" to R.string.act_exercise, "outdoor_work" to R.string.act_outdoor_work)

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun PlanScreen(vm: MainViewModel, st: UiState) {
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
        SectionCard(stringResource(R.string.map)) {
            StationsMap(st.stations, Modifier.fillMaxWidth().height(300.dp).clip(RoundedCornerShape(16.dp))) { vm.setStation(it) }
            Spacer(Modifier.height(8.dp))
            st.stations.forEach { s ->
                Row(Modifier.padding(vertical = 3.dp), verticalAlignment = Alignment.CenterVertically) {
                    AqiDot(s.now?.category?.color)
                    Spacer(Modifier.width(8.dp))
                    Text("${s.name}, ${s.city}: ${s.now?.aqi?.toInt() ?: "–"} ${categoryName(s.now?.category?.key)}",
                        style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
        SectionCard(stringResource(R.string.best_time) + " · " + (st.detail?.station?.name ?: "")) {
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                ACTIVITIES.forEach { (id, label) ->
                    FilterChip(selected = st.activity == id, onClick = { vm.setActivity(id) }, label = { Text(stringResource(label)) })
                }
            }
            Spacer(Modifier.height(8.dp))
            val p = st.plan
            when (p?.message_id) {
                "best_times" -> {
                    p?.windows.orEmpty().forEach { w ->
                        Text("✓ ${niceTime(w.start)} – ${niceTime(w.end)}", style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier.padding(vertical = 4.dp))
                    }
                    p?.worst?.let { Text(stringResource(R.string.plan_worst, "${niceTime(it.start)} – ${niceTime(it.end)}"), style = MaterialTheme.typography.bodyMedium) }
                }
                "no_clear_time" -> Text(stringResource(R.string.plan_no_clear))
                "limit_all_day" -> Text(stringResource(R.string.plan_limit), style = MaterialTheme.typography.titleMedium)
                else -> Text(stringResource(R.string.plan_no_data))
            }
            Spacer(Modifier.height(6.dp))
            if (p?.mode == "forecast") Text(stringResource(R.string.plan_forecast), style = MaterialTheme.typography.bodySmall)
            if (p?.mode == "typical") Text(stringResource(R.string.plan_typical), style = MaterialTheme.typography.bodySmall)
            Text("WHO [5]: plan when and where to be active, rather than stopping activity.", style = MaterialTheme.typography.bodySmall)
        }
        Spacer(Modifier.height(24.dp))
    }
}

/** OpenStreetMap (osmdroid) with one coloured pin per station. Tap a pin to select that station. */
@Composable
fun StationsMap(stations: List<Station>, modifier: Modifier, onPick: (String) -> Unit) {
    AndroidView(
        modifier = modifier,
        factory = { ctx ->
            MapView(ctx).apply {
                setTileSource(TileSourceFactory.MAPNIK)
                setMultiTouchControls(true)
                controller.setZoom(7.6)
                controller.setCenter(GeoPoint(12.85, 76.75))
            }
        },
        update = { map ->
            map.overlays.clear()
            stations.forEach { s ->
                if (s.lat == null || s.lon == null) return@forEach
                val m = Marker(map)
                m.position = GeoPoint(s.lat, s.lon)
                m.title = "${s.name}, ${s.city}"
                m.snippet = "AQI ${s.now?.aqi?.toInt() ?: "–"} ${s.now?.category?.name ?: ""}"
                m.icon = GradientDrawable().apply {
                    shape = GradientDrawable.OVAL
                    setSize(48, 48)
                    setColor(android.graphics.Color.parseColor(s.now?.category?.color ?: "#9E9E9E"))
                    setStroke(4, android.graphics.Color.WHITE)
                }
                m.setAnchor(Marker.ANCHOR_CENTER, Marker.ANCHOR_CENTER)
                m.setOnMarkerClickListener { marker, _ -> marker.showInfoWindow(); onPick(s.id); true }
                map.overlays.add(m)
            }
            map.invalidate()
        },
    )
}
