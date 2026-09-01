
const API_URL = "http://127.0.0.1:8000";

// ==========================================
// DOM ELEMENTS
// ==========================================

const messageInput = document.getElementById("messageInput");
const sendButton = document.getElementById("sendButton");
const chatBox = document.getElementById("chatBox");

const loginContainer = document.getElementById("loginContainer");
const registerContainer = document.getElementById("registerContainer");
const chatContainer = document.getElementById("chatContainer");

const loginForm = document.getElementById("loginForm");
const loginUsername = document.getElementById("loginUsername");
const loginPassword = document.getElementById("loginPassword");
const loginMessage = document.getElementById("loginMessage");

const showRegisterButton =
    document.getElementById("showRegisterButton");

const showLoginButton =
    document.getElementById("showLoginButton");

const registerForm =
    document.getElementById("registerForm");

const registerUsername =
    document.getElementById("registerUsername");

const registerEmail =
    document.getElementById("registerEmail");

const registerPassword =
    document.getElementById("registerPassword");

const registerMessage =
    document.getElementById("registerMessage");

const sessionList = document.getElementById("sessionList");
const newChatButton = document.getElementById("newChatButton");

const pdfInput = document.getElementById("pdfInput");
const uploadPdfButton = document.getElementById("uploadPdfButton");
const pdfMessage = document.getElementById("pdfMessage");

const logoutButton = document.getElementById("logoutButton");

// ==========================================
// CURRENT SESSION
// ==========================================

let currentSessionId =
    localStorage.getItem("currentSessionId")
        ? parseInt(localStorage.getItem("currentSessionId"))
        : null;

// ==========================================
// TOKEN
// ==========================================

function getToken() {
    return localStorage.getItem("access_token");
}

function clearLogin() {

    localStorage.removeItem("access_token");
    localStorage.removeItem("currentSessionId");

    currentSessionId = null;

    loginContainer.style.display = "flex";
    registerContainer.style.display = "none";
    chatContainer.style.display = "none";

    sessionList.innerHTML = "";
    chatBox.innerHTML = "";
    pdfMessage.textContent = "";

    const oldPdf =
        document.getElementById("uploadedPdf");

    if (oldPdf) {
        oldPdf.remove();
    }

    loginMessage.textContent =
        "Session expired. Please login again.";
}

function authHeaders() {

    const token = getToken();

    if (!token) {
        return null;
    }

    return {
        "Authorization": "Bearer " + token
    };
}

// ==========================================
// SHOW REGISTER SCREEN
// ==========================================

function showRegisterScreen(event) {

    if (event) {
        event.preventDefault();
    }

    loginContainer.style.display = "none";
    registerContainer.style.display = "flex";
    chatContainer.style.display = "none";

    loginMessage.textContent = "";
    registerMessage.textContent = "";

    registerUsername.value = "";
    registerEmail.value = "";
    registerPassword.value = "";

    registerUsername.focus();
}

// ==========================================
// SHOW LOGIN SCREEN
// ==========================================

function showLoginScreen(event) {

    if (event) {
        event.preventDefault();
    }

    registerContainer.style.display = "none";
    loginContainer.style.display = "flex";
    chatContainer.style.display = "none";

    registerMessage.textContent = "";
    loginMessage.textContent = "";

    loginUsername.value = "";
    loginPassword.value = "";

    loginUsername.focus();
}

// ==========================================
// LOGIN
// ==========================================

async function loginUser(event) {

    event.preventDefault();

    const username =
        loginUsername.value.trim();

    const password =
        loginPassword.value;

    if (!username || !password) {

        loginMessage.textContent =
            "Please enter email and password.";

        return;
    }

    loginMessage.textContent =
        "Logging in...";

    try {

        const formData =
            new URLSearchParams();

        formData.append(
            "username",
            username
        );

        formData.append(
            "password",
            password
        );

        const response =
            await fetch(
                API_URL + "/users/login",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/x-www-form-urlencoded"
                    },
                    body: formData
                }
            );

        const data =
            await response.json();

        console.log(
            "Login response:",
            response.status,
            data
        );

        if (!response.ok) {

            loginMessage.textContent =
                data.detail ||
                "Login failed.";

            return;
        }

        if (!data.access_token) {

            loginMessage.textContent =
                "Login succeeded but no token was returned.";

            return;
        }

        localStorage.setItem(
            "access_token",
            data.access_token
        );

        loginContainer.style.display = "none";
        registerContainer.style.display = "none";
        chatContainer.style.display = "flex";

        loginMessage.textContent = "";

        const success =
            await loadSessions();

        if (!success) {
            return;
        }

        if (!currentSessionId) {

            const created =
                await createChatSession();

            if (created) {
                await loadSessions();
            }
        }

    } catch (error) {

        console.error(
            "Login error:",
            error
        );

        loginMessage.textContent =
            "Could not connect to FastAPI server.";
    }
}

