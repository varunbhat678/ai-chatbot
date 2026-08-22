const API_URL = "http://127.0.0.1:8000";

let currentSessionId = 9;

const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const chatBox = document.getElementById("chatBox");


function addMessage(message, type) {
    const messageDiv = document.createElement("div");

    messageDiv.classList.add("message");

    if (type === "user") {
        messageDiv.classList.add("user-message");
    } else {
        messageDiv.classList.add("ai-message");
    }

    messageDiv.textContent = message;

    chatBox.appendChild(messageDiv);

    chatBox.scrollTop = chatBox.scrollHeight;
}


async function sendMessage() {

    const message = messageInput.value.trim();

    if (!message) {
        return;
    }

    // Display user's message
    addMessage(message, "user");

    // Clear input
    messageInput.value = "";

    try {

        const response = await fetch(`${API_URL}/chat/send`, {
            method: "POST",

            headers: {
                "Content-Type": "application/json"
            },

            body: JSON.stringify({
                session_id: currentSessionId,
                message: message
            })
        });


        if (!response.ok) {
            throw new Error("Failed to send message");
        }


        const data = await response.json();

        // Display AI response
        addMessage(data.response, "ai");


    } catch (error) {

        console.error(error);

        addMessage(
            "Sorry, something went wrong. Please try again.",
            "ai"
        );
    }
}


sendButton.addEventListener("click", sendMessage);


messageInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter") {
        sendMessage();
    }

});