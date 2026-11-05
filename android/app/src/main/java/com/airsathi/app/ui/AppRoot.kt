package com.airsathi.app.ui

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Map
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.SnackbarHost
import androidx.compose.material3.SnackbarHostState
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.res.stringResource
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.airsathi.app.R
import com.airsathi.app.ui.screens.AuthScreen
import com.airsathi.app.ui.screens.ForecastScreen
import com.airsathi.app.ui.screens.HealthScreen
import com.airsathi.app.ui.screens.HomeScreen
import com.airsathi.app.ui.screens.MeScreen
import com.airsathi.app.ui.screens.MemberScreen
import com.airsathi.app.ui.screens.OnboardingScreen
import com.airsathi.app.ui.screens.PlanScreen
import com.airsathi.app.ui.theme.AirSathiTheme

private data class Tab(val route: String, val label: Int, val icon: ImageVector)

private val TABS = listOf(
    Tab("home", R.string.nav_home, Icons.Filled.Home),
    Tab("plan", R.string.nav_plan, Icons.Filled.Map),
    Tab("health", R.string.nav_health, Icons.Filled.Favorite),
    Tab("me", R.string.nav_me, Icons.Filled.Person),
)

@Composable
fun AppRoot(vm: MainViewModel) {
    val st by vm.state.collectAsState()
    AirSathiTheme(dark = st.settings.dark, elder = st.settings.elder) {
        if (!st.ready) return@AirSathiTheme
        if (!st.settings.onboarded) {
            OnboardingScreen(vm, st)
            return@AirSathiTheme
        }
        val nav = rememberNavController()
        val snack = remember { SnackbarHostState() }
        val networkMsg = stringResource(R.string.error_network)
        LaunchedEffect(st.error) {
            st.error?.let {
                snack.showSnackbar(if (it == "network") networkMsg else it)
                vm.clearError()
            }
        }
        LaunchedEffect(st.toast) {
            st.toast?.let { snack.showSnackbar(it); vm.clearToast() }
        }
        val entry by nav.currentBackStackEntryAsState()
        val route = entry?.destination?.route
        Scaffold(
            snackbarHost = { SnackbarHost(snack) },
            bottomBar = {
                if (TABS.any { it.route == route }) {
                    NavigationBar {
                        TABS.forEach { t ->
                            NavigationBarItem(
                                selected = route == t.route,
                                onClick = { nav.navigate(t.route) { popUpTo("home"); launchSingleTop = true } },
                                icon = { Icon(t.icon, contentDescription = null) },
                                label = { Text(stringResource(t.label)) },
                            )
                        }
                    }
                }
            },
        ) { pad ->
            NavHost(nav, startDestination = "home", modifier = Modifier.padding(pad)) {
                composable("home") { HomeScreen(vm, st, openForecast = { nav.navigate("forecast") }, openLogin = { nav.navigate("auth") }) }
                composable("forecast") { ForecastScreen(st, back = { nav.popBackStack() }) }
                composable("plan") { PlanScreen(vm, st) }
                composable("health") { HealthScreen(vm, st, openLogin = { nav.navigate("auth") }) }
                composable("me") {
                    MeScreen(vm, st, openLogin = { nav.navigate("auth") }, openMember = { id -> nav.navigate("member/$id") })
                }
                composable("member/{id}") { e ->
                    val id = e.arguments?.getString("id")?.toIntOrNull()
                    MemberScreen(vm, st, memberId = id?.takeIf { it > 0 }, back = { nav.popBackStack() })
                }
                composable("auth") { AuthScreen(vm, st, done = { nav.popBackStack("home", inclusive = false) }) }
            }
        }
    }
}
