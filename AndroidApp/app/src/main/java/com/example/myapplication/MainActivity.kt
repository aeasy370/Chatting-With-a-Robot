package com.example.myapplication

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import android.media.MediaPlayer
import android.media.MediaRecorder
import android.os.Build
import android.os.Bundle
import android.os.Environment
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.annotation.RequiresApi
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
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
import java.io.File


class MainActivity : ComponentActivity() {
    val context: Context? = null
    var mediaRecorder: MediaRecorder? = null
    var mediaPlayer: MediaPlayer? = null
    private var output: String? = null
    private var outputFile: File? = null
    fun startRecording(mediaRecorder: MediaRecorder){
        mediaRecorder?.prepare()
        mediaRecorder?.start()
    }
    fun stopRecording(mediaRecorder: MediaRecorder){
        mediaRecorder?.stop()
        mediaRecorder?.release()
    }
    @RequiresApi(Build.VERSION_CODES.O)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (ContextCompat.checkSelfPermission(this,
                Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED && ContextCompat.checkSelfPermission(this,
                Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            val permissions = arrayOf(android.Manifest.permission.RECORD_AUDIO, android.Manifest.permission.WRITE_EXTERNAL_STORAGE, android.Manifest.permission.READ_EXTERNAL_STORAGE)
            ActivityCompat.requestPermissions(this, permissions,0)
        }
        mediaRecorder = MediaRecorder()
        output = Environment.getExternalStorageDirectory().absolutePath + "/recording.mp3"
        outputFile = File(output)
        mediaRecorder?.setAudioSource(MediaRecorder.AudioSource.MIC)
        mediaRecorder?.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
        mediaRecorder?.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
        mediaRecorder?.setOutputFile(outputFile)
        setContent {
            MyApplicationTheme {
                // A surface container using the 'background' color from the theme
                Surface(modifier = Modifier.padding(24.dp), color = MaterialTheme.colors.background) {
                    SpeechTest(startonClick = {startRecording(mediaRecorder!!)},
                               stoponClick = {stopRecording(mediaRecorder!!)})
                }
            }
        }
    }
}

@Composable
fun SpeechTest(startonClick: () -> Unit, stoponClick: () -> Unit) {
Column() {
    Button(onClick = startonClick) {
        Text("Start Recording")

    }
    Button(onClick = stoponClick) {
        Text("Stop Recording")

    }
}
}

@Preview(showBackground = true)
@Composable
fun DefaultPreview() {
    MyApplicationTheme {
        SpeechTest({},{})
    }
}