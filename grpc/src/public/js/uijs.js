const socket = io();

// 이름 클릭
const contact = document.getElementsByClassName("contact-name");
const before_call = document.getElementsByClassName("before-call")[0];
const call_success = document.getElementsByClassName("call-success")[0];
const exit_call = document.getElementsByClassName("end-call")[0];
const translated_text = document.getElementsByClassName("call-text")[0];
const underscore = document.getElementById("underscore");

var isReceivingPunc = false;

/**
 * 이벤트 함수
 */
// 이름 클릭 시 Trigger Event
function onContactClickHandler() {
    isReceivingPunc = false;
    before_call.style.display = "none"; // Contact page 없애기
    call_success.style.display = "block"; // 통화 페이지 나타내기
    exit_call.style.display = "block"; // 통화 종료 버튼 나타내기
    socket.emit("join");
}

// 통화 종료 시 Trigger Event
function onEndCallClickHandler() {
    isReceivingPunc = true;
    exit_call.style.display = "none"; // 통화 종료 버튼 숨기기
    socket.emit('get_punc', translated_text.innerHTML);
    translated_text.innerText = "";
}

function goToContactPage() {
    translated_text.innerHTML = "";
    call_success.style.display = "none";
    before_call.style.display = "block";
    call_success.removeEventListener('click', goToContactPage, false);
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
    if(!isReceivingPunc) {
        console.log('Received infer', data);
        startTextAnimation(translated_text.innerText + " ", `${data}`);
    }
})

socket.on("leave", (punc_text) => {
    console.log('leave received', punc_text);
});

socket.on("send_punc", (punc_answer) => {
    translated_text.innerText = punc_answer;
    call_success.addEventListener('click', goToContactPage, false);
});

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