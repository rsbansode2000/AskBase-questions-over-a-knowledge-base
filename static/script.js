document.addEventListener('DOMContentLoaded', () => {
  const input = document.querySelector('#file');
  const zone = document.querySelector('#drop-zone');
  const selected = document.querySelector('#selected-file');
  const form = document.querySelector('#upload-form');
  const progress = document.querySelector('#embedding-progress');
  const progressMessage = document.querySelector('#progress-message');

  const showFile = (file) => {
    if (!file || !selected) return;
    selected.textContent = `${file.name} · ${(file.size / 1048576).toFixed(2)} MB`;
    zone.classList.add('dragging');
  };
  input?.addEventListener('change', () => showFile(input.files[0]));
  ['dragenter', 'dragover'].forEach((name) => zone?.addEventListener(name, (event) => {
    event.preventDefault(); zone.classList.add('dragging');
  }));
  ['dragleave', 'drop'].forEach((name) => zone?.addEventListener(name, (event) => {
    event.preventDefault();
    if (name === 'drop' && event.dataTransfer.files[0]) {
      input.files = event.dataTransfer.files; showFile(event.dataTransfer.files[0]);
    }
    if (name === 'dragleave') zone.classList.remove('dragging');
  }));
  form?.addEventListener('submit', () => {
    progress?.classList.add('active');
    const messages = ['Uploading PDF...', 'Generating embeddings...', 'Creating vector database...', 'Almost done...'];
    let index = 0;
    progressMessage.textContent = messages[index];
    const timer = setInterval(() => { index = Math.min(index + 1, messages.length - 1); progressMessage.textContent = messages[index]; }, 1200);
    window.addEventListener('pagehide', () => clearInterval(timer), { once: true });
    const button = document.querySelector('#upload-button');
    if (button) { button.disabled = true; button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Processing...'; }
  });
  document.querySelectorAll('[data-confirm-delete]').forEach((deleteForm) => deleteForm.addEventListener('submit', (event) => {
    if (!window.confirm('Delete the uploaded PDF, embeddings, metadata, and chat history?')) event.preventDefault();
  }));
});
