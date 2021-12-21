const socket = io();

// 이름 클릭
const contact = document.getElementsByClassName("contact-name");

const before_call = document.getElementsByClassName("before-call")[0];
const call_success = document.getElementsByClassName("call-success")[0];
const exit_call = document.getElementsByClassName("end-call")[0];
const translated_text = document.getElementsByClassName("call-text")[0];

/**
 * 이벤트 함수
 */
// 이름 클릭 시 Trigger Event
function onContactClickHandler() {
    before_call.style.display = "none";
    call_success.style.display = "block";
    socket.emit("join");
}

// 통화 종료 시 Trigger Event
function onEndCallClickHandler() {
    before_call.style.display = "block";
    call_success.style.display = "none";
    socket.emit('leave')
    translated_text.innerText=''
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
    translated_text.innerText+=` ${data}`;
})