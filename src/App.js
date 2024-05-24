
import './App.css';
import { Button } from '@mui/material';
import React, { useCallback, useEffect, useState } from 'react';

function App() {
  
    const [status,setStatus] = useState()
      //================= CONFIG =================
    // Global Variables
    let websocket_uri = 'ws://127.0.0.1:8000/record';
    let bufferSize = 4096,
        AudioContext,
        context,
        processor,
        input,
        globalStream,
        websocket;

    // Initialize WebSocket
    initWebSocket();

    //================= RECORDING =================
    function startRecording() {
        // streamStreaming = true;
        AudioContext = window.AudioContext || window.webkitAudioContext;
        context = new AudioContext({
          // if Non-interactive, use 'playback' or 'balanced' // https://developer.mozilla.org/en-US/docs/Web/API/AudioContextLatencyCategory
          latencyHint: 'interactive',
        });
        processor = context.createScriptProcessor(bufferSize, 1, 1);
        processor.connect(context.destination);
        context.resume();      
        var handleSuccess = function (stream) {
          globalStream = stream;
          input = context.createMediaStreamSource(stream);
          input.connect(processor);
      
          processor.onaudioprocess = function (e) {
            var left = e.inputBuffer.getChannelData(0);
            var left16 = downsampleBuffer(left, 44100, 16000);
            websocket.send(left16);
          };
        };
      
        navigator.mediaDevices.getUserMedia({audio: true, video: false}).then(handleSuccess);
    } // closes function startRecording()

    function stopRecording() {
        // let streamStreaming = false;
      
        let track = globalStream.getTracks()[0];
        track.stop();
      
        input.disconnect(processor);
        processor.disconnect(context.destination);
        context.close().then(function () {
          input = null;
          processor = null;
          context = null;
          AudioContext = null;
        });
    } // closes function stopRecording()

    function initWebSocket() {
        // Create WebSocket
        websocket = new WebSocket(websocket_uri);
        //console.log("Websocket created...");
      
        // WebSocket Definitions: executed when triggered webSocketStatus
        websocket.onopen = function() {
          console.log("connected to server");
          //websocket.send("CONNECTED TO YOU");
          setStatus('Connected')
        }
        
        websocket.onclose = function(e) {
          console.log("connection closed (" + e.code + ")");
          setStatus('Disconnected')
        }
        
        websocket.onmessage = function(e) {
          console.log(e.data);
        }
    } 

    function downsampleBuffer (buffer, sampleRate, outSampleRate) {
        if (outSampleRate == sampleRate) {
          return buffer;
        }
        if (outSampleRate > sampleRate) {
          throw 'downsampling rate show be smaller than original sample rate';
        }
        var sampleRateRatio = sampleRate / outSampleRate;
        var newLength = Math.round(buffer.length / sampleRateRatio);
        var result = new Int16Array(newLength);
        var offsetResult = 0;
        var offsetBuffer = 0;
        while (offsetResult < result.length) {
          var nextOffsetBuffer = Math.round((offsetResult + 1) * sampleRateRatio);
          var accum = 0,
            count = 0;
          for (var i = offsetBuffer; i < nextOffsetBuffer && i < buffer.length; i++) {
            accum += buffer[i];
            count++;
          }
      
          result[offsetResult] = Math.min(1, accum / count) * 0x7fff;
          offsetResult++;
          offsetBuffer = nextOffsetBuffer;
        }
        return result.buffer;
    } // closes function downsampleBuffer()
  return (
    <div className="App">
      <Button onClick={startRecording} variant="contained">Start Recording</Button>
      <Button onClick={stopRecording} variant="contained">Stop Recording</Button>
      <div>Connection status {status}</div>
    </div>
  );
}

export default App;