// ==========================================
// USER REGISTRATION
// ==========================================

async function registerUser(event) {

    event.preventDefault();

    const username =
        registerUsername.value.trim();

    const email =
        registerEmail.value.trim();

    const password =
        registerPassword.value;

    if (!username || !email || !password) {

        registerMessage.textContent =
            "Please fill all fields.";

        return;
    }

    registerMessage.textContent =
        "Creating account...";

    try {

        const response =
            await fetch(
                API_URL + "/users/register",
                {
                    method: "POST",

                    headers: {
                        "Content-Type":
                            "application/json"
                    },

                    body: JSON.stringify({
                        username: username,
                        email: email,
                        password: password
                    })
                }
            );

        const data =
            await response.json();

        console.log(
            "Registration response:",
            response.status,
            data
        );

        if (!response.ok) {

            registerMessage.textContent =
                data.detail ||
                "Registration failed.";

            return;
        }

        // Registration successful

        registerMessage.textContent =
            "Account created successfully!";

        registerForm.reset();

        // Automatically return to login after short delay

        setTimeout(function () {

            registerContainer.style.display = "none";
            loginContainer.style.display = "flex";

            loginMessage.textContent =
                "Account created successfully. Please login.";

            loginUsername.value = email;

            loginPassword.focus();

        }, 1000);

    } catch (error) {

        console.error(
            "Registration error:",
            error
        );

        registerMessage.textContent =
            "Could not connect to FastAPI server.";
    }
}

// ==========================================
// LOAD SESSIONS
// ==========================================

async function loadSessions() {

    const headers = authHeaders();

    if (!headers) {
        return false;
    }

    try {

        const response =
            await fetch(
                API_URL + "/sessions/",
                {
                    method: "GET",
                    headers: headers
                }
            );

        if (response.status === 401) {

            clearLogin();
            return false;
        }

        const data =
            await response.json();

        if (!response.ok) {
            return false;
        }

        sessionList.innerHTML = "";

        if (!Array.isArray(data)) {
            return false;
        }

        data.forEach(function(session) {

            const wrapper =
                document.createElement("div");

            wrapper.classList.add(
                "session-wrapper"
            );

            const sessionDiv =
                document.createElement("div");

            sessionDiv.classList.add(
                "session-item"
            );

            sessionDiv.textContent =
                session.title || "New Chat";

            sessionDiv.dataset.sessionId =
                session.session_id;

            if (
                session.session_id ===
                currentSessionId
            ) {

                sessionDiv.classList.add(
                    "active"
                );
            }

            sessionDiv.addEventListener(
                "click",
                function(event) {

                    event.preventDefault();

                    selectSession(
                        session.session_id
                    );
                }
            );

            const deleteButton =
                document.createElement("button");

            deleteButton.type = "button";

            deleteButton.classList.add(
                "delete-session-button"
            );

            deleteButton.textContent = "×";

            deleteButton.title =
                "Delete session";

            deleteButton.addEventListener(
                "click",
                function(event) {

                    event.preventDefault();
                    event.stopPropagation();

                    deleteSession(
                        session.session_id
                    );
                }
            );

            wrapper.appendChild(sessionDiv);
            wrapper.appendChild(deleteButton);

            sessionList.appendChild(wrapper);
        });

        if (data.length > 0) {

            const savedSessionExists =
                data.some(
                    function(session) {

                        return (
                            session.session_id ===
                            currentSessionId
                        );
                    }
                );

            if (
                currentSessionId !== null &&
                savedSessionExists
            ) {

                await selectSession(
                    currentSessionId
                );

            } else {

                currentSessionId = null;

                localStorage.removeItem(
                    "currentSessionId"
                );

                await selectSession(
                    data[0].session_id
                );
            }
        }

        return true;

    } catch (error) {

        console.error(
            "Session connection error:",
            error
        );

        return false;
    }
}

