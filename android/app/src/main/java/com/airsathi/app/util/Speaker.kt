package com.airsathi.app.util

import android.content.Context
import android.speech.tts.TextToSpeech
import java.util.Locale

/** Reads text aloud with the phone's built-in voice (Kannada / Hindi if the phone has those voices, otherwise English). */
class Speaker(context: Context) {
    private var ready = false
    private val tts = TextToSpeech(context.applicationContext) { status -> ready = status == TextToSpeech.SUCCESS }

    fun speak(text: String, lang: String) {
        if (!ready) return
        val locale = when (lang) { "kn" -> Locale("kn", "IN"); "hi" -> Locale("hi", "IN"); else -> Locale("en", "IN") }
        val ok = tts.isLanguageAvailable(locale) >= TextToSpeech.LANG_AVAILABLE
        tts.language = if (ok) locale else Locale.ENGLISH
        tts.setSpeechRate(0.9f)
        tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "airsathi")
    }

    fun shutdown() {
        tts.stop()
        tts.shutdown()
    }
}
