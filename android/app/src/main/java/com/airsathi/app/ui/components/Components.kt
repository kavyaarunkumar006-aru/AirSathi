package com.airsathi.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowDropDown
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.airsathi.app.R
import com.airsathi.app.data.Forecast
import com.airsathi.app.data.Station
import com.airsathi.app.ui.theme.aqiColor
import com.airsathi.app.ui.theme.onAqiColor
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

// ---------- small helpers ----------
fun niceTime(iso: String?): String = try {
    LocalDateTime.parse(iso).format(DateTimeFormatter.ofPattern("EEE h a"))
} catch (e: Exception) { iso ?: "" }

fun niceDate(iso: String?): String = try {
    LocalDateTime.parse(iso).format(DateTimeFormatter.ofPattern("d MMM, h a"))
} catch (e: Exception) { iso ?: "" }

fun pollutantName(p: String?) = when (p) {
    "pm25" -> "PM2.5"; "pm10" -> "PM10"; "no2" -> "NO₂"; "so2" -> "SO₂"; "o3" -> "Ozone"; "co" -> "CO"; else -> p ?: ""
}

@Composable
fun categoryName(key: String?): String = when (key) {
    // CPCB category names are kept in English on purpose: they are the official names.
    "good" -> "Good"; "satisfactory" -> "Satisfactory"; "moderate" -> "Moderate"; "poor" -> "Poor"
    "very_poor" -> "Very Poor"; "severe" -> "Severe"; else -> "–"
}

@Composable
fun conditionLabel(c: String): String = when (c) {
    "lung" -> stringResource(R.string.cond_lung)
    "heart" -> stringResource(R.string.cond_heart)
    "pregnant" -> stringResource(R.string.cond_pregnant)
    "outdoor_worker" -> stringResource(R.string.cond_outdoor_worker)
    "athlete" -> stringResource(R.string.cond_athlete)
    else -> c
}

@Composable
fun symptomLabel(s: String): String = when (s) {
    "cough" -> stringResource(R.string.sym_cough)
    "wheeze" -> stringResource(R.string.sym_wheeze)
    "breathless" -> stringResource(R.string.sym_breathless)
    "headache" -> stringResource(R.string.sym_headache)
    "eye_irritation" -> stringResource(R.string.sym_eye_irritation)
    "sore_throat" -> stringResource(R.string.sym_sore_throat)
    "chest_tight" -> stringResource(R.string.sym_chest_tight)
    "tired" -> stringResource(R.string.sym_tired)
    else -> s
}

val CONDITIONS = listOf("lung", "heart", "pregnant", "outdoor_worker", "athlete")

// ---------- layout pieces ----------
@Composable
fun SectionCard(title: String? = null, modifier: Modifier = Modifier, content: @Composable ColumnScope.() -> Unit) {
    Card(
        modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 6.dp),
        shape = RoundedCornerShape(20.dp),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surface),
        elevation = CardDefaults.cardElevation(defaultElevation = 1.dp),
    ) {
        Column(Modifier.padding(16.dp)) {
            if (title != null) {
                Text(title, style = MaterialTheme.typography.titleMedium)
                Spacer(Modifier.height(8.dp))
            }
            content()
        }
    }
}

@Composable
fun Pill(text: String, bg: Color, fg: Color, modifier: Modifier = Modifier) {
    Box(modifier.background(bg, RoundedCornerShape(50)).padding(horizontal = 12.dp, vertical = 4.dp)) {
        Text(text, color = fg, style = MaterialTheme.typography.labelLarge)
    }
}

@Composable
fun AqiDot(hex: String?, modifier: Modifier = Modifier) {
    Box(modifier.size(14.dp).background(aqiColor(hex), CircleShape))
}

// ---------- station picker ----------
@Composable
fun StationPicker(stations: List<Station>, selected: String, onPick: (String) -> Unit) {
    var open by remember { mutableStateOf(false) }
    val cur = stations.firstOrNull { it.id == selected }
    Box {
        OutlinedButton(onClick = { open = true }) {
            Text(cur?.let { "${it.name}, ${it.city}" } ?: selected)
            Icon(Icons.Filled.ArrowDropDown, contentDescription = null)
        }
        DropdownMenu(expanded = open, onDismissRequest = { open = false }) {
            stations.forEach { s ->
                DropdownMenuItem(
                    text = { Text("${s.name}, ${s.city}" + (s.now?.aqi?.let { "  ·  ${it.toInt()}" } ?: "")) },
                    leadingIcon = { AqiDot(s.now?.category?.color) },
                    onClick = { open = false; onPick(s.id) },
                )
            }
        }
    }
}