// ==========================================
// CREATE SESSION
// ==========================================

async function createChatSession() {

    const headers = authHeaders();

    if (!headers) {
        return false;
    }

    try {

        const response =
            await fetch(
                API_URL + "/sessions/",
                {
                    method: "POST",
                    headers: headers
                }
            );

        if (response.status === 401) {

            clearLogin();
            return false;
        }

        const data =
            await response.json();

        if (!response.ok) {
            return false;
        }

        currentSessionId =
            data.session_id;

        localStorage.setItem(
            "currentSessionId",
            currentSessionId
        );

        return true;

    } catch (error) {

        console.error(
            "Session creation error:",
            error
        );

        return false;
    }
}

// ==========================================
// NEW CHAT
// ==========================================

async function createNewChat(event) {

    if (event) {
        event.preventDefault();
    }

    const created =
        await createChatSession();

    if (!created) {

        addMessage(
            "Could not create a new chat session.",
            "ai"
        );

        return;
    }

    chatBox.innerHTML = "";

    const oldPdf =
        document.getElementById("uploadedPdf");

    if (oldPdf) {
        oldPdf.remove();
    }

    pdfMessage.textContent = "";

    await loadSessions();

    addMessage(
        "Hello! How can I help you today?",
        "ai"
    );
}

// ==========================================
// DELETE SESSION
// ==========================================

async function deleteSession(sessionId) {

    const confirmed =
        window.confirm(
            "Are you sure you want to delete this chat?"
        );

    if (!confirmed) {
        return;
    }

    const headers =
        authHeaders();

    if (!headers) {
        return;
    }

    try {

        const response =
            await fetch(
                API_URL +
                "/sessions/" +
                sessionId,
                {
                    method: "DELETE",
                    headers: headers
                }
            );

        if (response.status === 401) {

            clearLogin();
            return;
        }

        const data =
            await response.json();

        if (!response.ok) {

            window.alert(
                data.detail ||
                "Could not delete session."
            );

            return;
        }

        if (
            sessionId ===
            currentSessionId
        ) {

            currentSessionId = null;

            localStorage.removeItem(
                "currentSessionId"
            );

            chatBox.innerHTML = "";

            const oldPdf =
                document.getElementById(
                    "uploadedPdf"
                );

            if (oldPdf) {
                oldPdf.remove();
            }

            pdfMessage.textContent = "";
        }

        await loadSessions();

    } catch (error) {

        console.error(
            "Delete session error:",
            error
        );

        window.alert(
            "Could not connect to FastAPI server."
        );
    }
}

// ==========================================
// PDF UPLOAD
// ==========================================

async function uploadPDF() {

    const file =
        pdfInput.files &&
        pdfInput.files[0];

    if (!file) {

        pdfMessage.textContent =
            "No PDF selected.";

        return;
    }

    if (
        !file.name
            .toLowerCase()
            .endsWith(".pdf")
    ) {

        pdfMessage.textContent =
            "Only PDF files are allowed.";

        pdfInput.value = "";

        return;
    }

    const token =
        getToken();

    if (!token) {

        pdfMessage.textContent =
            "Please login first.";

        return;
    }

    if (!currentSessionId) {

        pdfMessage.textContent =
            "Please create/select a chat session first.";

        return;
    }

    uploadPdfButton.disabled = true;

    pdfMessage.textContent =
        "Uploading PDF...";

    const formData =
        new FormData();

    formData.append(
        "file",
        file
    );

    formData.append(
        "session_id",
        currentSessionId
    );

    try {

        const response =
            await fetch(
                API_URL + "/pdf/upload",
                {
                    method: "POST",
                    headers: {
                        "Authorization":
                            "Bearer " + token
                    },
                    body: formData
                }
            );

        const data =
            await response.json();

        if (response.status === 401) {

            clearLogin();
            return;
        }

        if (!response.ok) {

            pdfMessage.textContent =
                data.detail ||
                "PDF upload failed.";

            return;
        }

        pdfMessage.textContent =
            "PDF uploaded successfully!";

        pdfInput.value = "";

        showUploadedPDF(
            data.filename,
            data.document_id
        );

        currentSessionId =
            data.session_id ||
            currentSessionId;

        localStorage.setItem(
            "currentSessionId",
            currentSessionId
        );

        await loadSessions();

    } catch (error) {

        console.error(
            "PDF upload error:",
            error
        );

        pdfMessage.textContent =
            "Could not connect to FastAPI server.";

    } finally {

        uploadPdfButton.disabled = false;
    }
}

