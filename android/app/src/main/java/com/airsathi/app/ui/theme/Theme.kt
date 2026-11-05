package com.airsathi.app.ui.theme

import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.Density
import androidx.compose.ui.unit.sp

val Teal = Color(0xFF0E7C7B)
val TealLight = Color(0xFF5FB3AE)
val Leaf = Color(0xFF7BC86C)

private val Light = lightColorScheme(
    primary = Teal, onPrimary = Color.White, secondary = Leaf, background = Color(0xFFF4F7F5), surface = Color.White,
    surfaceVariant = Color(0xFFE6EFEC), onSurfaceVariant = Color(0xFF3F4A47),
)
private val Dark = darkColorScheme(
    primary = TealLight, onPrimary = Color(0xFF00201F), secondary = Leaf, background = Color(0xFF0F1716), surface = Color(0xFF172120),
    surfaceVariant = Color(0xFF23302E), onSurfaceVariant = Color(0xFFC3CECB),
)

/** Official CPCB category colours (from the backend), with a safe default. */
fun aqiColor(hex: String?): Color = try {
    if (hex == null) Color(0xFF9E9E9E) else Color(android.graphics.Color.parseColor(hex))
} catch (e: IllegalArgumentException) {
    Color(0xFF9E9E9E)
}

/** Readable text colour on top of a category colour (dark text on light yellow/green, white on red). */
fun onAqiColor(index: Int?): Color = if ((index ?: 0) in 0..3) Color(0xFF1B1B1B) else Color.White

private val Type = Typography(
    displayLarge = TextStyle(fontSize = 64.sp, fontWeight = FontWeight.Bold),
    headlineMedium = TextStyle(fontSize = 26.sp, fontWeight = FontWeight.SemiBold),
    titleLarge = TextStyle(fontSize = 20.sp, fontWeight = FontWeight.SemiBold),
    titleMedium = TextStyle(fontSize = 17.sp, fontWeight = FontWeight.SemiBold),
    bodyLarge = TextStyle(fontSize = 16.sp, lineHeight = 23.sp),
    bodyMedium = TextStyle(fontSize = 15.sp, lineHeight = 21.sp),
    labelLarge = TextStyle(fontSize = 15.sp, fontWeight = FontWeight.Medium),
)

/** elder = true makes every text 30 % bigger (on top of the phone's own font-size setting). */
@Composable
fun AirSathiTheme(dark: Boolean, elder: Boolean, content: @Composable () -> Unit) {
    val d = LocalDensity.current
    val density = if (elder) Density(d.density, d.fontScale * 1.3f) else d
    CompositionLocalProvider(LocalDensity provides density) {
        MaterialTheme(colorScheme = if (dark) Dark else Light, typography = Type, content = content)
    }
}
