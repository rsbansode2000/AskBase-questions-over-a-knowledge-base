const form = document.querySelector('#question-form');
const input = document.querySelector('#question-input');
const windowEl = document.querySelector('#chat-window');
const badge = document.querySelector('#ready-badge');
const newChatButton = document.querySelector('#new-chat');
const deleteChatButton = document.querySelector('#delete-chat');
const escapeHtml = (value) => String(value).replace(/[&<>"']/g, (char) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;' })[char]);

function showEmptyChat(message = 'What would you like to know?') {
  windowEl.innerHTML = `<div class="empty-chat" id="empty-chat"><i class="bi bi-stars"></i><h3>${message}</h3><p>Ask about the contents of your uploaded document.</p></div>`;
}

async function updateChat(endpoint, confirmation) {
  if (confirmation && !window.confirm(confirmation)) return;
  newChatButton.disabled = true;
  deleteChatButton.disabled = true;
  try {
    const response = await fetch(endpoint, { method: 'POST' });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not update the chat.');
    showEmptyChat(endpoint === '/chat/new' ? 'What would you like to know?' : 'Chat deleted.');
    input.value = '';
  } catch (error) {
    window.alert(error.message);
  } finally {
    newChatButton.disabled = false;
    deleteChatButton.disabled = false;
    if (!input.disabled) input.focus();
  }
}

function addMessage(role, text, sources = [], timestamp = 'now') {
  const sourceHtml = sources.length ? `<div class="sources">${sources.map((source) => `<div><i class="bi bi-file-earmark-text"></i> ${escapeHtml(source.document)} · Page ${source.page} · Chunk ${source.chunk} · Confidence ${source.confidence}</div>`).join('')}</div>` : '';
  windowEl.insertAdjacentHTML('beforeend', `<article class="message ${role}"><span class="message-label">${role === 'user' ? 'You' : 'Assistant'} · ${timestamp}</span><div class="message-body"><div class="message-bubble">${escapeHtml(text)}</div>${sourceHtml}</div></article>`);
  windowEl.scrollTop = windowEl.scrollHeight;
}

function showTyping() {
  windowEl.insertAdjacentHTML('beforeend', '<article id="typing" class="message assistant"><span class="message-label">Assistant</span><div class="message-body"><div class="message-bubble"><span class="spinner-border spinner-border-sm text-primary"></span> Searching relevant context...</div></div></article>');
  windowEl.scrollTop = windowEl.scrollHeight;
}

form?.addEventListener('submit', async (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (!question || input.disabled) return;
  document.querySelector('#empty-chat')?.remove();
  addMessage('user', question);
  input.value = '';
  input.disabled = true;
  form.querySelector('button').disabled = true;
  showTyping();
  try {
    const response = await fetch('/chat', { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify({ question }) });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || 'Could not generate an answer.');
    document.querySelector('#typing')?.remove();
    addMessage('assistant', data.answer, data.sources || [], data.timestamp || 'now');
  } catch (error) {
    document.querySelector('#typing')?.remove();
    addMessage('assistant', error.message);
  } finally {
    input.disabled = false;
    form.querySelector('button').disabled = false;
    input.focus();
  }
});

newChatButton?.addEventListener('click', () => updateChat('/chat/new'));
deleteChatButton?.addEventListener('click', () => updateChat('/chat/delete', 'Delete this chat history? This cannot be undone.'));
windowEl?.scrollTo(0, windowEl.scrollHeight);
