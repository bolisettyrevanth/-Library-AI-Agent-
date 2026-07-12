**
 * Library AI Agent — Chat Interface JavaScript
 * Handles: message sending, rendering, markdown formatting, suggestions
 */

'use strict';

const chatInput   = document.getElementById('chatInput');
const sendBtn     = document.getElementById('sendBtn');
const messagesArea = document.getElementById('messagesArea');
const typingIndicator = document.getElementById('typingIndicator');
const clearChatBtn = document.getElementById('clearChatBtn');

/* ── Utility: Escape HTML ──────────────────────────────── */
function escapeHtml(str) {
  return str
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

/* ── Utility: Basic Markdown → HTML ────────────────────── */
function formatMarkdown(text) {
  // Escape first, then apply formatting
  let html = escapeHtml(text);

  // Code blocks
  html = html.replace(/```([\s\S]*?)```/g, '<pre class="bg-body-secondary rounded-3 p-3 small mt-2 mb-2"><code>$1</code></pre>');
  // Inline code
  html = html.replace(/`([^`]+)`/g, '<code class="bg-body-secondary px-1 rounded">$1</code>');
  // Bold
  html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  // Italic
  html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');
  // Numbered list
  html = html.replace(/^(\d+)\. (.+)$/gm, '<li class="mb-1">$2</li>');
  html = html.replace(/((<li.*<\/li>\n?)+)/g, '<ol class="ps-3 mt-1 mb-2">$1</ol>');
  // Bullet list
  html = html.replace(/^[•\-\*] (.+)$/gm, '<li class="mb-1">$1</li>');
  // Headings
  html = html.replace(/^### (.+)$/gm, '<h6 class="fw-bold mt-2 mb-1">$1</h6>');
  html = html.replace(/^## (.+)$/gm, '<h5 class="fw-bold mt-2 mb-1">$1</h5>');
  // Line breaks
  html = html.replace(/\n{2,}/g, '</p><p class="mb-1">');
  html = html.replace(/\n/g, '<br>');
  // Wrap in paragraph
  html = `<p class="mb-1">${html}</p>`;

  return html;
}

/* ── Get current time string ────────────────────────────── */
function getTime() {
  return new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
}

/* ── Render a user message ──────────────────────────────── */
function appendUserMessage(text) {
  const div = document.createElement('div');
  div.className = 'chat-msg user-msg mb-4 d-flex flex-column align-items-end';
  div.innerHTML = `
    <div class="msg-bubble user-bubble-msg">
      <p class="mb-0">${escapeHtml(text)}</p>
    </div>
    <div class="text-muted small mt-1">
      <i class="bi bi-clock me-1"></i>${getTime()}
    </div>`;
  messagesArea.appendChild(div);
  scrollToBottom();
}

/* ── Render a bot message ───────────────────────────────── */
function appendBotMessage(text) {
  const div = document.createElement('div');
  div.className = 'chat-msg bot-msg mb-4';
  div.innerHTML = `
    <div class="d-flex gap-3 align-items-start">
      <div class="ai-avatar-xs flex-shrink-0">
        <i class="bi bi-robot"></i>
      </div>
      <div class="msg-bubble bot-bubble-msg">
        ${formatMarkdown(text)}
      </div>
    </div>
    <div class="text-muted small ms-5 mt-1">
      <i class="bi bi-clock me-1"></i>${getTime()} &nbsp;
      <i class="bi bi-stars text-primary me-1"></i>IBM Granite AI
    </div>`;
  messagesArea.appendChild(div);
  scrollToBottom();
}

/* ── Render an error message ─────────────────────────────── */
function appendErrorMessage(text) {
  const div = document.createElement('div');
  div.className = 'chat-msg mb-4';
  div.innerHTML = `
    <div class="alert alert-danger rounded-3 d-flex gap-2 align-items-start mb-0">
      <i class="bi bi-exclamation-triangle-fill flex-shrink-0 mt-1"></i>
      <div class="small">${escapeHtml(text)}</div>
    </div>`;
  messagesArea.appendChild(div);
  scrollToBottom();
}

/* ── Scroll messages to bottom ──────────────────────────── */
function scrollToBottom() {
  messagesArea.scrollTo({ top: messagesArea.scrollHeight, behavior: 'smooth' });
}

/* ── Show / hide typing indicator ───────────────────────── */
function showTyping() {
  typingIndicator.classList.remove('d-none');
  scrollToBottom();
}
function hideTyping() {
  typingIndicator.classList.add('d-none');
}

/* ── Set input / button state ───────────────────────────── */
function setUIBusy(busy) {
  chatInput.disabled = busy;
  sendBtn.disabled   = busy;
  if (busy) {
    sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm"></span>';
  } else {
    sendBtn.innerHTML = '<i class="bi bi-send-fill"></i>';
    chatInput.focus();
  }
}

/* ── Send a message ─────────────────────────────────────── */
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = '';
  appendUserMessage(text);
  setUIBusy(true);
  showTyping();
clearChatBtn.addEventListener('click', async function () {
    if (!confirm('Clear the entire conversation?')) return;
    try {
      await fetch('/api/chat/clear', { method: 'POST' });
    } catch (_) { /* ignore */ }
    
    // Safely remove custom messages while keeping the welcome message
    const customMsgs = messagesArea.querySelectorAll('.chat-msg:not(#welcomeMsg)');
    customMsgs.forEach(el => el.remove());
    showToast('Conversation cleared.', 'info');
  });

    if (!response.ok) {
      throw new Error(`Server error: ${response.status}`);
    }

    const data = await response.json();
    hideTyping();

    if (data.error) {
      appendErrorMessage(data.error);
    } else {
      appendBotMessage(data.reply || 'No response received.');
    }
  } catch (err) {
    hideTyping();
    appendErrorMessage(`Connection error: ${err.message}. Please check your API configuration.`);
  } finally {
    setUIBusy(false);
  }
}

/* ── Clear chat ─────────────────────────────────────────── */
if (clearChatBtn) {
  clearChatBtn.addEventListener('click', async function () {
    if (!confirm('Clear the entire conversation?')) return;
    try {
      await fetch('/api/chat/clear', { method: 'POST' });
    } catch (_) { /* ignore */ }
    // Remove all messages except the welcome message
    const msgs = messagesArea.querySelectorAll('.chat-msg:not(#welcomeMsg .chat-msg)');
    messagesArea.querySelectorAll('.chat-msg').forEach((el, i) => {
      if (i > 0) el.remove();  // keep welcome
    });
    showToast('Conversation cleared.', 'info');
  });
}

/* ── Suggestion buttons ─────────────────────────────────── */
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.suggestion-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      chatInput.value = this.dataset.msg;
      chatInput.focus();
      sendMessage();
    });
  });
});

/* ── Keyboard: Enter to send ─────────────────────────────── */
if (chatInput) {
  chatInput.addEventListener('keydown', function (e) {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });
}

/* ── Send button click ──────────────────────────────────── */
if (sendBtn) {
  sendBtn.addEventListener('click', sendMessage);
}

/* ── Character counter ──────────────────────────────────── */
if (chatInput) {
  chatInput.addEventListener('input', function () {
    const remaining = 500 - this.value.length;
    if (remaining < 50) {
      this.style.borderColor = remaining < 10 ? '#ef4444' : '#f59e0b';
    } else {
      this.style.borderColor = '';
    }
  });
}
