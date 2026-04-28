var running = false;

function sendMessage() {
    if (running == true) return;
    var msg = document.getElementById("user-input").value;
    if (msg == "") return;
    running = true;
    addMsg(msg);

    // Simulasi respons dari server setelah jeda waktu
    window.setTimeout(function () {
        var botResponse = getBotResponse(msg);
        addResponseMsg(botResponse);
    }, 1000);    
}

function addMsg(msg) {
    var div = document.createElement("div");
    div.innerHTML =
        "<span style='flex-grow:1'></span><div class='chat-message-sent'>" +
        msg +
        "</div>";
    div.className = "chat-message-div";
    document.getElementById("chat-body").appendChild(div);
    document.getElementById("user-input").value = "";
    document.getElementById("chat-body").scrollTop = document.getElementById(
        "chat-body"
    ).scrollHeight;
}

function addResponseMsg(msg) {
    var div = document.createElement("div");
    div.innerHTML = "<div class='chat-message-received'>" + msg + "</div>";
    div.className = "chat-message-div";
    document.getElementById("chat-body").appendChild(div);
    document.getElementById("chat-body").scrollTop = document.getElementById(
        "chat-body"
    ).scrollHeight;
    running = false;
}

function getBotResponse(userMsg) {
    // Proses untuk mendapatkan respons berdasarkan pertanyaan pengguna
    switch (userMsg.toLowerCase()) {
        case 'hai, ada yang perlu ditanyakan?':
            return 'Selamat datang! Ya, ada yang bisa saya bantu?';
        case 'apa itu pelayanan statistik digital?':
            return 'Pelayanan Statistik Terpadu (PST) Digital adalah pelayanan dari Badan Pusat Statistik Kota Surabaya yang bertujuan untuk memudahkan pengguna dalam menemukan publikasi yang telah diterbitkan oleh Badan Pusat Statistik Kota Surabaya.';
        case 'bagaimana cara kita menemukan publikasi di pelayanan statistik terpadu digital ini?':
            return 'Anda dapat menemukan publikasi dengan... (jawaban singkat)';
        case 'bagaimana cara konsultasi tentang publikasi digital?':
            return 'Untuk konsultasi tentang publikasi digital, Anda bisa... (jawaban singkat)';
        case 'ya':
            return 'Baik, untuk pertanyaan Anda dapat memilih pada chat sebelumnya.';
        case 'makasih':
            return 'Terima kasih kembali sudah menggunakan fitur kami. Untuk saran dalam pengembangan fitur dapat disalurkan melalui menu survey kepuasan. :)'
        default:
            return 'Maaf, saya tidak mengerti pertanyaan Anda.';
    }
}



document.getElementById("user-input").addEventListener("keyup", function (event) {
    if (event.keyCode === 13) {
        event.preventDefault();
        sendMessage();
    }
});

document.getElementById("input-message").onclick = function () {
    var chatbot = document.getElementById("chatbot-body");
    if (chatbot.classList.contains("collapsed")) {
        chatbot.classList.remove("collapsed");
        document.getElementById("input-message").children[0].style.display = "none";
        document.getElementById("input-message").children[1].style.display = "";
        setTimeout(function () {
            var botResponse = getBotResponse("Hallo, ada yang perlu ditanyakan?");
            addResponseMsg(botResponse);
        }, 1000);
    } else {
        chatbot.classList.add("collapsed");
        document.getElementById("input-message").children[0].style.display = "";
        document.getElementById("input-message").children[1].style.display = "none";
    }
};
