const sio = io("/room");
window.location.href = "#last-message";

const construct_username = (username, size) => {
    return `<a class="username-link" href="/users/${username}" style="font-size: ${size}px;">@${username}</a>`;
}

sio.on("message", (data) => {
    const chat = document.getElementById("chat");
    chat.innerHTML += `<p>${data.msg}</p>`;
    window.location.href = "#last-message";
});

sio.on("new_message", (data) => {
    const chat =  document.getElementById("chat");
    let message = `<div class="row">
                        <div class="col-md-6">
                            <img style="border-radius: 50%;" src="${data.avatar}" alt="...">
                            ${construct_username(data.username, 12)}
                        </div>
                        <div class="col-md-6" align="right">
                            ${moment(data.sent_at).fromNow(refresh=true)}
                        </div>
                    </div>
                    <div class="row">
                        <div class="col-md-12">
                            <p>${data.msg}</p>
                        </div>
                    </div>`;
    chat.innerHTML += message;
    window.location.href = "#last-message";
});

document.querySelector("#send-message").onclick = () => {
    const msg = document.querySelector("#message");
    const data = {
        msg: msg.value
    };
    sio.emit("new-message", data);
    msg.value = "";
    window.location.href = "#last-message";
};