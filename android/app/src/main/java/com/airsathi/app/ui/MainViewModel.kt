package com.airsathi.app.ui

import android.app.Application
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.airsathi.app.data.AdviceResp
import com.airsathi.app.data.Api
import com.airsathi.app.data.Badges
import com.airsathi.app.data.DeviceBody
import com.airsathi.app.data.DiaryBody
import com.airsathi.app.data.DiaryResp
import com.airsathi.app.data.ForgotBody
import com.airsathi.app.data.LoginBody
import com.airsathi.app.data.Me
import com.airsathi.app.data.MeBody
import com.airsathi.app.data.Member
import com.airsathi.app.data.MemberBody
import com.airsathi.app.data.Msg
import com.airsathi.app.data.Period
import com.airsathi.app.data.PlanResp
import com.airsathi.app.data.Prefs
import com.airsathi.app.data.ResetBody
import com.airsathi.app.data.Settings
import com.airsathi.app.data.SignUpBody
import com.airsathi.app.data.Station
import com.airsathi.app.data.StationDetail
import com.airsathi.app.data.Status
import com.airsathi.app.data.Weekly
import com.airsathi.app.widget.AqiWidget
import com.google.firebase.FirebaseApp
import com.google.firebase.messaging.FirebaseMessaging
import com.google.gson.Gson
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import retrofit2.HttpException
import java.time.LocalDateTime
import java.time.format.DateTimeFormatter

data class UiState(
    val ready: Boolean = false,
    val settings: Settings = Settings(),
    val loading: Boolean = false,
    val error: String? = null,
    val offlineSince: String? = null,
    val me: Me? = null,
    val stations: List<Station> = emptyList(),
    val detail: StationDetail? = null,
    val advice: AdviceResp? = null,
    val plan: PlanResp? = null,
    val activity: String = "walk",
    val weekly: Weekly? = null,
    val diary: DiaryResp? = null,
    val badges: Badges? = null,
    val tip: Msg? = null,
    val status: Status? = null,
    val periods: List<Period> = emptyList(),
    val toast: String? = null,
) {
    val loggedIn get() = settings.token != null
    val mode get() = if (settings.demo) "demo" else "live"
    val member: Member? get() = me?.members?.firstOrNull { it.id == settings.memberId } ?: me?.members?.firstOrNull()
}

class MainViewModel(app: Application) : AndroidViewModel(app) {
    private val ctx = app.applicationContext
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state
    private var api: Api = Api.create(Settings().server)
    private val gson = Gson()

    private val s get() = _state.value.settings
    private val auth get() = s.token?.let { "Bearer $it" }

    init {
        viewModelScope.launch {
            val loaded = Prefs.load(ctx)
            api = Api.create(loaded.server)
            _state.update { it.copy(settings = loaded, ready = true) }
            if (loaded.onboarded) refreshAll()
            else runCatching { api.stations("demo", loaded.demoPeriod, null) }.onSuccess { l -> _state.update { it.copy(stations = l) } }
        }
    }

    private fun msg(e: Throwable): String = when (e) {
        is HttpException -> try {
            val body = e.response()?.errorBody()?.string() ?: ""
            Regex("\"detail\"\\s*:\\s*\"([^\"]+)\"").find(body)?.groupValues?.get(1) ?: "Error ${e.code()}"
        } catch (x: Exception) { "Error ${e.code()}" }
        else -> "network"
    }

    private fun updateSettings(change: (Settings) -> Settings, reload: Boolean = true) {
        val new = change(s)
        _state.update { it.copy(settings = new) }
        viewModelScope.launch {
            Prefs.save(ctx, new)
            if (reload) refreshAll()
        }
    }

