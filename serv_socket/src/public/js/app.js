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

async function initCall(){
    call.hidden = false;
    await getMedia();
    console.log("initCall done!");
}
socket.on('connect',async ()=>{
    await initCall();
    console.log("connected");
})

socket.on("infer",(data)=>{
    console.log('Received infer',data);
    displayer.innerText+=` ${data}`;
})