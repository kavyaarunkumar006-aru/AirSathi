package com.airsathi.app.ui.components

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/**
 * Sathi, the AirSathi mascot: a round cloud with a leaf. Its colour is the CPCB category colour and its face changes:
 * 0 Good = big smile, 1 Satisfactory = smile, 2 Moderate = flat mouth, 3 Poor = small frown + mask,
 * 4 Very Poor / 5 Severe = frown + mask + closed eyes. Original design drawn in code.
 */
@Composable
fun Sathi(categoryIndex: Int?, color: Color, modifier: Modifier = Modifier, size: Dp = 140.dp, description: String = "Sathi") {
    val lvl = categoryIndex ?: 1
    Canvas(modifier.size(size).semantics { contentDescription = description }) {
        val w = this.size.width
        val h = this.size.height
        val ink = Color(0xFF1F2D2B)
        // leaf on top
        val leaf = Path().apply {
            moveTo(w * 0.56f, h * 0.24f)
            cubicTo(w * 0.60f, h * 0.06f, w * 0.78f, h * 0.02f, w * 0.86f, h * 0.06f)
            cubicTo(w * 0.84f, h * 0.18f, w * 0.72f, h * 0.27f, w * 0.56f, h * 0.24f)
            close()
        }
        drawPath(leaf, Color(0xFF6DBE5C))
        // cloud body = overlapping circles
        val body = color
        drawCircle(body, radius = w * 0.20f, center = Offset(w * 0.30f, h * 0.55f))
        drawCircle(body, radius = w * 0.26f, center = Offset(w * 0.50f, h * 0.45f))
        drawCircle(body, radius = w * 0.20f, center = Offset(w * 0.70f, h * 0.55f))
        drawRoundRect(body, topLeft = Offset(w * 0.12f, h * 0.52f), size = Size(w * 0.76f, h * 0.24f),
            cornerRadius = androidx.compose.ui.geometry.CornerRadius(w * 0.12f))
        // eyes
        val eyeY = h * 0.50f
        if (lvl >= 4) {
            drawLine(ink, Offset(w * 0.37f, eyeY), Offset(w * 0.45f, eyeY), strokeWidth = w * 0.025f, cap = StrokeCap.Round)
            drawLine(ink, Offset(w * 0.55f, eyeY), Offset(w * 0.63f, eyeY), strokeWidth = w * 0.025f, cap = StrokeCap.Round)
        } else {
            drawCircle(ink, radius = w * 0.035f, center = Offset(w * 0.41f, eyeY))
            drawCircle(ink, radius = w * 0.035f, center = Offset(w * 0.59f, eyeY))
            drawCircle(Color.White, radius = w * 0.012f, center = Offset(w * 0.42f, eyeY - w * 0.012f))
            drawCircle(Color.White, radius = w * 0.012f, center = Offset(w * 0.60f, eyeY - w * 0.012f))
        }
        // cheeks when happy
        if (lvl <= 1) {
            drawCircle(Color(0x55FF8A80), radius = w * 0.03f, center = Offset(w * 0.33f, h * 0.58f))
            drawCircle(Color(0x55FF8A80), radius = w * 0.03f, center = Offset(w * 0.67f, h * 0.58f))
        }
        if (lvl >= 3) {
            // mask
            drawRoundRect(Color.White, topLeft = Offset(w * 0.36f, h * 0.56f), size = Size(w * 0.28f, h * 0.14f),
                cornerRadius = androidx.compose.ui.geometry.CornerRadius(w * 0.04f))
            drawLine(Color(0xFFB0BEC5), Offset(w * 0.36f, h * 0.60f), Offset(w * 0.24f, h * 0.55f), strokeWidth = w * 0.012f)
            drawLine(Color(0xFFB0BEC5), Offset(w * 0.64f, h * 0.60f), Offset(w * 0.76f, h * 0.55f), strokeWidth = w * 0.012f)
            drawLine(Color(0xFFCFD8DC), Offset(w * 0.40f, h * 0.63f), Offset(w * 0.60f, h * 0.63f), strokeWidth = w * 0.01f)
        } else {
            // mouth: smile depth depends on level
            val depth = when (lvl) { 0 -> 0.09f; 1 -> 0.05f; else -> 0.0f }
            val mouth = Path().apply {
                moveTo(w * 0.42f, h * 0.60f)
                quadraticBezierTo(w * 0.50f, h * (0.60f + depth), w * 0.58f, h * 0.60f)
            }
            drawPath(mouth, ink, style = Stroke(width = w * 0.025f, cap = StrokeCap.Round))
        }
    }
}