    // ---------------- loading data ----------------
    fun refreshAll() {
        viewModelScope.launch {
            _state.update { it.copy(loading = true, error = null) }
            try {
                if (s.token != null) {
                    try {
                        val me = api.me(auth!!)
                        _state.update { it.copy(me = me) }
                        if (s.memberId == null || me.members.orEmpty().none { m -> m.id == s.memberId }) {
                            val self = me.members.orEmpty().firstOrNull()
                            if (self != null) {
                                val new = s.copy(memberId = self.id, station = self.station ?: s.station)
                                _state.update { it.copy(settings = new) }
                                Prefs.save(ctx, new)
                            }
                        }
                    } catch (e: HttpException) {
                        if (e.code() == 401) logout(silent = true)
                    }
                }
                val st = _state.value.member?.station ?: s.station
                val detail = api.station(st, _state.value.mode, s.demoPeriod, s.demoAt)
                _state.update { it.copy(detail = detail, offlineSince = null) }
                val now = LocalDateTime.now().format(DateTimeFormatter.ofPattern("d MMM, h:mm a"))
                Prefs.saveCache(ctx, gson.toJson(detail), now)
                try { AqiWidget.refresh(ctx) } catch (e: Exception) { /* widget not placed yet */ }
                loadAdvice()
                loadPlan()
                launch { runCatching { api.stations(_state.value.mode, s.demoPeriod, s.demoAt) }.onSuccess { l -> _state.update { it.copy(stations = l) } } }
                launch { runCatching { api.weekly(st, _state.value.mode, s.demoPeriod, s.demoAt) }.onSuccess { w -> _state.update { it.copy(weekly = w) } } }
                launch { runCatching { api.tip(s.lang) }.onSuccess { t -> _state.update { it.copy(tip = t) } } }
                launch { runCatching { api.periods() }.onSuccess { p -> _state.update { it.copy(periods = p) } } }
                launch { runCatching { api.status() }.onSuccess { p -> _state.update { it.copy(status = p) } } }
                if (s.token != null) {
                    launch { runCatching { api.diary(auth!!, _state.value.member?.id) }.onSuccess { d -> _state.update { it.copy(diary = d) } } }
                    launch { runCatching { api.badges(auth!!) }.onSuccess { b -> _state.update { it.copy(badges = b) } } }
                    registerPush()
                }
            } catch (e: Exception) {
                // offline: show the last saved data, clearly labelled
                val (json, time) = Prefs.cache(ctx)
                val cached = json?.let { runCatching { gson.fromJson(it, StationDetail::class.java) }.getOrNull() }
                _state.update { it.copy(error = msg(e), detail = it.detail ?: cached, offlineSince = if (cached != null) time else null) }
            } finally {
                _state.update { it.copy(loading = false) }
            }
        }
    }

    private suspend fun loadAdvice() {
        val st = _state.value.detail?.station?.id ?: s.station
        val m = _state.value.member
        val a = runCatching {
            if (m != null && auth != null) api.advice(auth, st, _state.value.mode, s.demoPeriod, s.demoAt, s.lang, m.id, null, null)
            else api.advice(null, st, _state.value.mode, s.demoPeriod, s.demoAt, s.lang, null, s.guestAge, s.guestConditions)
        }.getOrNull()
        _state.update { it.copy(advice = a) }
    }

    private suspend fun loadPlan() {
        val st = _state.value.detail?.station?.id ?: s.station
        val p = runCatching { api.plan(st, _state.value.activity, _state.value.mode, s.demoPeriod, s.demoAt) }.getOrNull()
        _state.update { it.copy(plan = p) }
    }

    fun setActivity(a: String) {
        _state.update { it.copy(activity = a) }
        viewModelScope.launch { loadPlan() }
    }

