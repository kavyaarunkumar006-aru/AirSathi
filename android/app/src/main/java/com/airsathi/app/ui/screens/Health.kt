package com.airsathi.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
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
import androidx.compose.material3.AssistChip
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.airsathi.app.R
import com.airsathi.app.ui.MainViewModel
import com.airsathi.app.ui.UiState
import com.airsathi.app.ui.components.SectionCard
import com.airsathi.app.ui.components.categoryName
import com.airsathi.app.ui.components.symptomLabel
import com.airsathi.app.ui.theme.aqiColor

private val SYMPTOMS = listOf("cough", "wheeze", "breathless", "headache", "eye_irritation", "sore_throat", "chest_tight", "tired")

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun HealthScreen(vm: MainViewModel, st: UiState, openLogin: () -> Unit) {
    val a = st.advice?.advice_now
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
        // advice
        SectionCard(stringResource(R.string.what_to_do) + (st.member?.name?.let { " · $it" } ?: "")) {
            if (a == null) {
                Text(stringResource(R.string.no_data))
            } else {
                Text("AQI ${a.aqi} · ${categoryName(a.category?.key)}", style = MaterialTheme.typography.titleMedium)
                Text("${a.headline?.text} ${a.headline?.source ?: ""}", style = MaterialTheme.typography.bodyMedium)
                Spacer(Modifier.height(8.dp))
                a.actions.orEmpty().forEach { m -> Text("• ${m.text} ${m.source ?: ""}", style = MaterialTheme.typography.bodyLarge) }
                a.tip?.let { Spacer(Modifier.height(6.dp)); Text("💡 ${it.text} ${it.source ?: ""}", style = MaterialTheme.typography.bodyMedium) }
                a.doctor?.let {
                    Spacer(Modifier.height(10.dp))
                    Text(stringResource(R.string.see_doctor), style = MaterialTheme.typography.titleMedium)
                    Text("${it.text} ${it.source ?: ""}", style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
        // diary
        SectionCard(stringResource(R.string.diary)) {
            if (!st.loggedIn) {
                Text(stringResource(R.string.login_needed))
                AssistChip(onClick = openLogin, label = { Text(stringResource(R.string.sign_in)) })
            } else {
                Text(stringResource(R.string.diary_hint), style = MaterialTheme.typography.bodyMedium)
                val picked = remember { mutableStateListOf<String>() }
                var saved by remember { mutableStateOf<String?>(null) }
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SYMPTOMS.forEach { s ->
                        FilterChip(selected = s in picked, onClick = { if (s in picked) picked.remove(s) else picked.add(s) },
                            label = { Text(symptomLabel(s)) })
                    }
                }
                Button(enabled = picked.isNotEmpty(), onClick = {
                    vm.logSymptoms(picked.toList()) { aqi -> saved = aqi?.toString() ?: "–"; picked.clear() }
                }) { Text(stringResource(R.string.save)) }
                saved?.let { Text(stringResource(R.string.diary_saved, it), style = MaterialTheme.typography.bodyMedium) }
                val summary = st.diary?.summary.orEmpty()
                if (summary.isNotEmpty()) {
                    Spacer(Modifier.height(8.dp))
                    Text(stringResource(R.string.diary_summary), style = MaterialTheme.typography.titleMedium)
                    summary.forEach { c ->
                        Text("${symptomLabel(c.symptom ?: "")}: " + stringResource(R.string.diary_times, c.count ?: 0, c.avg_aqi?.toString() ?: "–"),
                            style = MaterialTheme.typography.bodyMedium)
                    }
                }
            }
        }
        // weekly bars
        val days = st.weekly?.days.orEmpty()
        if (days.isNotEmpty()) {
            SectionCard(stringResource(R.string.weekly)) {
                val max = (days.maxOf { it.aqi ?: 0 }).coerceAtLeast(100)
                Row(Modifier.fillMaxWidth().height(140.dp), verticalAlignment = Alignment.Bottom, horizontalArrangement = Arrangement.SpaceEvenly) {
                    days.forEach { d ->
                        Column(horizontalAlignment = Alignment.CenterHorizontally) {
                            Text("${d.aqi}", style = MaterialTheme.typography.labelSmall)
                            Box(Modifier.width(22.dp).height((110f * (d.aqi ?: 0) / max).dp)
                                .background(aqiColor(d.category?.color), RoundedCornerShape(6.dp)))
                            Text(d.day?.takeLast(2) ?: "", style = MaterialTheme.typography.labelSmall)
                        }
                    }
                }
            }
        }
        // disclaimer + sources
        SectionCard(stringResource(R.string.disclaimer_title)) {
            Text(st.advice?.disclaimer?.text ?: "", style = MaterialTheme.typography.bodyMedium)
            Spacer(Modifier.height(8.dp))
            Text(stringResource(R.string.sources), style = MaterialTheme.typography.titleMedium)
            st.advice?.sources.orEmpty().forEach { (k, v) -> Text("$k $v", style = MaterialTheme.typography.bodySmall) }
        }
        Spacer(Modifier.height(24.dp))
    }
}
