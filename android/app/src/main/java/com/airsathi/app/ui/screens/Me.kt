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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.EmojiEvents
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.unit.dp
import com.airsathi.app.R
import com.airsathi.app.ui.MainViewModel
import com.airsathi.app.ui.UiState
import com.airsathi.app.ui.components.SectionCard
import com.airsathi.app.ui.components.conditionLabel
import com.airsathi.app.ui.components.niceDate

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun MeScreen(vm: MainViewModel, st: UiState, openLogin: () -> Unit, openMember: (Int) -> Unit) {
    var confirmDelete by remember { mutableStateOf(false) }
    var server by remember(st.settings.server) { mutableStateOf(st.settings.server) }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState())) {
        // account + family
        SectionCard(st.me?.name ?: stringResource(R.string.guest)) {
            if (!st.loggedIn) {
                Button(onClick = openLogin) { Text(stringResource(R.string.sign_in) + " / " + stringResource(R.string.sign_up)) }
            } else {
                Text(st.me?.email ?: "", style = MaterialTheme.typography.bodyMedium)
                Spacer(Modifier.height(8.dp))
                Text(stringResource(R.string.family), style = MaterialTheme.typography.titleMedium)
                st.me?.members.orEmpty().forEach { m ->
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text("${m.name}${m.age?.let { ", $it" } ?: ""}", style = MaterialTheme.typography.bodyLarge)
                            Text(
                                (m.groups.orEmpty().map { g -> if (g == "child" || g == "older") g else conditionLabel(g) }.joinToString(", "))
                                    .ifBlank { "—" } + " · " + stringResource(R.string.alert_level, m.alert_threshold ?: 201),
                                style = MaterialTheme.typography.bodySmall,
                            )
                        }
                        IconButton(onClick = { openMember(m.id) }) { Icon(Icons.Filled.Edit, contentDescription = stringResource(R.string.edit_member)) }
                    }
                }
                TextButton(onClick = { openMember(0) }) {
                    Icon(Icons.Filled.Add, contentDescription = null); Text(stringResource(R.string.add_member))
                }
            }
        }
        // badges
        st.badges?.let { b ->
            SectionCard(stringResource(R.string.badges) + " · " + stringResource(R.string.streak, b.streak ?: 0)) {
                FlowRow(horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                    b.badges.orEmpty().forEach { bd ->
                        Column(Modifier.width(96.dp).padding(vertical = 4.dp), horizontalAlignment = Alignment.CenterHorizontally) {
                            Icon(Icons.Filled.EmojiEvents, contentDescription = null,
                                tint = if (bd.earned == true) Color(0xFFF2B705) else Color(0xFFBDBDBD))
                            Text(bd.title ?: "", style = MaterialTheme.typography.labelMedium)
                        }
                    }
                }
            }
        }
        // settings
        SectionCard(stringResource(R.string.settings)) {
            Text(stringResource(R.string.language), style = MaterialTheme.typography.titleMedium)
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                listOf("en" to "English", "kn" to "ಕನ್ನಡ", "hi" to "हिन्दी").forEach { (c, l) ->
                    FilterChip(selected = st.settings.lang == c, onClick = { vm.setLanguage(c) }, label = { Text(l) })
                }
            }
            SettingSwitch(stringResource(R.string.elder_mode), st.settings.elder) { vm.setElder(it) }
            SettingSwitch(stringResource(R.string.dark_theme), st.settings.dark) { vm.setDark(it) }
            SettingSwitch(stringResource(R.string.demo_mode), st.settings.demo) { vm.setDemo(it) }
            if (st.settings.demo) {
                Text(stringResource(R.string.demo_period), style = MaterialTheme.typography.titleMedium)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    st.periods.forEach { p ->
                        FilterChip(selected = st.settings.demoPeriod == p.id, onClick = { vm.setDemoPeriod(p.id) }, label = { Text(p.label ?: p.id) })
                    }
                }
                Text(niceDate(st.detail?.now?.ts), style = MaterialTheme.typography.bodyLarge)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedButton(onClick = { vm.stepDemo(-1) }) { Text(stringResource(R.string.demo_back)) }
                    OutlinedButton(onClick = { vm.stepDemo(1) }) { Text(stringResource(R.string.demo_fwd)) }
                    OutlinedButton(onClick = { vm.stepDemo(6) }) { Text(stringResource(R.string.demo_fwd6)) }
                }
                TextButton(onClick = { vm.resetDemo() }) { Text(stringResource(R.string.demo_reset)) }
            }
            Spacer(Modifier.height(8.dp))
            OutlinedTextField(server, { server = it }, label = { Text(stringResource(R.string.server)) }, singleLine = true,
                modifier = Modifier.fillMaxWidth())
            if (server != st.settings.server) Button(onClick = { vm.setServer(server) }) { Text(stringResource(R.string.save)) }
        }
        // data status
        st.status?.stations?.let { list ->
            SectionCard(stringResource(R.string.data_status)) {
                list.forEach { s -> Text("${s.name}: ${s.label}${s.ts?.let { " (${niceDate(it)})" } ?: ""}", style = MaterialTheme.typography.bodySmall) }
            }
        }
        SectionCard(stringResource(R.string.about)) { Text(stringResource(R.string.about_body), style = MaterialTheme.typography.bodyMedium) }
        SectionCard(stringResource(R.string.privacy)) { Text(stringResource(R.string.privacy_body), style = MaterialTheme.typography.bodyMedium) }
        if (st.loggedIn) {
            SectionCard {
                OutlinedButton(onClick = { vm.logout() }, modifier = Modifier.fillMaxWidth()) { Text(stringResource(R.string.logout)) }
                TextButton(onClick = { confirmDelete = true }, modifier = Modifier.fillMaxWidth()) {
                    Text(stringResource(R.string.delete_account), color = MaterialTheme.colorScheme.error)
                }
            }
        }
        Spacer(Modifier.height(24.dp))
    }
    if (confirmDelete) {
        AlertDialog(
            onDismissRequest = { confirmDelete = false },
            text = { Text(stringResource(R.string.delete_confirm)) },
            confirmButton = { TextButton(onClick = { confirmDelete = false; vm.deleteAccount() }) { Text(stringResource(R.string.delete)) } },
            dismissButton = { TextButton(onClick = { confirmDelete = false }) { Text(stringResource(R.string.cancel)) } },
        )
    }
}

@Composable
private fun SettingSwitch(label: String, value: Boolean, onChange: (Boolean) -> Unit) {
    Row(Modifier.fillMaxWidth().padding(vertical = 4.dp), verticalAlignment = Alignment.CenterVertically) {
        Text(label, Modifier.weight(1f), style = MaterialTheme.typography.bodyLarge)
        Switch(checked = value, onCheckedChange = onChange)
    }
}
