const socket = io();

const remoteAudio =  document.querySelector("audio");
const call = document.querySelector('#call');

//const callBtn = document.querySelector("#callbtn");
const hangupBtn = document.querySelector("#hangup");
const muteBtn = document.querySelector("#mute");
const displayer = document.querySelector("#displayer");
call.hidden=true;

let myStream;
let remoteStream;
let muted = false;
const roomName=1;
let myPeerConnection;
let SID
let mediaRecorder;
let chunks=[];

async function getMedia(){
    try{
        myStream = await navigator.mediaDevices.getUserMedia({
            audio:{
                sampleRate:16000,
                sampleSize:16,
                channelCount:1,
            }
        });
        remoteAudio.srcObject = myStream;
    } catch(error){
        console.log(error);
    }
}

/* function handleCallClick(){
    callBtn.style.display = "none";
    hangupBtn.style.display = "block";
    muteBtn.style.display = "block";

} */
function handleHangupClick(){
    hangupBtn.style.display = "none";
    muteBtn.style.display = "none";
    mediaRecorder.stop();
    socket.emit('leave_room',SID,roomName);
}
function handleMuteClick(){
    myStream
        .getAudioTracks()
        .forEach((track)=>{track.enabled = !track.enabled});
    if(!muted){
        muteBtn.innerText = "Unmute";
        muted = true;
    }else{
        muteBtn.innerText = "Mute";
        muted = false;
    }
}
hangupBtn.addEventListener("click",handleHangupClick);
muteBtn.addEventListener("click",handleMuteClick);

//Welcome code
const welcome= document.querySelector('#welcome');
const welcomeForm=welcome.querySelector("form");

async function initCall(){
    welcome.hidden = true;
    call.hidden = false;
    await getMedia();
    console.log("initCall done!");
}

async function handleWelcomeSubmit(e){
    e.preventDefault();
    const input = welcomeForm.querySelector("input");
    await initCall();
    socket.emit("join_room",SID,{'room':roomName});
    input.value = "";
}


welcomeForm.addEventListener("submit",handleWelcomeSubmit);

socket.on('connected',()=>{
    console.log("connected");
})

socket.on('welcome',()=>{
    mediaRecorder=new MediaRecorder(myStream);
    mediaRecorder.ondataavailable=async (e)=>{
        chunks.push(e.data);
        var blob = new Blob(chunks, {
            type: "audio/wav"
        });
        chunks=[];
        var xmlhttp = new XMLHttpRequest();
        var url = "https://115.85.182.137:6017/stream/";
        xmlhttp.open("POST", url, true);
        xmlhttp.setRequestHeader("Content-type", "audio/wav");
        xmlhttp.setRequestHeader('Access-Control-Allow-Origin', '*')
        xmlhttp.send(blob);
        // var arr = await blob.arrayBuffer();
        // if (arr.byteLength % 2 ===1) {
        //     arr+='\x00';
        // }
        // var buffer = new Int16Array(arr);
        //socket.emit('audio',SID,blob,roomName);
    }
    mediaRecorder.start(1000);
    socket.emit('start_stream')
})

socket.on("infer",(data)=>{
    console.log('Received infer',data);
    displayer.innerText+=` ${data}`;
})