// ==========================================
// SHOW UPLOADED PDF
// ==========================================

function showUploadedPDF(
    filename,
    documentId
) {

    const oldPdf =
        document.getElementById(
            "uploadedPdf"
        );

    if (oldPdf) {
        oldPdf.remove();
    }

    const pdfBox =
        document.createElement("div");

    pdfBox.id =
        "uploadedPdf";

    pdfBox.classList.add(
        "uploaded-pdf"
    );

    pdfBox.innerHTML = `
        <span>📄 ${filename}</span>
        <button
            type="button"
            id="removePdfButton"
            title="Remove PDF from this chat"
        >
            ×
        </button>
    `;

    const inputArea =
        document.querySelector(
            ".input-area"
        );

    inputArea.parentNode.insertBefore(
        pdfBox,
        inputArea
    );

    const removeButton =
        document.getElementById(
            "removePdfButton"
        );

    removeButton.addEventListener(
        "click",
        async function() {

            const token =
                getToken();

            if (!token) {
                return;
            }

            if (!currentSessionId) {
                return;
            }

            removeButton.disabled = true;

            pdfMessage.textContent =
                "Removing PDF...";

            try {

                const response =
                    await fetch(
                        API_URL +
                        "/sessions/" +
                        currentSessionId +
                        "/pdf",
                        {
                            method: "DELETE",
                            headers: {
                                "Authorization":
                                    "Bearer " +
                                    token
                            }
                        }
                    );

                const data =
                    await response.json();

                if (response.status === 401) {

                    clearLogin();
                    return;
                }

                if (!response.ok) {

                    pdfMessage.textContent =
                        data.detail ||
                        "Could not remove PDF.";

                    removeButton.disabled =
                        false;

                    return;
                }

                pdfBox.remove();

                pdfMessage.textContent = "";

                await loadSessions();

            } catch (error) {

                console.error(
                    "PDF detach error:",
                    error
                );

                pdfMessage.textContent =
                    "Could not connect to FastAPI server.";

                removeButton.disabled =
                    false;
            }
        }
    );
}

// ==========================================
// LOAD SESSION PDF
// ==========================================

async function loadSessionPDF(sessionId) {

    const headers =
        authHeaders();

    if (!headers) {
        return;
    }

    try {

        const sessionResponse =
            await fetch(
                API_URL + "/sessions/",
                {
                    method: "GET",
                    headers: headers
                }
            );

        if (
            sessionResponse.status === 401
        ) {

            clearLogin();
            return;
        }

        if (!sessionResponse.ok) {
            return;
        }

        const sessions =
            await sessionResponse.json();

        const currentSession =
            sessions.find(
                function(sessionItem) {

                    return (
                        sessionItem.session_id ===
                        sessionId
                    );
                }
            );

        if (
            !currentSession ||
            !currentSession.document_id
        ) {

            const oldPdf =
                document.getElementById(
                    "uploadedPdf"
                );

            if (oldPdf) {
                oldPdf.remove();
            }

            return;
        }

        const documentResponse =
            await fetch(
                API_URL + "/pdf/",
                {
                    method: "GET",
                    headers: headers
                }
            );

        if (!documentResponse.ok) {
            return;
        }

        const documents =
            await documentResponse.json();

        const pdfDocument =
            documents.find(
                function(documentItem) {

                    return (
                        documentItem.document_id ===
                        currentSession.document_id
                    );
                }
            );

        if (!pdfDocument) {
            return;
        }

        showUploadedPDF(
            pdfDocument.filename,
            pdfDocument.document_id
        );

    } catch (error) {

        console.error(
            "Session PDF loading error:",
            error
        );
    }
}

// ==========================================
// SELECT SESSION
// ==========================================

