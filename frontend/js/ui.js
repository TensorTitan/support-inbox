// frontend/js/ui.js

export function setStatus(text) {
  const el = document.getElementById("status");
  if (el) el.textContent = text;
}

export function setAI(state) {
  const aiStatus = document.getElementById("aiStatus");
  if (!aiStatus) return;

  if (state === "processing") {
    aiStatus.textContent = "AI: processing…";
  } else if (state === "available") {
    aiStatus.textContent = "AI: available";
  } else if (state === "unavailable") {
    aiStatus.textContent = "AI: unavailable";
  } else {
    aiStatus.textContent = "AI: unknown";
  }
}

export function clearMessages() {
  const el = document.getElementById("messages");
  if (el) el.innerHTML = "";
}

export function addMessage(sender, content, ai) {
  const messagesDiv = document.getElementById("messages");
  if (!messagesDiv) return;

  const div = document.createElement("div");
  div.className = "message";

  let aiBlock = "";

  if (ai && ai.intent) {
    aiBlock = `
      <div class="ai">
        <div><b>Intent:</b> ${escape(ai.intent)}</div>
        <div><b>Summary:</b> ${escape(ai.summary || "")}</div>
        <div><b>Suggested reply:</b></div>
        <div class="quote">"${escape(ai.suggested_reply || "")}"</div>
      </div>
    `;
  } else {
    aiBlock = `
      <div class="ai muted">
        AI: processing…
      </div>
    `;
  }

  div.innerHTML = `
    <div class="sender">${escape(sender)}</div>
    <div class="content">${escape(content)}</div>
    ${aiBlock}
  `;

  messagesDiv.appendChild(div);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

/**
 * Prevent XSS from messages / AI output
 */
function escape(str) {
  if (!str) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}