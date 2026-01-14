import { MESSAGING_HTTP, getToken, getName, clearAuth } from "./api.js";
import { connectWS } from "./ws.js";
import { setStatus, setAI, clearMessages, addMessage } from "./ui.js";

let conversationId = null;
let poller = null;
let timeout = null;
let ws = null;

function requireAuth() {
  if (!getToken()) {
    window.location.href = "login.html";
    return false;
  }
  return true;
}

async function reloadConversation() {
  if (!conversationId) return;

  const res = await fetch(`${MESSAGING_HTTP}/conversations/${conversationId}`);
  const data = await res.json();

  clearMessages();
  data.messages.forEach(m => {
    addMessage(m.sender, m.content, m.ai);
  });


  const hasAI = data.messages.some(m => m.ai && m.ai.intent);

  if (hasAI) {
    stopPolling();
    setAI("available");
  }
}

function startPolling() {
  stopPolling();
  setAI("processing");

  poller = setInterval(reloadConversation, 1000);

  timeout = setTimeout(() => {
    stopPolling();
    setAI("unavailable");
  }, 15000);
}

function stopPolling() {
  if (poller) clearInterval(poller);
  if (timeout) clearTimeout(timeout);
  poller = timeout = null;
}

function bootWS() {
  ws = connectWS({
    onOpen: () => setStatus("Connected"),
    onClose: () => setStatus("Disconnected"),
    onMessage: (data) => {
      if (data.type === "message_stored") {
        conversationId = data.message.conversation_id;
        reloadConversation();
        startPolling();
      }

      if (data.type === "ai_completed" || data.type === "AICompleted") {
        reloadConversation();
      }

      if (data.type === "error") {
        console.error("Gateway error:", data.error);
      }
    }
  });
}

function wireUI() {
  document.getElementById("who").textContent =
    `Logged in as ${getName() || "operator"}`;

  document.getElementById("send").onclick = () => {
    const input = document.getElementById("text");
    const text = input.value.trim();
    if (!text || !ws) return;

    ws.send(JSON.stringify({
      conversation_id: conversationId,
      content: text
    }));

    input.value = "";
  };

  document.getElementById("refreshAi").onclick = () => {
    reloadConversation();
    startPolling();
  };

  document.getElementById("logout").onclick = () => {
    clearAuth();
    window.location.href = "login.html";
  };
}

(function main() {
  if (!requireAuth()) return;
  wireUI();
  bootWS();
})();