async function selectSession(sessionId) {

    currentSessionId =
        sessionId;

    localStorage.setItem(
        "currentSessionId",
        currentSessionId
    );

    chatBox.innerHTML = "";

    const oldPdf =
        document.getElementById(
            "uploadedPdf"
        );

    if (oldPdf) {
        oldPdf.remove();
    }

    pdfMessage.textContent = "";

    const headers =
        authHeaders();

    if (!headers) {
        return;
    }

    try {

        await loadSessionPDF(
            sessionId
        );

        const response =
            await fetch(
                API_URL +
                "/chat/history/" +
                sessionId,
                {
                    method: "GET",
                    headers: headers
                }
            );

        if (
            response.status === 401
        ) {

            clearLogin();
            return;
        }

        const data =
            await response.json();

        if (!response.ok) {

            addMessage(
                data.detail ||
                "Could not load chat history.",
                "ai"
            );

            return;
        }

        const history =
            data.history;

        if (
            !history ||
            history.length === 0
        ) {

            addMessage(
                "Hello! How can I help you today?",
                "ai"
            );

            return;
        }

        history.forEach(
            function(chat) {

                addMessage(
                    chat.message,
                    "user"
                );

                addMessage(
                    chat.response,
                    "ai"
                );
            }
        );

    } catch (error) {

        console.error(
            "History connection error:",
            error
        );

        addMessage(
            "Could not load chat history.",
            "ai"
        );
    }
}

// ==========================================
// AI THINKING INDICATOR
// ==========================================

function showThinkingIndicator() {

    const thinkingDiv =
        document.createElement("div");

    thinkingDiv.id =
        "thinkingIndicator";

    thinkingDiv.classList.add(
        "message",
        "ai-message",
        "thinking-message"
    );

    thinkingDiv.innerHTML = `
        <span>Thinking</span>
        <span class="thinking-dots">
            <span>.</span>
            <span>.</span>
            <span>.</span>
        </span>
    `;

    chatBox.appendChild(
        thinkingDiv
    );

    chatBox.scrollTop =
        chatBox.scrollHeight;
}

function removeThinkingIndicator() {

    const thinkingDiv =
        document.getElementById(
            "thinkingIndicator"
        );

    if (thinkingDiv) {
        thinkingDiv.remove();
    }
}

// ==========================================
// SEND MESSAGE
// ==========================================

async function sendMessage(event) {

    if (event) {
        event.preventDefault();
    }

    const message =
        messageInput.value.trim();

    if (!message) {
        return;
    }

    if (!currentSessionId) {

        addMessage(
            "Chat session is not available.",
            "ai"
        );

        return;
    }

    const token =
        getToken();

    if (!token) {

        addMessage(
            "Please login first.",
            "ai"
        );

        return;
    }

    addMessage(
        message,
        "user"
    );

    messageInput.value = "";

    sendButton.disabled = true;

    showThinkingIndicator();

    try {

        const response =
            await fetch(
                API_URL + "/chat/send",
                {
                    method: "POST",
                    headers: {
                        "Content-Type":
                            "application/json",

                        "Authorization":
                            "Bearer " + token
                    },

                    body: JSON.stringify({
                        session_id:
                            currentSessionId,

                        message:
                            message
                    })
                }
            );

        removeThinkingIndicator();

        if (
            response.status === 401
        ) {

            clearLogin();
            return;
        }

        const data =
            await response.json();

        if (!response.ok) {

            addMessage(
                data.detail ||
                "Server returned an error.",
                "ai"
            );

            return;
        }

        addMessage(
            data.response,
            "ai"
        );

        // Refresh session title
        await loadSessions();

    } catch (error) {

        console.error(
            "Chat connection error:",
            error
        );

        removeThinkingIndicator();

        addMessage(
            "Could not connect to FastAPI server.",
            "ai"
        );

    } finally {

        sendButton.disabled = false;

        messageInput.focus();
    }
}

// ==========================================
// ADD MESSAGE
// ==========================================

