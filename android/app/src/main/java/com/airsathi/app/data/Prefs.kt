package com.airsathi.app.data

import android.content.Context
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.intPreferencesKey
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import com.airsathi.app.BuildConfig
import kotlinx.coroutines.flow.first

val Context.dataStore by preferencesDataStore(name = "airsathi_settings")

/** Settings saved on the phone (login token, language, last data for offline use...). */
data class Settings(
    val onboarded: Boolean = false,
    val token: String? = null,
    val server: String = BuildConfig.DEFAULT_SERVER,
    val lang: String = "en",
    val elder: Boolean = false,
    val dark: Boolean = false,
    val demo: Boolean = true,
    val demoPeriod: String = "spring",
    val demoAt: String? = null,
    val station: String = "silkboard",
    val memberId: Int? = null,
    val guestAge: Int? = null,
    val guestConditions: String = "",
)

object Prefs {
    private val ONBOARDED = booleanPreferencesKey("onboarded")
    private val TOKEN = stringPreferencesKey("token")
    private val SERVER = stringPreferencesKey("server")
    private val LANG = stringPreferencesKey("lang")
    private val ELDER = booleanPreferencesKey("elder")
    private val DARK = booleanPreferencesKey("dark")
    private val DEMO = booleanPreferencesKey("demo")
    private val DEMO_PERIOD = stringPreferencesKey("demo_period")
    private val DEMO_AT = stringPreferencesKey("demo_at")
    private val STATION = stringPreferencesKey("station")
    private val MEMBER = intPreferencesKey("member")
    private val GUEST_AGE = intPreferencesKey("guest_age")
    private val GUEST_CONDS = stringPreferencesKey("guest_conds")
    private val CACHE = stringPreferencesKey("cache_station_json")
    private val CACHE_TIME = stringPreferencesKey("cache_time")
    private val PUSH_TOKEN = stringPreferencesKey("push_token")

    suspend fun load(ctx: Context): Settings {
        val p = ctx.dataStore.data.first()
        return Settings(
            onboarded = p[ONBOARDED] ?: false, token = p[TOKEN], server = p[SERVER] ?: BuildConfig.DEFAULT_SERVER,
            lang = p[LANG] ?: "en", elder = p[ELDER] ?: false, dark = p[DARK] ?: false, demo = p[DEMO] ?: true,
            demoPeriod = p[DEMO_PERIOD] ?: "spring", demoAt = p[DEMO_AT]?.ifBlank { null }, station = p[STATION] ?: "silkboard",
            memberId = p[MEMBER]?.takeIf { it > 0 }, guestAge = p[GUEST_AGE]?.takeIf { it >= 0 }, guestConditions = p[GUEST_CONDS] ?: "",
        )
    }

    suspend fun save(ctx: Context, s: Settings) {
        ctx.dataStore.edit { p ->
            p[ONBOARDED] = s.onboarded
            if (s.token != null) p[TOKEN] = s.token else p.remove(TOKEN)
            p[SERVER] = s.server; p[LANG] = s.lang; p[ELDER] = s.elder; p[DARK] = s.dark; p[DEMO] = s.demo
            p[DEMO_PERIOD] = s.demoPeriod; p[DEMO_AT] = s.demoAt ?: ""; p[STATION] = s.station
            p[MEMBER] = s.memberId ?: 0; p[GUEST_AGE] = s.guestAge ?: -1; p[GUEST_CONDS] = s.guestConditions
        }
    }

    suspend fun saveCache(ctx: Context, json: String, time: String) {
        ctx.dataStore.edit { it[CACHE] = json; it[CACHE_TIME] = time }
    }

    suspend fun cache(ctx: Context): Pair<String?, String?> {
        val p: Preferences = ctx.dataStore.data.first()
        return p[CACHE] to p[CACHE_TIME]
    }

    suspend fun savePushToken(ctx: Context, t: String) { ctx.dataStore.edit { it[PUSH_TOKEN] = t } }
    suspend fun pushToken(ctx: Context): String? = ctx.dataStore.data.first()[PUSH_TOKEN]
}
