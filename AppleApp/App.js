import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { Audio } from 'expo-av';
import { Button, StyleSheet, Text, View } from 'react-native';
import * as Sharing from 'expo-sharing';

export default function App() {
  const [recording, setRecording] = React.useState();
  const [recordings, setRecordings] = React.useState([]);
  const[message, setMessage] = React.useState("");
  async function startRecording(){
    try {
      const permission = await Audio.requestPermissionsAsync();
      if (permission.status === "granted"){
        await Audio.setAudioModeAsync({
          allowsRecordingIOS: true,
          playsInSilentModeIOS: true,
        });

        const opts = Audio.RecordingOptionsPresets.HIGH_QUALITY;
        opts.extension = '.mp3';
        const { recording } = await Audio.Recording.createAsync(
          opts
        );

        setRecording(recording);
      } else{
        setMessage("Please grant permission for microphone access");
      }
    } catch (err){
      console.error('Failed to start recording', err);
    }
  }

  async function stopRecording(){
    setRecording(undefined);
    await recording.stopAndUnloadAsync();

    let updatedRecordings = [...recordings];
    const { sound, status } = await recording.createNewLoadedSoundAsync();
    updatedRecordings.push({
      sound: sound,
      duration: getDurationFormatted(status.durationMillis),
      file: recording.getURI()
    });

    setRecordings(updatedRecordings);
  }

  function getDurationFormatted(millis) {
    const minutes = millis / 1000 / 60;
    const minutesDisplay = Math.floor(minutes);
    const seconds = Math.round((minutes - minutesDisplay) * 60);
    const secondsDisplay = seconds < 10 ? `0${seconds}` : seconds;
    return `${minutesDisplay}:${secondsDisplay}`;
  }

  function getRecordingLines() {
    return recordings.map((recordingLine, index) => {
      return (
        <View key={index} style={styles.row}>
          <Text style={styles.fill}>Recording {index + 1} - {recordingLine.duration}</Text>
          <Button style={styles.button} onPress={() => recordingLine.sound.replayAsync()} title="Play"></Button>
          <Button style={styles.button} onPress={() => Sharing.shareAsync(recordingLine.file)} title="Share"></Button>
        </View>
      );
    });
  }


  return (
    
    <View style={styles.container}>
      <Text>{message}</Text>
      {/*Wrapper for buttons and title*/}
      <View style={styles.buttonWrapper}>
        <Text style={styles.sectionTitle}>Hit a button to record or to send to server!</Text>
        {/*Button for Voice Recording*/}
        <Button
          title={recording ? 'Stop Recording' : 'Start Recording'}
          onPress={recording ? stopRecording : startRecording}
        />
        {getRecordingLines()}
        <Button
          title="Send to Server"
        />
      </View>
      
      <StatusBar style="auto" />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0d0d0d',
  },
  buttonWrapper:{
    paddingTop: 80,
    paddingHorizontal: 20,
  },
  sectionTitle: {
    fontSize: 24,
    color: '#fafafa',
    fontWeight: 'bold',
  },
  fill:{
    color: '#fafafa'
  }
});
