package com.airsathi.app.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.airsathi.app.R
import com.airsathi.app.ui.UiState
import com.airsathi.app.ui.components.AqiDot
import com.airsathi.app.ui.components.AqiScale
import com.airsathi.app.ui.components.ForecastChart
import com.airsathi.app.ui.components.SectionCard
import com.airsathi.app.ui.components.categoryName
import com.airsathi.app.ui.components.niceTime

@Composable
fun ForecastScreen(st: UiState, back: () -> Unit) {
    val d = st.detail
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = back) { Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = null) }
            Text("${stringResource(R.string.forecast_title)} · ${d?.station?.name ?: ""}", style = MaterialTheme.typography.titleLarge)
        }
        SectionCard {
            ForecastChart(d?.now?.aqi, d?.forecast.orEmpty())
        }
        SectionCard {
            d?.forecast.orEmpty().forEach { f ->
                Row(Modifier.padding(vertical = 6.dp), verticalAlignment = Alignment.CenterVertically) {
                    AqiDot(f.category?.color)
                    Spacer(Modifier.width(10.dp))
                    Column {
                        Text("${niceTime(f.target)} · AQI ${f.aqi} · ${categoryName(f.category?.key)}", style = MaterialTheme.typography.titleMedium)
                        if (f.lo != null && f.hi != null) Text(stringResource(R.string.likely_range, f.lo, f.hi), style = MaterialTheme.typography.bodyMedium)
                        Text(
                            stringResource(when (f.confidence) {
                                "high" -> R.string.confidence_high; "moderate" -> R.string.confidence_moderate; else -> R.string.confidence_low
                            }) + " · " + stringResource(R.string.method, f.method ?: ""),
                            style = MaterialTheme.typography.bodySmall,
                        )
                    }
                }
            }
        }
        SectionCard(stringResource(R.string.how_accurate)) {
            Text(stringResource(R.string.accuracy_body), style = MaterialTheme.typography.bodyMedium)
            Spacer(Modifier.height(8.dp))
            Text(stringResource(R.string.accuracy_live), style = MaterialTheme.typography.bodyMedium)
        }
        SectionCard(stringResource(R.string.aqi_scale)) { AqiScale() }
        Spacer(Modifier.height(24.dp))
    }
}
