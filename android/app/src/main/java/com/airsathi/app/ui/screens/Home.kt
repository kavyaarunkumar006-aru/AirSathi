package com.airsathi.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyRow
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.VolumeUp
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.airsathi.app.R
import com.airsathi.app.ui.MainViewModel
import com.airsathi.app.ui.UiState
import com.airsathi.app.ui.components.ForecastStrip
import com.airsathi.app.ui.components.Pill
import com.airsathi.app.ui.components.Sathi
import com.airsathi.app.ui.components.SectionCard
import com.airsathi.app.ui.components.StationPicker
import com.airsathi.app.ui.components.categoryName
import com.airsathi.app.ui.components.niceDate
import com.airsathi.app.ui.components.pollutantName
import com.airsathi.app.ui.theme.aqiColor
import com.airsathi.app.ui.theme.onAqiColor
import com.airsathi.app.util.Speaker

@Composable
fun HomeScreen(vm: MainViewModel, st: UiState, openForecast: () -> Unit, openLogin: () -> Unit) {
    val ctx = LocalContext.current
    val speaker = remember { Speaker(ctx) }
    DisposableEffect(Unit) { onDispose { speaker.shutdown() } }
    val d = st.detail
    val now = d?.now
    val cat = now?.category
    val color = aqiColor(cat?.color)
    val adv = st.advice?.advice_now
    val who = st.member?.name ?: stringResource(R.string.guest)

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).background(MaterialTheme.colorScheme.background)) {
        if (st.loading) LinearProgressIndicator(Modifier.fillMaxWidth())

        // banners: demo, offline, data source
        if (st.settings.demo && d != null) {
            Box(Modifier.fillMaxWidth().background(Color(0xFF37474F)).padding(8.dp)) {
                Text(stringResource(R.string.demo_banner, d.period_label ?: "", niceDate(now?.ts)), color = Color.White,
                    style = MaterialTheme.typography.labelLarge, modifier = Modifier.align(Alignment.Center))
            }
        }
        st.offlineSince?.let {
            Box(Modifier.fillMaxWidth().background(Color(0xFFB71C1C)).padding(8.dp)) {
                Text(stringResource(R.string.offline_banner, it), color = Color.White, modifier = Modifier.align(Alignment.Center))
            }
        }

        // who + station
        Row(Modifier.fillMaxWidth().padding(horizontal = 16.dp, vertical = 8.dp), verticalAlignment = Alignment.CenterVertically) {
            StationPicker(st.stations, d?.station?.id ?: st.settings.station) { vm.setStation(it) }
            Spacer(Modifier.weight(1f))
            IconButton(onClick = { vm.refreshAll() }) { Icon(Icons.Filled.Refresh, contentDescription = stringResource(R.string.retry)) }
        }
        val members = st.me?.members.orEmpty()
        if (members.size > 1) {
            LazyRow(contentPadding = androidx.compose.foundation.layout.PaddingValues(horizontal = 16.dp), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(members) { m ->
                    FilterChip(selected = m.id == st.member?.id, onClick = { vm.selectMember(m.id) }, label = { Text(m.name ?: "") })
                }
            }
        }

        if (d == null) {
            SectionCard {
                Text(if (st.loading) stringResource(R.string.loading) else stringResource(R.string.error_network))
                if (!st.loading) Button(onClick = { vm.refreshAll() }) { Text(stringResource(R.string.retry)) }
            }
            return@Column
        }

        // the big AQI card
        Column(
            Modifier.fillMaxWidth().padding(16.dp).background(color.copy(alpha = 0.22f), RoundedCornerShape(28.dp)).padding(20.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            Text(stringResource(R.string.air_now), style = MaterialTheme.typography.titleMedium)
            Sathi(cat?.index, if (cat == null) Color(0xFFB0BEC5) else color, size = 150.dp, description = categoryName(cat?.key))
            if (now?.aqi != null) {
                Text("${now.aqi.toInt()}", style = MaterialTheme.typography.displayLarge)
                Pill(categoryName(cat?.key), color, onAqiColor(cat?.index))
                now.dominant?.let {
                    Spacer(Modifier.height(6.dp))
                    Text(stringResource(R.string.main_pollutant, pollutantName(it)), style = MaterialTheme.typography.bodyLarge)
                }
            } else {
                Text(stringResource(R.string.no_data), textAlign = TextAlign.Center)
            }
            Spacer(Modifier.height(8.dp))
            // where the number comes from: always visible
            Text(now?.label ?: "", style = MaterialTheme.typography.bodyMedium, textAlign = TextAlign.Center, fontWeight = FontWeight.Medium)
            if (now?.age_h != null && now.age_h >= 1 && !st.settings.demo) {
                Text(stringResource(R.string.data_age, String.format("%.0f", now.age_h)), style = MaterialTheme.typography.bodySmall)
            }
            if (adv != null) {
                val catName = categoryName(cat?.key)
                Spacer(Modifier.height(12.dp))
                Text(stringResource(R.string.for_you, who), style = MaterialTheme.typography.titleMedium)
                Text(adv.actions?.firstOrNull()?.text ?: "", style = MaterialTheme.typography.bodyLarge, textAlign = TextAlign.Center)
                FilledTonalButton(onClick = {
                    speaker.speak(
                        listOfNotNull("AQI ${now?.aqi?.toInt() ?: ""}", catName, adv.headline?.text,
                            adv.actions?.firstOrNull()?.text).joinToString(". "), st.settings.lang)
                }, modifier = Modifier.padding(top = 8.dp)) {
                    Icon(Icons.AutoMirrored.Filled.VolumeUp, contentDescription = null)
                    Spacer(Modifier.width(6.dp))
                    Text(stringResource(R.string.listen))
                }
            }
        }

        // alert for the selected person in the next 12 h
        val next = st.advice?.advice_next12h
        val worst = st.advice?.worst_next12h
        if (next?.alert == true && worst != null) {
            SectionCard {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(Icons.Filled.Warning, contentDescription = null, tint = aqiColor(worst.category?.color))
                    Spacer(Modifier.width(8.dp))
                    Text(stringResource(R.string.alert_banner, who), style = MaterialTheme.typography.titleMedium)
                }
                Text("${stringResource(R.string.worst_next_12h)}: ${worst.aqi} (${categoryName(worst.category?.key)}), ${niceDate(worst.target)}")
                next.actions?.forEach { Text("• ${it.text}", style = MaterialTheme.typography.bodyMedium) }
            }
        }

        // forecast
        Text(stringResource(R.string.next_24h), style = MaterialTheme.typography.titleLarge, modifier = Modifier.padding(start = 16.dp, top = 8.dp, bottom = 8.dp))
        ForecastStrip(d.forecast.orEmpty(), onClick = openForecast)
        TextButton(onClick = openForecast, modifier = Modifier.padding(start = 8.dp)) { Text(stringResource(R.string.how_accurate)) }

        // tip
        st.tip?.let { tip ->
            SectionCard(stringResource(R.string.tip_today)) {
                Text(tip.text ?: "", style = MaterialTheme.typography.bodyLarge)
                Text(tip.source ?: "", style = MaterialTheme.typography.bodySmall)
            }
        }
        if (!st.loggedIn) {
            SectionCard {
                AssistChip(onClick = openLogin, label = { Text(stringResource(R.string.sign_up)) })
            }
        }
        Spacer(Modifier.height(24.dp))
    }
}