function addMessage(message, type) {

    const messageDiv =
        document.createElement("div");

    messageDiv.classList.add(
        "message"
    );

    if (type === "user") {

        messageDiv.classList.add(
            "user-message"
        );

        messageDiv.textContent =
            message;

    } else {

        messageDiv.classList.add(
            "ai-message"
        );

        let formattedMessage =
            String(message);

        formattedMessage =
            formattedMessage
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;");

        formattedMessage =
            formattedMessage.replace(
                /```([\s\S]*?)```/g,
                function(match, code) {

                    return (
                        '<pre class="code-block"><code>' +
                        code.trim() +
                        "</code></pre>"
                    );
                }
            );

        formattedMessage =
            formattedMessage.replace(
                /`([^`]+)`/g,
                "<code>$1</code>"
            );

        formattedMessage =
            formattedMessage.replace(
                /\*\*(.*?)\*\*/g,
                "<strong>$1</strong>"
            );

        formattedMessage =
            formattedMessage.replace(
                /\*([^*]+)\*/g,
                "<em>$1</em>"
            );

        formattedMessage =
            formattedMessage.replace(
                /^### (.*)$/gm,
                "<h4>$1</h4>"
            );

        formattedMessage =
            formattedMessage.replace(
                /^## (.*)$/gm,
                "<h3>$1</h3>"
            );

        formattedMessage =
            formattedMessage.replace(
                /^# (.*)$/gm,
                "<h2>$1</h2>"
            );

        formattedMessage =
            formattedMessage.replace(
                /^[•*-] (.*)$/gm,
                "<li>$1</li>"
            );

        formattedMessage =
            formattedMessage.replace(
                /^\d+\.\s+(.*)$/gm,
                "<li>$1</li>"
            );

        formattedMessage =
            formattedMessage.replace(
                /(<li>.*?<\/li>(?:\s*<li>.*?<\/li>)*)/gs,
                "<ul>$1</ul>"
            );

        formattedMessage =
            formattedMessage.replace(
                /\n/g,
                "<br>"
            );

        messageDiv.innerHTML =
            formattedMessage;
    }

    chatBox.appendChild(
        messageDiv
    );

    chatBox.scrollTop =
        chatBox.scrollHeight;
}

// ==========================================
// EVENT LISTENERS
// ==========================================

// LOGIN

loginForm.addEventListener(
    "submit",
    loginUser
);

// REGISTER

if (registerForm) {

    registerForm.addEventListener(
        "submit",
        registerUser
    );
}

// SHOW REGISTER

if (showRegisterButton) {

    showRegisterButton.addEventListener(
        "click",
        showRegisterScreen
    );
}

// SHOW LOGIN

if (showLoginButton) {

    showLoginButton.addEventListener(
        "click",
        showLoginScreen
    );
}

// SEND

sendButton.addEventListener(
    "click",
    sendMessage
);

// NEW CHAT

newChatButton.addEventListener(
    "click",
    createNewChat
);

// LOGOUT

logoutButton.addEventListener(
    "click",
    function(event) {

        event.preventDefault();

        clearLogin();
    }
);

// ENTER KEY

messageInput.addEventListener(
    "keydown",
    function(event) {

        if (event.key === "Enter") {

            event.preventDefault();

            sendMessage(event);
        }
    }
);

// ==========================================
// PDF BUTTON
// ==========================================

uploadPdfButton.addEventListener(
    "click",
    function(event) {

        event.preventDefault();

        pdfInput.click();
    }
);

// ==========================================
// PDF FILE SELECTION
// ==========================================

pdfInput.addEventListener(
    "change",
    function() {

        if (
            pdfInput.files &&
            pdfInput.files.length > 0
        ) {

            uploadPDF();
        }
    }
);

// ==========================================
// PAGE LOAD
// ==========================================

window.addEventListener(
    "DOMContentLoaded",
    async function() {

        console.log(
            "AI Chatbot frontend loaded."
        );

        const token =
            getToken();

        if (!token) {

            loginContainer.style.display =
                "flex";

            registerContainer.style.display =
                "none";

            chatContainer.style.display =
                "none";

            return;
        }

        loginContainer.style.display =
            "none";

        registerContainer.style.display =
            "none";

        chatContainer.style.display =
            "flex";

        const success =
            await loadSessions();

        if (!success) {
            return;
        }

        if (!currentSessionId) {

            const created =
                await createChatSession();

            if (created) {

                await loadSessions();

            } else {

                addMessage(
                    "Could not create chat session.",
                    "ai"
                );
            }
        }
    }
);

