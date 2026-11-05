package com.airsathi.app.data

import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.POST
import retrofit2.http.PUT
import retrofit2.http.Path
import retrofit2.http.Query
import java.util.concurrent.TimeUnit

/** Every backend endpoint the app uses. The backend's own list is at <server>/docs. */
interface Api {
    @GET("api/stations")
    suspend fun stations(@Query("mode") mode: String, @Query("period") period: String, @Query("at") at: String?): List<Station>

    @GET("api/stations/{id}")
    suspend fun station(@Path("id") id: String, @Query("mode") mode: String, @Query("period") period: String,
                        @Query("at") at: String?): StationDetail

    @GET("api/advice")
    suspend fun advice(@Header("Authorization") auth: String?, @Query("station") station: String, @Query("mode") mode: String,
                       @Query("period") period: String, @Query("at") at: String?, @Query("lang") lang: String,
                       @Query("member_id") memberId: Int?, @Query("age") age: Int?, @Query("conditions") conditions: String?): AdviceResp

    @GET("api/plan")
    suspend fun plan(@Query("station") station: String, @Query("activity") activity: String, @Query("mode") mode: String,
                     @Query("period") period: String, @Query("at") at: String?): PlanResp

    @GET("api/summary/weekly")
    suspend fun weekly(@Query("station") station: String, @Query("mode") mode: String, @Query("period") period: String,
                       @Query("at") at: String?): Weekly

    @GET("api/demo/periods") suspend fun periods(): List<Period>
    @GET("api/status") suspend fun status(): Status
    @GET("api/tips/today") suspend fun tip(@Query("lang") lang: String): Msg

    @POST("api/auth/signup") suspend fun signup(@Body b: SignUpBody): TokenResp
    @POST("api/auth/login") suspend fun login(@Body b: LoginBody): TokenResp
    @POST("api/auth/forgot") suspend fun forgot(@Body b: ForgotBody): OkResp
    @POST("api/auth/reset") suspend fun reset(@Body b: ResetBody): TokenResp

    @GET("api/me") suspend fun me(@Header("Authorization") auth: String): Me
    @PUT("api/me") suspend fun updateMe(@Header("Authorization") auth: String, @Body b: MeBody): Me
    @DELETE("api/me") suspend fun deleteMe(@Header("Authorization") auth: String): OkResp

    @POST("api/members") suspend fun addMember(@Header("Authorization") auth: String, @Body b: MemberBody): Member
    @PUT("api/members/{id}") suspend fun updateMember(@Header("Authorization") auth: String, @Path("id") id: Int, @Body b: MemberBody): Member
    @DELETE("api/members/{id}") suspend fun deleteMember(@Header("Authorization") auth: String, @Path("id") id: Int): OkResp

    @POST("api/diary") suspend fun addDiary(@Header("Authorization") auth: String, @Body b: DiaryBody): DiarySaved
    @GET("api/diary") suspend fun diary(@Header("Authorization") auth: String, @Query("member_id") memberId: Int?): DiaryResp

    @POST("api/devices") suspend fun addDevice(@Header("Authorization") auth: String, @Body b: DeviceBody): OkResp
    @GET("api/badges") suspend fun badges(@Header("Authorization") auth: String): Badges

    companion object {
        fun create(baseUrl: String): Api {
            val url = if (baseUrl.endsWith("/")) baseUrl else "$baseUrl/"
            // Render's free server sleeps when unused; the first request can take up to a minute to wake it.
            val client = OkHttpClient.Builder()
                .connectTimeout(60, TimeUnit.SECONDS)
                .readTimeout(90, TimeUnit.SECONDS)
                .build()
            return Retrofit.Builder().baseUrl(url).client(client)
                .addConverterFactory(GsonConverterFactory.create()).build().create(Api::class.java)
        }
    }
}
