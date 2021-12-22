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
let roomName;
let myPeerConnection;
let SID
let mediaRecorder;

let recLength = 0;
let recBuffers = [];

let bufferLen = 4096;
let numChannels = 1;
let mimeType = 'audio/wav';

window.AudioContext = window.AudioContext || window.webkitAudioContext;
let audio_context = new AudioContext();

let audio_stream;

async function getMedia(){
    try{
        myStream = await navigator.mediaDevices.getUserMedia({
            audio:{
                sampleRate:16000,
                sampleSize:16,
                channelCount:1,
            }
        });
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
    socket.emit('leave_room',roomName);
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
    console.log('MEDIA DONE')
    makeConnection();
    console.log("initCall done!");
}

async function handleWelcomeSubmit(e){
    e.preventDefault();
    const input = welcomeForm.querySelector("input");
    await initCall();
    socket.emit("join_room",{'room':input.value});
    roomName = input.value;
    input.value = "";
}

welcomeForm.addEventListener("submit",handleWelcomeSubmit);
socket.on('joined',(sid)=>{
    console.log(sid)
    SID=sid.toString();
    mediaRecorder=new MediaRecorder(myStream);
    mediaRecorder.ondataavailable=async (e)=>{
        socket.emit('audio_stream',SID,e.data,roomName);
    }
    mediaRecorder.start(63);
})
socket.on("welcome",async ()=>{
    console.log("got welcome");
    const offer = await myPeerConnection.createOffer();
    myPeerConnection.setLocalDescription(offer);
    console.log("sent the offer");
    socket.emit("offer",offer,roomName);
})

socket.on("offer",async (offer)=>{
    console.log("received the offer");
    myPeerConnection.setRemoteDescription(offer);
    const answer=await myPeerConnection.createAnswer();
    myPeerConnection.setLocalDescription(answer);
    socket.emit("answer",answer,roomName);
    console.log("sent the answer");
})

socket.on("answer",(answer)=>{
    console.log("received the answer");
    myPeerConnection.setRemoteDescription(answer);
})

socket.on("ice",(ice)=>{
    console.log("received candidate");
    myPeerConnection.addIceCandidate(ice);
})

socket.on("infer",(data)=>{
    console.log('Received infer',data);
    displayer.innerText+=` ${data}`;
})
socket.on('err',(data)=>{
    console.log('Received err',data);
    displayer.innerText+=` ${data}`;
})

//RTC Code
function makeConnection(){
    myPeerConnection = new RTCPeerConnection({
        iceServers:[
            {
                urls:[
                    "stun:stun.l.google.com:19302",
                    "stun:stun1.l.google.com:19302",
                    "stun:stun2.l.google.com:19302",
                    "stun:stun3.l.google.com:19302",
                    "stun:stun4.l.google.com:19302",
                ],
            },
        ]
    });
    myPeerConnection.addEventListener("icecandidate",handleICE);
    myPeerConnection.addEventListener("addstream",handleStream);
    myPeerConnection.addEventListener("addtrack",handleTrack);
    myStream
        .getAudioTracks()
        .forEach((track) => {myPeerConnection.addTrack(track,myStream)});

}

function handleICE(event){
    console.log("sent candidate");
    socket.emit("ice",event.candidate,roomName);
}

function handleStream(event){
    console.log("received track");
    remoteAudio.srcObject = event.stream;
}

function handleTrack(event){
    setTimeout(console.log("Track",event),10000);
}
