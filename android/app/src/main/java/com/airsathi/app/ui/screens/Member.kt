package com.airsathi.app.ui.screens

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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import com.airsathi.app.R
import com.airsathi.app.data.MemberBody
import com.airsathi.app.ui.MainViewModel
import com.airsathi.app.ui.UiState
import com.airsathi.app.ui.components.CONDITIONS
import com.airsathi.app.ui.components.StationPicker
import com.airsathi.app.ui.components.conditionLabel

/** Add or edit one family member: age, health conditions, home station, alert level. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun MemberScreen(vm: MainViewModel, st: UiState, memberId: Int?, back: () -> Unit) {
    val m = st.me?.members?.firstOrNull { it.id == memberId }
    var name by remember { mutableStateOf(m?.name ?: "") }
    var age by remember { mutableStateOf(m?.age?.toString() ?: "") }
    var station by remember { mutableStateOf(m?.station ?: st.settings.station) }
    val conds = remember { mutableStateListOf<String>().apply { addAll(m?.conditions.orEmpty()) } }
    var alertsOn by remember { mutableStateOf(m?.alerts_on ?: true) }
    // the allowed maximum is the default for this person's groups (101 vulnerable, 201 healthy); the user can only lower it
    val vulnerable = conds.isNotEmpty() || (age.toIntOrNull()?.let { it < 14 || it >= 60 } ?: false)
    val maxThr = if (vulnerable) 101f else 201f
    var thr by remember { mutableFloatStateOf((m?.alert_threshold ?: maxThr.toInt()).toFloat()) }
    var error by remember { mutableStateOf<String?>(null) }

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(16.dp)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            IconButton(onClick = back) { Icon(Icons.AutoMirrored.Filled.ArrowBack, contentDescription = null) }
            Text(stringResource(if (m == null) R.string.add_member else R.string.edit_member), style = MaterialTheme.typography.titleLarge)
        }
        OutlinedTextField(name, { name = it }, label = { Text(stringResource(R.string.name)) }, singleLine = true, modifier = Modifier.fillMaxWidth())
        OutlinedTextField(age, { age = it.filter(Char::isDigit).take(3) }, label = { Text(stringResource(R.string.age)) }, singleLine = true,
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.fillMaxWidth())
        Spacer(Modifier.height(10.dp))
        Text(stringResource(R.string.home_station), style = MaterialTheme.typography.titleMedium)
        StationPicker(st.stations, station) { station = it }
        Spacer(Modifier.height(10.dp))
        Text(stringResource(R.string.health_conditions), style = MaterialTheme.typography.titleMedium)
        FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            CONDITIONS.forEach { c ->
                FilterChip(selected = c in conds, onClick = { if (c in conds) conds.remove(c) else conds.add(c) }, label = { Text(conditionLabel(c)) })
            }
        }
        Spacer(Modifier.height(10.dp))
        Row(verticalAlignment = Alignment.CenterVertically) {
            Text(stringResource(R.string.alerts_on), Modifier.weight(1f))
            Switch(alertsOn, { alertsOn = it })
        }
        val shown = thr.coerceAtMost(maxThr).toInt()
        Text(stringResource(R.string.alert_level, shown), style = MaterialTheme.typography.bodyLarge)
        Slider(value = thr.coerceAtMost(maxThr), onValueChange = { thr = it }, valueRange = 51f..maxThr)
        error?.let { Text(it, color = MaterialTheme.colorScheme.error) }
        Button(enabled = name.isNotBlank(), onClick = {
            vm.saveMember(m?.id, MemberBody(name.trim(), age.toIntOrNull(), conds.toList(), station, shown, alertsOn)) { e ->
                if (e == null) back() else error = e
            }
        }, modifier = Modifier.fillMaxWidth().padding(top = 8.dp)) { Text(stringResource(R.string.save)) }
        if (m != null && m.is_self != true) {
            TextButton(onClick = { vm.deleteMember(m.id); back() }) { Text(stringResource(R.string.delete), color = MaterialTheme.colorScheme.error) }
        }
    }
}
