package com.airsathi.app.ui.screens

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.airsathi.app.R
import com.airsathi.app.ui.MainViewModel
import com.airsathi.app.ui.UiState
import com.airsathi.app.ui.components.CONDITIONS
import com.airsathi.app.ui.components.Sathi
import com.airsathi.app.ui.components.StationPicker
import com.airsathi.app.ui.components.conditionLabel
import androidx.compose.ui.graphics.Color

/** Log in, create account, or reset a forgotten password. */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun AuthScreen(vm: MainViewModel, st: UiState, done: () -> Unit) {
    var mode by remember { mutableStateOf("signup") }          // signup | login | forgot | reset
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var pw by remember { mutableStateOf("") }
    var age by remember { mutableStateOf("") }
    var code by remember { mutableStateOf("") }
    var station by remember { mutableStateOf(st.settings.station) }
    val conds = remember { mutableStateListOf<String>() }
    var error by remember { mutableStateOf<String?>(null) }
    var busy by remember { mutableStateOf(false) }
    val networkMsg = stringResource(R.string.error_network)
    val finish: (String?) -> Unit = { e ->
        busy = false
        if (e == null) done() else error = if (e == "network") networkMsg else e
    }

    Surface(Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp)) {
            Sathi(categoryIndex = 0, color = Color(0xFF7FD3C9), size = 96.dp)
            Text(
                stringResource(
                    when (mode) { "login" -> R.string.sign_in; "signup" -> R.string.sign_up; else -> R.string.reset_password }
                ), style = MaterialTheme.typography.headlineMedium,
            )
            Spacer(Modifier.height(16.dp))
            if (mode == "signup") {
                OutlinedTextField(name, { name = it }, label = { Text(stringResource(R.string.name)) }, singleLine = true, modifier = Modifier.fillMaxWidth())
            }
            OutlinedTextField(email, { email = it.trim() }, label = { Text(stringResource(R.string.email)) }, singleLine = true,
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email), modifier = Modifier.fillMaxWidth())
            if (mode == "reset") {
                OutlinedTextField(code, { code = it.filter(Char::isDigit).take(6) }, label = { Text(stringResource(R.string.reset_code)) },
                    singleLine = true, keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.fillMaxWidth())
            }
            if (mode != "forgot") {
                OutlinedTextField(pw, { pw = it }, label = { Text(stringResource(if (mode == "reset") R.string.new_password else R.string.password)) },
                    singleLine = true, visualTransformation = PasswordVisualTransformation(),
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password), modifier = Modifier.fillMaxWidth())
            }
            if (mode == "signup") {
                OutlinedTextField(age, { age = it.filter(Char::isDigit).take(3) }, label = { Text(stringResource(R.string.age)) }, singleLine = true,
                    keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number), modifier = Modifier.fillMaxWidth())
                Spacer(Modifier.height(12.dp))
                Text(stringResource(R.string.home_station), style = MaterialTheme.typography.titleMedium)
                StationPicker(st.stations, station) { station = it }
                Spacer(Modifier.height(12.dp))
                Text(stringResource(R.string.health_conditions), style = MaterialTheme.typography.titleMedium)
                FlowRow {
                    CONDITIONS.forEach { c ->
                        FilterChip(selected = c in conds, onClick = { if (c in conds) conds.remove(c) else conds.add(c) },
                            label = { Text(conditionLabel(c)) }, modifier = Modifier.padding(end = 8.dp))
                    }
                }
            }
            error?.let { Text(it, color = MaterialTheme.colorScheme.error, modifier = Modifier.padding(top = 8.dp)) }
            Spacer(Modifier.height(16.dp))
            Button(
                enabled = !busy && email.contains("@"),
                onClick = {
                    busy = true; error = null
                    when (mode) {
                        "login" -> vm.login(email, pw, finish)
                        "signup" -> vm.signup(name.ifBlank { email.substringBefore("@") }, email, pw, age.toIntOrNull(), conds.toList(), station, finish)
                        "forgot" -> vm.forgot(email) { e -> busy = false; if (e == null) mode = "reset" else error = e }
                        else -> vm.reset(email, code, pw, finish)
                    }
                },
                modifier = Modifier.fillMaxWidth().height(56.dp),
            ) {
                Text(stringResource(when (mode) {
                    "login" -> R.string.sign_in; "signup" -> R.string.sign_up; "forgot" -> R.string.send_code; else -> R.string.reset_password
                }))
            }
            when (mode) {
                "signup" -> TextButton(onClick = { mode = "login" }) { Text(stringResource(R.string.have_account)) }
                "login" -> {
                    TextButton(onClick = { mode = "signup" }) { Text(stringResource(R.string.no_account)) }
                    TextButton(onClick = { mode = "forgot" }) { Text(stringResource(R.string.forgot_password)) }
                }
                else -> TextButton(onClick = { mode = "login" }) { Text(stringResource(R.string.sign_in)) }
            }
        }
    }
}
