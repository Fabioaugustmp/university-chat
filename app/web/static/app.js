const chatMessages = document.getElementById("chat-messages");
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message");
const resetButton = document.getElementById("reset-chat");

const intentValue = document.getElementById("intent-value");
const confidenceValue = document.getElementById("confidence-value");
const topicValue = document.getElementById("topic-value");
const engineValue = document.getElementById("engine-value");

const SESSION_KEY = "academic-chat-session";

function getSessionId() {
  let sessionId = window.localStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = window.crypto.randomUUID();
    window.localStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
}

function resetSession() {
  const newSessionId = window.crypto.randomUUID();
  window.localStorage.setItem(SESSION_KEY, newSessionId);
  chatMessages.innerHTML = "";
  setInsights({ intent: "-", confidence: "-", current_topic: "-", used_bert: false });
  addMessage(
    "assistant",
    "Nova conversa iniciada. Pergunte sobre historico, boleto, disciplinas ou professores."
  );
}

function addMessage(role, text) {
  const bubble = document.createElement("div");
  bubble.className = `bubble ${role}`;
  bubble.textContent = text;
  chatMessages.appendChild(bubble);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

function setInsights(payload) {
  intentValue.textContent = payload.intent || "-";
  confidenceValue.textContent =
    typeof payload.confidence === "number" ? payload.confidence.toFixed(2) : "-";
  topicValue.textContent = payload.current_topic || "-";
  engineValue.textContent = payload.used_bert ? "BERT" : "Fallback";
}

async function sendMessage(message) {
  addMessage("user", message);

  const response = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      message,
      session_id: getSessionId(),
    }),
  });

  if (!response.ok) {
    addMessage("assistant", "Nao consegui responder agora. Verifique se a API esta ativa.");
    return;
  }

  const payload = await response.json();
  window.localStorage.setItem(SESSION_KEY, payload.session_id);
  addMessage("assistant", payload.reply);
  setInsights(payload);
}

chatForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = messageInput.value.trim();
  if (!message) {
    return;
  }

  messageInput.value = "";
  messageInput.focus();
  await sendMessage(message);
});

resetButton.addEventListener("click", resetSession);

addMessage(
  "assistant",
  "Ola! Eu sou o Assistente Academico Inteligente. Pergunte, por exemplo: Quem e o professor de Redes?"
);
