package com.example.myapplication

import android.Manifest
import android.content.pm.PackageManager
import android.media.MediaPlayer
import android.media.MediaRecorder
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.annotation.RequiresApi
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.material.Button
import androidx.compose.material.MaterialTheme
import androidx.compose.material.Surface
import androidx.compose.material.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.example.myapplication.ui.theme.MyApplicationTheme
import kotlinx.coroutines.launch
import kotlinx.coroutines.runBlocking
import okhttp3.*
import retrofit2.Retrofit
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.POST
import retrofit2.http.Path
import java.io.*
import java.util.concurrent.TimeUnit


interface AudioService{
    @POST("/")
    suspend fun sendAudio(@Body recordingData: MultipartBody): ResponseBody
    @GET("/{recordingname}")
    suspend fun recieveData(@Path("recordingname") recordingName: String): ResponseBody
}
class MainActivity : ComponentActivity() {
    var mediaRecorder: MediaRecorder? = null
    var mediaPlayer: MediaPlayer? = null
    private var output: String? = null
    private var outputFile: File? = null

    fun startRecording(mediaRecorder: MediaRecorder, output: String){
        Log.d("Testing output", output)
        mediaRecorder?.prepare()
        mediaRecorder?.start()
    }
    fun stopRecording(mediaRecorder: MediaRecorder){
        mediaRecorder?.stop()
        mediaRecorder?.release()
        mediaRecorder?.reset()

    }
    @RequiresApi(Build.VERSION_CODES.Q)
    fun sendRecording(recordingFile: File){
        val okHttpClient = OkHttpClient.Builder()
            .readTimeout(5, TimeUnit.MINUTES)
            .connectTimeout(5, TimeUnit.MINUTES)
            .build()
        val retrofitBuilder = Retrofit.Builder()
            .baseUrl("http://10.131.212.122:5301")
            .client(okHttpClient)
            .build()
        val recordingRequestBody = MultipartBody.Builder().setType(MultipartBody.FORM)
            .addFormDataPart("file", recordingFile.name,RequestBody.create(MediaType.parse("audio/*"),recordingFile))
            .build()
//        val testString = "Hello World"
//        val recordingRequestBody = RequestBody.create(MediaType.parse("text"),testString)
        val recordingService = retrofitBuilder.create(AudioService::class.java)
        //val filePartBody = MultipartBody.Part.createFormData("file", recordingFile.name, recordingFile.asRequestBody())
        runBlocking {
            launch { recordingService.sendAudio(recordingRequestBody)
            recordingService.recieveData(recordingFile.name)}
        }


    }

    @RequiresApi(Build.VERSION_CODES.S)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED && ContextCompat.checkSelfPermission(this,
                Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            val permissions = arrayOf(Manifest.permission.RECORD_AUDIO, Manifest.permission.WRITE_EXTERNAL_STORAGE, Manifest.permission.READ_EXTERNAL_STORAGE)
            ActivityCompat.requestPermissions(this, permissions,0)
        }
        mediaRecorder = MediaRecorder(applicationContext)
        output = applicationContext.getExternalFilesDir(null)!!.absolutePath + "/recording.3gp"
        outputFile = File(output)
        outputFile!!.createNewFile()
        mediaRecorder?.setAudioSource(MediaRecorder.AudioSource.MIC)
        mediaRecorder?.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP)
        mediaRecorder?.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
        mediaRecorder?.setOutputFile(outputFile)
        setContent {
            MyApplicationTheme {
                // A surface container using the 'background' color from the theme
                Surface(modifier = Modifier, color = MaterialTheme.colors.background) {
                    SpeechTest(startonClick = {startRecording(mediaRecorder!!, output!!)},
                        stoponClick = {stopRecording(mediaRecorder!!)},
                        sendOnClick = {sendRecording(outputFile!!)}
                    )
                }
            }
        }
    }
}

@Composable
fun SpeechTest(startonClick: () -> Unit, stoponClick: () -> Unit, sendOnClick: () -> Unit) {
Column() {
    Button(onClick = startonClick) {
        Text("Start Recording")

    }
    Button(onClick = stoponClick) {
        Text("Stop Recording")

    }
    Button(onClick = sendOnClick){
        Text("Send Recording to Server")
    }
}
}

@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    MyApplicationTheme {
        SpeechTest({},{},{})
    }
}