document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('messages');

  function formatTime(d = new Date()) {
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }

  function appendMessage(role, text) {
    const wrapper = document.createElement('div');
    wrapper.className = role === 'user' ? 'flex justify-end items-end' : 'flex justify-start items-start';

  const avatar = document.createElement('div');
  avatar.className = 'w-10 h-10 rounded-full flex items-center justify-center text-sm font-semibold mr-3';
  avatar.style.background = role === 'user' ? '#2563EB' : '#374151';

  const bubbleWrap = document.createElement('div');
  bubbleWrap.className = 'flex flex-col';

  const meta = document.createElement('div');
  const bubble = document.createElement('div');
  bubble.className = 'max-w-[72%] px-4 py-3 rounded-lg';
  bubble.style.background = role === 'user' ? '#2563EB' : '#111827';

  bubbleWrap.appendChild(meta);
  bubbleWrap.appendChild(bubble);

  if (role === 'user') {
      wrapper.appendChild(bubbleWrap);
      wrapper.appendChild(avatar);
    } else {
      wrapper.appendChild(avatar);
      wrapper.appendChild(bubbleWrap);
    }

    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();

  if (!text) return;
  appendMessage('user', text);
  input.value = '';

  // loader
  const loader = document.createElement('div');
  loader.className = 'flex justify-start';

  loader.innerHTML = '<div class="max-w-[72%] px-4 py-3 rounded-lg" style="background:#111827;color:#F9FAFB">...</div>';
  messages.appendChild(loader);
  messages.scrollTop = messages.scrollHeight;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
  const data = await res.json();
  messages.removeChild(loader);
  const assistant = data.choices && data.choices[0] ? data.choices[0].content : JSON.stringify(data);
      appendMessage('assistant', assistant);
    } catch (err) {
      messages.removeChild(loader);
      appendMessage('assistant', 'Error: could not reach server');
    }
  });
});
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('chat-form');
  const input = document.getElementById('chat-input');
  const messages = document.getElementById('messages');

  function appendMessage(role, text) {
    const wrapper = document.createElement('div');
    wrapper.className = role === 'user' ? 'flex justify-end my-2' : 'flex justify-start my-2';
    const bubble = document.createElement('div');
    bubble.className = 'max-w-xl px-4 py-2 rounded-lg shadow ' + (role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-800 text-gray-100');
    bubble.textContent = text;
    wrapper.appendChild(bubble);
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
  }

  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    appendMessage('user', text);
    input.value = '';

    // show loader
    const loader = document.createElement('div');
    loader.className = 'flex justify-start my-2';
    loader.innerHTML = '<div class="max-w-xl px-4 py-2 rounded-lg shadow bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-100">...</div>';
    messages.appendChild(loader);
    messages.scrollTop = messages.scrollHeight;

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: text }),
      });
      const data = await res.json();
      // remove loader
      messages.removeChild(loader);
      const assistant = data.choices && data.choices[0] ? data.choices[0].content : JSON.stringify(data);
      appendMessage('assistant', assistant);
    } catch (err) {
      messages.removeChild(loader);
      appendMessage('assistant', 'Error: could not reach server');
    }
  });

  // Dark mode is always enabled by default for this UI.
});