// ---------- forecast ----------
@Composable
fun ForecastStrip(items: List<Forecast>, onClick: () -> Unit = {}) {
    LazyRow(horizontalArrangement = Arrangement.spacedBy(10.dp), contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 16.dp)) {
        items(items) { f ->
            val c = aqiColor(f.category?.color)
            Card(onClick = onClick, shape = RoundedCornerShape(18.dp), colors = CardDefaults.cardColors(containerColor = c)) {
                Column(Modifier.width(104.dp).padding(12.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                    val fg = onAqiColor(f.category?.index)
                    Text(stringResource(R.string.in_hours, f.h ?: 0), color = fg, style = MaterialTheme.typography.labelLarge)
                    Text("${f.aqi ?: "–"}", color = fg, style = MaterialTheme.typography.headlineMedium, fontWeight = FontWeight.Bold)
                    Text(categoryName(f.category?.key), color = fg, style = MaterialTheme.typography.bodyMedium, textAlign = TextAlign.Center)
                    if (f.lo != null && f.hi != null) {
                        Text(stringResource(R.string.likely_range, f.lo, f.hi), color = fg.copy(alpha = 0.8f),
                            style = MaterialTheme.typography.bodySmall, textAlign = TextAlign.Center)
                    }
                }
            }
        }
    }
}

/** Line chart: current AQI and the forecasts, with the likely range as a shaded band and a dot per point in its category colour. */
@Composable
fun ForecastChart(nowAqi: Double?, items: List<Forecast>, modifier: Modifier = Modifier) {
    val pts = buildList {
        if (nowAqi != null) add(Triple(0, nowAqi.toFloat(), Pair(nowAqi.toFloat(), nowAqi.toFloat())))
        items.forEach { f -> if (f.aqi != null) add(Triple(f.h ?: 0, f.aqi.toFloat(), Pair((f.lo ?: f.aqi).toFloat(), (f.hi ?: f.aqi).toFloat()))) }
    }
    val colors = buildList {
        if (nowAqi != null) add(null)
        items.forEach { if (it.aqi != null) add(it.category?.color) }
    }
    val line = MaterialTheme.colorScheme.primary
    val grid = MaterialTheme.colorScheme.onSurfaceVariant.copy(alpha = 0.25f)
    Canvas(modifier.fillMaxWidth().height(180.dp)) {
        if (pts.size < 2) return@Canvas
        val maxY = (pts.maxOf { it.third.second } * 1.15f).coerceAtLeast(60f)
        val maxX = pts.maxOf { it.first }.toFloat().coerceAtLeast(1f)
        fun x(h: Int) = 12f + (size.width - 24f) * h / maxX
        fun y(v: Float) = size.height - 8f - (size.height - 16f) * v / maxY
        listOf(50f, 100f, 200f, 300f).filter { it < maxY }.forEach { g ->
            drawLine(grid, Offset(0f, y(g)), Offset(size.width, y(g)), strokeWidth = 2f)
        }
        val band = Path().apply {
            moveTo(x(pts[0].first), y(pts[0].third.second))
            pts.drop(1).forEach { lineTo(x(it.first), y(it.third.second)) }
            pts.reversed().forEach { lineTo(x(it.first), y(it.third.first)) }
            close()
        }
        drawPath(band, line.copy(alpha = 0.15f))
        val p = Path().apply {
            moveTo(x(pts[0].first), y(pts[0].second))
            pts.drop(1).forEach { lineTo(x(it.first), y(it.second)) }
        }
        drawPath(p, line, style = Stroke(width = 5f))
        pts.forEachIndexed { i, t ->
            drawCircle(aqiColor(colors.getOrNull(i)).takeIf { colors.getOrNull(i) != null } ?: line, radius = 10f, center = Offset(x(t.first), y(t.second)))
        }
    }
}

/** The six CPCB categories as a colour scale. */
@Composable
fun AqiScale() {
    val cats = listOf("good" to "#009865", "satisfactory" to "#A3C853", "moderate" to "#FFF833",
        "poor" to "#F29C33", "very_poor" to "#E93F33", "severe" to "#AF2D24")
    val ranges = listOf("0-50", "51-100", "101-200", "201-300", "301-400", "401-500")
    Row(Modifier.fillMaxWidth()) {
        cats.forEachIndexed { i, (k, hex) ->
            Column(Modifier.weight(1f).background(aqiColor(hex)).padding(vertical = 6.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                Text(ranges[i], color = onAqiColor(i), style = MaterialTheme.typography.labelSmall)
                Text(categoryName(k), color = onAqiColor(i), style = MaterialTheme.typography.labelSmall, textAlign = TextAlign.Center)
            }
        }
    }
}
