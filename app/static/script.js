// app/static/script.js
const {aiName, aiWelcome, customerName} = window.APP_CONFIG;

document.addEventListener("DOMContentLoaded", () => initChat());

function initChat() {
    const chatBox = document.getElementById("chat-box");
    // Append initial AI welcome message
    chatBox.innerHTML += buildMessageElement(aiName, aiWelcome);
}

function buildMessageElement(sender, message) {
    return ` <div class="chat-message ai-message">
      <div class="message-name"><strong>${sender}:</strong> ${message}</div>
    </div>`;
}

async function sendMessage() {
    const input = document.getElementById("user-input");
    const message = input.value.trim();
    if (!message) return;

    appendMessage(customerName, message);
    input.value = "";

    // Add temporary "AI: ..." message Pause for 500ms to simulate AI typing
    await new Promise(resolve => setTimeout(resolve, 500));
    const typingMsg = appendMessage(aiName, "...");
    startTypingAnimation(typingMsg);

    try {
        const response = await fetch("/chat", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({message}),
        });

        const data = await response.json();

        stopTypingAnimation(typingMsg);
        typingMsg.innerHTML = `<b>${aiName}:</b> ${data.message}`;
    } catch (err) {
        stopTypingAnimation(typingMsg);
        typingMsg.innerHTML = `<strong>System:</strong> Error: Could not contact server.`;
    }
}

async function clearChat() {
    const chatBox = document.getElementById("chat-box");
    const aiName = window.APP_CONFIG.aiName;
    const aiWelcome = window.APP_CONFIG.aiWelcome;

    //Step 1: Ask for confirmation
    const confirmed = confirm("Are you sure you want to clear this chat?");
    if (!confirmed) return;

    try {
        // Step 2: Clear chat history on server
        const res = await fetch("/clear", {method: "POST"});
        const data = await res.json();

        // Step 3: Clear UI
        chatBox.innerHTML = "";

        // Step 4: Add small delay, re-show AI welcome
        const typing = document.createElement("div");
        typing.classList.add("chat-message", "ai-message");
        typing.innerHTML = buildMessageElement(aiName, "...");
        chatBox.appendChild(typing);

        await new Promise(resolve => setTimeout(resolve, 800));
        typing.remove();

        initChat();
    } catch (err) {
        console.error("Failed to clear chat:", err);
        alert("Something went wrong while clearing the chat.");
    }
}


function appendMessage(sender, message) {
    const chatBox = document.getElementById("chat-box");
    const msgElement = document.createElement("p");
    msgElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
    chatBox.appendChild(msgElement);
    chatBox.scrollTop = chatBox.scrollHeight;
    return msgElement;
}

// Typing animation control
let typingInterval;

function startTypingAnimation(msgElement) {
    let dots = 0;
    typingInterval = setInterval(() => {
        dots = (dots + 1) % 4;
        msgElement.innerHTML = `<strong>${aiName}:</strong> ${'.'.repeat(dots)}`;
    }, 500);
}

function stopTypingAnimation(msgElement) {
    clearInterval(typingInterval);
    msgElement.innerHTML = `<strong>${aiName}:</strong>`;
}

// Enable "Enter" key to send message
document.addEventListener("DOMContentLoaded", () => {
    const input = document.getElementById("user-input");
    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter" && !event.shiftKey) {
            event.preventDefault();
            sendMessage();
        }
    });
});
