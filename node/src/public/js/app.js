const socket = io();

const remoteAudio =  document.querySelector("audio");
const call = document.querySelector('#call');

const callBtn = document.querySelector("#callbtn");
const hangupBtn = document.querySelector("#hangup");
const muteBtn = document.querySelector("#mute");

call.hidden=true;

let myStream;
let remoteStream;
let muted = false;
let roomName;
let myPeerConnection;

async function getMedia(){
    try{
        myStream = await navigator.mediaDevices.getUserMedia({
            audio:{
                sampleRate:16000,
                sampleSize:16,
                channelCount:1,
                echoCancellation:true,
                noiseSuppression:true,
                autoGainControl:true
            }
        });
    } catch(error){
        console.log(error);
    }
}

function handleCallClick(){
    callBtn.style.display = "none";
    hangupBtn.style.display = "block";
    muteBtn.style.display = "block";

}
function handleHangupClick(){
    callBtn.style.display = "block";
    hangupBtn.style.display = "none";
    muteBtn.style.display = "none";
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
callBtn.addEventListener("click",handleCallClick);
hangupBtn.addEventListener("click",handleHangupClick);
muteBtn.addEventListener("click",handleMuteClick);

//Welcome code
const welcome= document.querySelector('#welcome');
const welcomeForm=welcome.querySelector("form");

async function initCall(){
    welcome.hidden = true;
    call.hidden = false;
    await getMedia();
    makeConnection();
    console.log("initCall done!");
}

async function handleWelcomeSubmit(e){
    e.preventDefault();
    const input = welcomeForm.querySelector("input");
    await initCall();
    socket.emit("join_room",input.value);
    roomName = input.value;
    input.value = "";
}
welcomeForm.addEventListener("submit",handleWelcomeSubmit);

socket.on("welcome",async ()=>{
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

//RTC Code
function makeConnection(){
    myPeerConnection = new RTCPeerConnection();
    myPeerConnection.addEventListener("icecandidate",handleICE);
    myPeerConnection.addEventListener("addstream",handleTrack);
    myStream
        .getAudioTracks()
        .forEach((track) => {myPeerConnection.addTrack(track,myStream)});

}

function handleICE(event){
    console.log("sent candidate");
    socket.emit("ice",event.candidate,roomName);
}

function handleTrack(event){
    console.log("received track");
    remoteAudio.srcObject = event.stream;
}
