package com.example.myapplication

import android.Manifest
import android.annotation.SuppressLint
import android.content.pm.PackageManager
import android.media.MediaPlayer
import android.media.MediaRecorder
import android.os.Build
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.annotation.RequiresApi
import androidx.compose.foundation.layout.*
import androidx.compose.material.*
import androidx.compose.runtime.Composable
import androidx.compose.runtime.MutableState
import androidx.compose.runtime.mutableStateOf
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
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

    }
    @RequiresApi(Build.VERSION_CODES.Q)
    fun sendRecording(recordingFile: File){
        val okHttpClient = OkHttpClient.Builder()
            .readTimeout(30, TimeUnit.SECONDS)
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
        val retrofitBuilder = Retrofit.Builder()
            .baseUrl("http://216.96.192.192:25623/ ")
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
            launch { recordingService.sendAudio(recordingRequestBody) }
        }


    }

    fun recieveRecording(oFile: File, text: MutableState<String>){
        val okHttpClient = OkHttpClient.Builder()
            .readTimeout(30, TimeUnit.SECONDS)
            .connectTimeout(30, TimeUnit.SECONDS)
            .build()
        val retrofitBuilder = Retrofit.Builder()
            .baseUrl("http://216.96.192.192:25623/ ")
            .client(okHttpClient)
            .build()

        val recordingService = retrofitBuilder.create(AudioService::class.java)
        runBlocking {
            launch {  val response = recordingService.recieveData(oFile.name)
            text.value = response.string()}
        }

    }

    @RequiresApi(Build.VERSION_CODES.Q)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED && ContextCompat.checkSelfPermission(this,
                Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            val permissions = arrayOf(Manifest.permission.RECORD_AUDIO, Manifest.permission.WRITE_EXTERNAL_STORAGE, Manifest.permission.READ_EXTERNAL_STORAGE)
            ActivityCompat.requestPermissions(this, permissions,0)
        }
        val text = mutableStateOf("text")
        mediaRecorder = MediaRecorder()
        output = applicationContext.getExternalFilesDir(null)!!.absolutePath + "/recording.3gp"
        outputFile = File(output)
        outputFile!!.createNewFile()
        mediaRecorder?.setAudioSource(MediaRecorder.AudioSource.MIC)
        mediaRecorder?.setOutputFormat(MediaRecorder.OutputFormat.THREE_GPP)
        mediaRecorder?.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
        mediaRecorder?.setOutputFile(outputFile)

        setContent {
            MyApplicationTheme {

                Surface(modifier = Modifier
                    .fillMaxHeight()
                    .fillMaxWidth(), color = Color(0xFFFFFFF)) {
                    SpeechTest(startonClick = {startRecording(mediaRecorder!!, output!!)},
                        stoponClick = {stopRecording(mediaRecorder!!)},
                        sendOnClick = {sendRecording(outputFile!!)},
                        recieveOnClick = {recieveRecording(outputFile!!, text)},
                        text = text
                    )
                }
            }
        }
    }
}


@Composable
fun SpeechTest(startonClick: () -> Unit, stoponClick: () -> Unit, sendOnClick: () -> Unit, recieveOnClick: () -> Unit, text: MutableState<String>){

    Column {
    Button(onClick = startonClick,colors = ButtonDefaults.outlinedButtonColors(backgroundColor = Color(0xFFFF8200))) {
        Text("Start Recording", color = Color.White)

    }
    Button(onClick = stoponClick, colors = ButtonDefaults.outlinedButtonColors(backgroundColor = Color(0xFFFF8200))) {
        Text("Stop Recording", color = Color.White)

    }
    Button(onClick = sendOnClick, colors = ButtonDefaults.outlinedButtonColors(backgroundColor = Color(0xFFFF8200))){
        Text("Send Recording to Server", color = Color.White)
    }
        Button(onClick = recieveOnClick, colors = ButtonDefaults.outlinedButtonColors(backgroundColor = Color(0xFFFF8200))){
            Text("Receive Data", color = Color.White)
        }
    Spacer(modifier = Modifier.height(20.dp))
    Text(text.value)
    Spacer(modifier = Modifier.height(20.dp))
    Button(onClick = {}, colors = ButtonDefaults.outlinedButtonColors(backgroundColor = Color.White)){
        Text("Settings", color = Color(0xFFFF8200))
    }

}
}

@SuppressLint("UnrememberedMutableState")
@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    val text = mutableStateOf("text")
    MyApplicationTheme {
        SpeechTest({},{},{},{},text)
    }
}