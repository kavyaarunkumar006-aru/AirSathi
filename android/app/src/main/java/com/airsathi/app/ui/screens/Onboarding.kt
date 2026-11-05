package com.airsathi.app.ui.screens

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.res.stringResource
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.airsathi.app.R
import com.airsathi.app.ui.MainViewModel
import com.airsathi.app.ui.UiState
import com.airsathi.app.ui.components.Sathi

/** First launch: 1) language, 2) meet Sathi, 3) guest or account. */
@Composable
fun OnboardingScreen(vm: MainViewModel, st: UiState) {
    var step by remember { mutableIntStateOf(0) }
    var showAuth by remember { mutableIntStateOf(0) }       // 0 = no, 1 = show login/sign-up
    if (showAuth == 1) {
        AuthScreen(vm, st, done = { showAuth = 0 })
        return
    }
    Surface(Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
        Column(
            Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally, verticalArrangement = Arrangement.Center,
        ) {
            Sathi(categoryIndex = if (step == 0) 1 else 0, color = Color(0xFF7FD3C9), size = 170.dp)
            Spacer(Modifier.height(12.dp))
            Text(stringResource(R.string.app_name), style = MaterialTheme.typography.headlineMedium)
            Text(stringResource(R.string.tagline), style = MaterialTheme.typography.bodyLarge, textAlign = TextAlign.Center)
            Spacer(Modifier.height(28.dp))
            when (step) {
                0 -> {
                    Text(stringResource(R.string.choose_language), style = MaterialTheme.typography.titleLarge)
                    Spacer(Modifier.height(12.dp))
                    listOf("en" to "English", "kn" to "ಕನ್ನಡ", "hi" to "हिन्दी").forEach { (code, label) ->
                        val sel = st.settings.lang == code
                        if (sel) Button(onClick = { vm.setLanguage(code); step = 1 }, Modifier.fillMaxWidth().height(56.dp)) {
                            Text(label, style = MaterialTheme.typography.titleLarge)
                        } else OutlinedButton(onClick = { vm.setLanguage(code); step = 1 }, Modifier.fillMaxWidth().height(56.dp)) {
                            Text(label, style = MaterialTheme.typography.titleLarge)
                        }
                        Spacer(Modifier.height(10.dp))
                    }
                }
                1 -> {
                    Text(stringResource(R.string.meet_sathi), style = MaterialTheme.typography.titleLarge)
                    Spacer(Modifier.height(8.dp))
                    Text(stringResource(R.string.meet_sathi_body), style = MaterialTheme.typography.bodyLarge, textAlign = TextAlign.Center)
                    Spacer(Modifier.height(24.dp))
                    Button(onClick = { step = 2 }, Modifier.fillMaxWidth().height(56.dp)) { Text(stringResource(R.string.next)) }
                }
                else -> {
                    Button(onClick = { showAuth = 1 }, Modifier.fillMaxWidth().height(56.dp)) { Text(stringResource(R.string.sign_up)) }
                    Spacer(Modifier.height(10.dp))
                    OutlinedButton(onClick = { vm.finishOnboarding() }, Modifier.fillMaxWidth().height(56.dp)) {
                        Text(stringResource(R.string.try_guest))
                    }
                    TextButton(onClick = { showAuth = 1 }) { Text(stringResource(R.string.have_account)) }
                }
            }
        }
    }
}