    // ---------------- settings ----------------
    fun finishOnboarding() = updateSettings({ it.copy(onboarded = true) })
    fun setLanguage(lang: String) {
        AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(lang))
        updateSettings({ it.copy(lang = lang) })
        if (auth != null) viewModelScope.launch { runCatching { api.updateMe(auth!!, MeBody(lang = lang)) } }
    }
    fun setElder(v: Boolean) = updateSettings({ it.copy(elder = v) }, reload = false)
    fun setDark(v: Boolean) = updateSettings({ it.copy(dark = v) }, reload = false)
    fun setDemo(v: Boolean) = updateSettings({ it.copy(demo = v, demoAt = null) })
    fun setDemoPeriod(p: String) = updateSettings({ it.copy(demoPeriod = p, demoAt = null) })
    fun setStation(id: String) {
        val m = _state.value.member
        if (m != null && auth != null) {
            saveMember(m.id, MemberBody(m.name ?: "", m.age, m.conditions.orEmpty(), id, m.alert_threshold, m.alerts_on ?: true))
        }
        updateSettings({ it.copy(station = id) })
    }
    fun selectMember(id: Int) = updateSettings({ it.copy(memberId = id) })
    fun setGuestProfile(age: Int?, conditions: List<String>) = updateSettings({ it.copy(guestAge = age, guestConditions = conditions.joinToString(",")) })
    fun setServer(url: String) {
        val u = url.trim().let { if (it.endsWith("/")) it else "$it/" }
        api = Api.create(u)
        updateSettings({ it.copy(server = u) })
    }

    /** Move the demo clock by some hours (from the hour currently shown). */
    fun stepDemo(hours: Long) {
        val ts = _state.value.detail?.now?.ts ?: return
        val t = runCatching { LocalDateTime.parse(ts).plusHours(hours) }.getOrNull() ?: return
        updateSettings({ it.copy(demoAt = t.toString()) })
    }
    fun resetDemo() = updateSettings({ it.copy(demoAt = null) })
    fun clearToast() = _state.update { it.copy(toast = null) }
    fun clearError() = _state.update { it.copy(error = null) }

    // ---------------- accounts ----------------
    private fun afterLogin(token: String?) {
        if (token == null) return
        updateSettings({ it.copy(token = token, onboarded = true, memberId = null) })
    }

    fun login(email: String, pw: String, done: (String?) -> Unit) = viewModelScope.launch {
        runCatching { api.login(LoginBody(email, pw)) }.onSuccess { afterLogin(it.token); done(null) }.onFailure { done(msg(it)) }
    }

    fun signup(name: String, email: String, pw: String, age: Int?, conds: List<String>, station: String, done: (String?) -> Unit) =
        viewModelScope.launch {
            runCatching { api.signup(SignUpBody(email, name, pw, s.lang, age, conds, station)) }
                .onSuccess { afterLogin(it.token); done(null) }.onFailure { done(msg(it)) }
        }

    fun forgot(email: String, done: (String?) -> Unit) = viewModelScope.launch {
        runCatching { api.forgot(ForgotBody(email)) }.onSuccess { done(null) }.onFailure { done(msg(it)) }
    }

    fun reset(email: String, code: String, pw: String, done: (String?) -> Unit) = viewModelScope.launch {
        runCatching { api.reset(ResetBody(email, code, pw)) }.onSuccess { afterLogin(it.token); done(null) }.onFailure { done(msg(it)) }
    }

    fun logout(silent: Boolean = false) {
        _state.update { it.copy(me = null, diary = null, badges = null) }
        updateSettings({ it.copy(token = null, memberId = null) }, reload = !silent)
    }

    fun deleteAccount() = viewModelScope.launch {
        auth?.let { runCatching { api.deleteMe(it) } }
        logout()
    }

    // ---------------- family ----------------
    fun saveMember(id: Int?, b: MemberBody, done: (String?) -> Unit = {}) = viewModelScope.launch {
        val a = auth ?: return@launch done("login")
        runCatching { if (id == null) api.addMember(a, b) else api.updateMember(a, id, b) }
            .onSuccess { done(null); refreshAll() }.onFailure { done(msg(it)) }
    }

    fun deleteMember(id: Int) = viewModelScope.launch {
        val a = auth ?: return@launch
        runCatching { api.deleteMember(a, id) }.onSuccess { refreshAll() }
    }

    // ---------------- diary ----------------
    fun logSymptoms(symptoms: List<String>, done: (Int?) -> Unit) = viewModelScope.launch {
        val a = auth ?: return@launch
        val m = _state.value.member ?: return@launch
        runCatching { api.addDiary(a, DiaryBody(m.id, symptoms, null, _state.value.mode, s.demoPeriod, s.demoAt)) }
            .onSuccess { r ->
                done(r.aqi)
                runCatching { api.diary(a, m.id) }.onSuccess { d -> _state.update { it.copy(diary = d) } }
                runCatching { api.badges(a) }.onSuccess { b -> _state.update { it.copy(badges = b) } }
            }
    }

    // ---------------- push notifications ----------------
    private fun registerPush() {
        val a = auth ?: return
        if (FirebaseApp.getApps(ctx).isEmpty()) return            // google-services.json not added: push is off
        try {
            FirebaseMessaging.getInstance().token.addOnSuccessListener { token ->
                viewModelScope.launch {
                    Prefs.savePushToken(ctx, token)
                    runCatching { api.addDevice(a, DeviceBody(token)) }
                }
            }
        } catch (e: Exception) { /* push not available on this phone */ }
    }
}
