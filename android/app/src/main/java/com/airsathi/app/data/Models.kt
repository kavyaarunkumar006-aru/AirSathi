package com.airsathi.app.data

// Shapes of the JSON that the AirSathi backend sends. Every field is nullable so a missing value never crashes the app.

data class Category(val key: String? = null, val name: String? = null, val color: String? = null, val index: Int? = null)

data class Now(
    val ts: String? = null, val aqi: Double? = null, val category: Category? = null, val dominant: String? = null,
    val tier: String? = null, val label: String? = null, val age_h: Double? = null,
)

data class Forecast(
    val h: Int? = null, val target: String? = null, val aqi: Int? = null, val lo: Int? = null, val hi: Int? = null,
    val category: Category? = null, val confidence: String? = null, val method: String? = null,
)

data class Station(
    val id: String = "", val name: String? = null, val city: String? = null,
    val lat: Double? = null, val lon: Double? = null, val now: Now? = null,
)

data class StationDetail(
    val station: Station? = null, val mode: String? = null, val period: String? = null, val period_label: String? = null,
    val now: Now? = null, val forecast: List<Forecast>? = null,
)

data class Msg(val id: String? = null, val text: String? = null, val source: String? = null)

data class Advice(
    val aqi: Int? = null, val category: Category? = null, val groups: List<String>? = null, val vulnerable: Boolean? = null,
    val threshold: Int? = null, val headline: Msg? = null, val actions: List<Msg>? = null, val tip: Msg? = null,
    val doctor: Msg? = null, val alert: Boolean? = null,
)

data class AdviceResp(
    val now: Now? = null, val advice_now: Advice? = null, val advice_next12h: Advice? = null,
    val worst_next12h: Forecast? = null, val disclaimer: Msg? = null, val sources: Map<String, String>? = null,
)

data class PlanWindow(val start: String? = null, val end: String? = null, val level: Int? = null)
data class PlanResp(val mode: String? = null, val activity: String? = null, val windows: List<PlanWindow>? = null,
                    val worst: PlanWindow? = null, val message_id: String? = null)

data class WeeklyDay(val day: String? = null, val aqi: Int? = null, val category: Category? = null)
data class Weekly(val days: List<WeeklyDay>? = null, val cleanest: WeeklyDay? = null, val worst: WeeklyDay? = null)

data class Period(val id: String = "", val label: String? = null, val note: String? = null, val start: String? = null, val end: String? = null)

data class TokenResp(val token: String? = null)

data class Member(
    val id: Int = 0, val name: String? = null, val age: Int? = null, val conditions: List<String>? = null,
    val station: String? = null, val is_self: Boolean? = null, val alerts_on: Boolean? = null, val groups: List<String>? = null,
    val alert_threshold: Int? = null, val default_threshold: Int? = null,
)

data class Me(val id: Int = 0, val email: String? = null, val name: String? = null, val lang: String? = null,
              val is_admin: Boolean? = null, val members: List<Member>? = null)

data class DiaryEntry(val id: Int = 0, val ts: String? = null, val symptoms: List<String>? = null, val aqi: Int? = null)
data class SymptomCount(val symptom: String? = null, val count: Int? = null, val avg_aqi: Int? = null)
data class DiaryResp(val entries: List<DiaryEntry>? = null, val summary: List<SymptomCount>? = null, val symptoms: List<String>? = null)
data class DiarySaved(val id: Int? = null, val aqi: Int? = null)

data class Badge(val id: String? = null, val title: String? = null, val description: String? = null, val earned: Boolean? = null)
data class Badges(val streak: Int? = null, val badges: List<Badge>? = null)

data class StatusStation(val id: String? = null, val name: String? = null, val tier: String? = null, val label: String? = null,
                         val ts: String? = null, val updated_at: String? = null)
data class Status(val stations: List<StatusStation>? = null)

// request bodies
data class SignUpBody(val email: String, val name: String, val password: String, val lang: String,
                      val age: Int?, val conditions: List<String>, val station: String)
data class LoginBody(val email: String, val password: String)
data class ForgotBody(val email: String)
data class ResetBody(val email: String, val code: String, val password: String)
data class MemberBody(val name: String, val age: Int?, val conditions: List<String>, val station: String,
                      val alert_threshold: Int?, val alerts_on: Boolean)
data class DiaryBody(val member_id: Int, val symptoms: List<String>, val note: String?, val mode: String, val period: String, val at: String?)
data class DeviceBody(val token: String, val platform: String = "android")
data class MeBody(val name: String? = null, val lang: String? = null)
data class OkResp(val ok: Boolean? = null)
