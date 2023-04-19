import { StatusBar } from 'expo-status-bar';
import React from 'react';
import { Audio } from 'expo-av';
import { Button, StyleSheet, Text, View, TextInput } from 'react-native';
import * as Sharing from 'expo-sharing';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import AsyncStorage from '@react-native-async-storage/async-storage';

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


  function SettingsScreen ({navigation}){
    /* Declaration of Settings Screen */
    const saveServer = async() => {
      /* Saving server name */ 
      try {
        AsyncStorage.setItem('Server', JSON.stringify(text));
      } catch (error) {
        console.log(error);
        alert('Error with Saving Server');
      }
    };
  
    const getServer = async() => {
      /* Get Server name from save */
      try {
        const servname = JSON.parse(await AsyncStorage.getItem('Server'));
        onChangeText(servname);
      } catch (error) {
        console.log(error);
        alert('Error with Loading Server');
      }
    };
    const savePort = async() => {
      /* Save Port Number */
      try {
        AsyncStorage.setItem('Port', JSON.stringify(number));
      } catch (error) {
        console.log(error);
        alert('Error with Saving Port');
      }
    };
  
    const getPort = async() => {
      /* Get Port Number From Save */
      try {
        const portname = JSON.parse(await AsyncStorage.getItem('Port'));
        onChangeNumber(portname);
      } catch (error) {
        console.log(error);
        alert('Error with Loading Port');
      }
    };

    React.useEffect(() => {
      /*Get Server and Port on Boot up */
      getServer();
      getPort();
    }, []);
    const [text, onChangeText] = React.useState('');
    const [number, onChangeNumber] = React.useState('');
    return(
      <View style={{ flex: 1, alignItems: 'center', justifyContent: 'center' }}>
        <TextInput
        style={styles.input}
        onChangeText={onChangeText}
        placeholder='Server'
        value={text}
      />
      <Button
      title="Save server name"
      onPress={saveServer}
      />
     <TextInput
        style={styles.input}
        onChangeText={onChangeNumber}
        value={number}
        placeholder="Port"
        keyboardType="numeric"
      />
      <Button
      title="Save Port Number"
      onPress={savePort}
      />
      <Button
      title="Back to Home"
      onPress={() => navigation.navigate('Home')}
      />
    </View>
    );
  }
  function HomeScreen ({navigation}) {
    /* Declaration of Home Screen */
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
          <Button
          title="Go to Settings"
          onPress={() => navigation.navigate('Settings')}
          />
        </View>
        <StatusBar style="light" />
      </View>
    );
  }
  const Stack = createNativeStackNavigator();
  return (
    <NavigationContainer>
    <Stack.Navigator>
      <Stack.Screen name="Home" component={HomeScreen} /> 
      <Stack.Screen name="Settings" component={SettingsScreen} />   
      </Stack.Navigator>
  </NavigationContainer>
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
