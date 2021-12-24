const socket = io();
// 이름 클릭
const contact = document.getElementsByClassName("contact-name");
const before_call = document.getElementsByClassName("before-call")[0];
const call_success = document.getElementsByClassName("call-success")[0];
const exit_call = document.getElementsByClassName("end-call")[0];
const translated_text = document.getElementsByClassName("call-text")[0];
const underscore = document.getElementById("underscore");
/**
 * 이벤트 함수
 */
// 이름 클릭 시 Trigger Event
function onContactClickHandler() {
    before_call.style.display = "none";
    call_success.style.display = "block";
    exit_call.style.display = "block";
    socket.emit("join");
}
// 통화 종료 시 Trigger Event
function onEndCallClickHandler() {
    final_text=`${translated_text.innerText}`;
    translated_text.innerText = "";
    exit_call.style.display = "none";
    translated_text.style.height="80%";
    socket.emit('leave',final_text);
}

function onExitClickHandler() {
    translated_text.innerText = "";
    before_call.style.display = "block";
    call_success.style.display = "none";
    exit_call.style.display = "none";
    call_success.removeEventListener("click", onExitClickHandler,false);
}
/**
 * 이벤트 넣기
 */
for(var i = 0; i < contact.length; ++i) {
    contact[i].addEventListener('click', onContactClickHandler, false);
}
exit_call.addEventListener('click', onEndCallClickHandler, false);
/**
 * 서버 데이터
 */
socket.on("infer", (data) => {
    console.log('Received infer', data);
    startTextAnimation(translated_text.innerText+" ", `${data}`);
})

socket.on("final", (data) =>{
    console.log('Received leave', data);
    translated_text.innerText = data;
    call_success.addEventListener("click", onExitClickHandler,false);
})


/**
 * Text animation
 */
function startTextAnimation(prev_words, words) {
    var letterCount = 1;
    translated_text.innerText = (prev_words + words.substring(0, letterCount));
    letterCount++;
    let character_display = window.setInterval(function() {
        translated_text.innerText = (prev_words + words.substring(0, letterCount));
        letterCount++;
        console.log(words);
        if(letterCount >= words.length + 1) {
            window.clearInterval(character_display);
        }
    }, 25);
}

function displayUnderscore() {
    var visible = true;
    window.setInterval(function() {
        if (visible === true) {
        underscore.className = 'underscore-container hidden';
        visible = false;
        } else {
            underscore.className = 'underscore-container';
        visible = true;
        }
    }, 400);
}

displayUnderscore();