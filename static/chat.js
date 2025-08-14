/**
 * Enhanced chat interface for Pydantic structured output demo
 * Supports conversation context and advanced LLM features
 */
document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('chat-form');
  const input = document.getElementById('user-input');
  const messages = document.getElementById('chat-window');
  
  // Conversation state
  let conversationId = null;
  let isProcessing = false;

  function generateConversationId() {
    return 'conv_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
  }

  function formatTime(date = new Date()) {
    return date.toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      hour12: false
    });
  }

  function appendMessage(role, content, metadata = {}) {
    const wrapper = document.createElement('div');
    wrapper.className = `message-wrapper ${role}-message mb-4`;
    
    const messageContainer = document.createElement('div');
    messageContainer.className = role === 'user' 
      ? 'flex justify-end items-start space-x-2' 
      : 'flex justify-start items-start space-x-2';
    
    // Avatar
    const avatar = document.createElement('div');
    avatar.className = 'flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold';
    avatar.style.backgroundColor = role === 'user' ? '#2563EB' : '#374151';
    avatar.style.color = '#ffffff';
    avatar.textContent = role === 'user' ? 'U' : 'AI';
    
    // Message bubble
    const bubble = document.createElement('div');
    bubble.className = 'max-w-[75%] px-4 py-3 rounded-lg break-words';
    bubble.style.backgroundColor = role === 'user' ? '#2563EB' : '#111827';
    bubble.style.color = role === 'user' ? '#ffffff' : '#F9FAFB';
    
    // Handle different content types
    if (typeof content === 'string') {
      bubble.textContent = content;
    } else if (typeof content === 'object') {
      bubble.textContent = JSON.stringify(content, null, 2);
      bubble.style.fontFamily = 'monospace';
      bubble.style.fontSize = '0.875rem';
    }
    
    // Metadata (timestamp, model info, etc.)
    if (Object.keys(metadata).length > 0) {
      const metaDiv = document.createElement('div');
      metaDiv.className = 'text-xs text-gray-400 mt-1 px-1';
      
      const metaInfo = [];
      if (metadata.timestamp) metaInfo.push(formatTime(new Date(metadata.timestamp)));
      if (metadata.model) metaInfo.push(`Model: ${metadata.model}`);
      if (metadata.generation_time_ms) metaInfo.push(`${metadata.generation_time_ms}ms`);
      
      metaDiv.textContent = metaInfo.join(' • ');
      bubble.appendChild(metaDiv);
    }
    
    // Assemble message
    if (role === 'user') {
      messageContainer.appendChild(bubble);
      messageContainer.appendChild(avatar);
    } else {
      messageContainer.appendChild(avatar);
      messageContainer.appendChild(bubble);
    }
    
    wrapper.appendChild(messageContainer);
    messages.appendChild(wrapper);
    messages.scrollTop = messages.scrollHeight;
    
    return wrapper;
  }

  function showTypingIndicator() {
    const indicator = document.createElement('div');
    indicator.id = 'typing-indicator';
    indicator.className = 'flex justify-start items-start space-x-2 mb-4';
    
    indicator.innerHTML = `
      <div class="flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold" 
           style="background-color: #374151; color: #ffffff;">AI</div>
      <div class="max-w-[75%] px-4 py-3 rounded-lg" style="background-color: #111827; color: #F9FAFB;">
        <div class="typing-animation">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
    
    messages.appendChild(indicator);
    messages.scrollTop = messages.scrollHeight;
    return indicator;
  }

  function removeTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
      indicator.remove();
    }
  }

  function showError(message) {
    appendMessage('assistant', `❌ Error: ${message}`, {
      timestamp: new Date().toISOString()
    });
  }

  async function checkServiceHealth() {
    try {
      const response = await fetch('/api/health');
      const data = await response.json();
      return data.status === 'healthy';
    } catch (error) {
      console.error('Health check failed:', error);
      return false;
    }
  }

  async function sendMessage(message) {
    if (isProcessing) return;
    
    isProcessing = true;
    
    // Initialize conversation ID if not exists
    if (!conversationId) {
      conversationId = generateConversationId();
    }
    
    // Show user message
    appendMessage('user', message, {
      timestamp: new Date().toISOString()
    });
    
    // Show typing indicator
    const typingIndicator = showTypingIndicator();
    
    try {
      const requestPayload = {
        message: message,
        conversation_id: conversationId,
        temperature: 0.7
      };
      
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestPayload)
      });
      
      // Remove typing indicator
      removeTypingIndicator();
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.message || `HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      // Handle error responses
      if (data.error) {
        showError(data.message || 'Unknown error occurred');
        return;
      }
      
      // Extract response content
      let assistantContent = 'No response received';
      let metadata = {};
      
      if (data.choices && data.choices.length > 0) {
        const choice = data.choices[0];
        assistantContent = choice.message?.content || choice.content || assistantContent;
      }
      
      // Extract metadata
      if (data.metadata) {
        metadata = {
          timestamp: data.created || new Date().toISOString(),
          model: data.metadata.model_name,
          generation_time_ms: data.metadata.generation_time_ms
        };
      }
      
      // Show assistant response
      appendMessage('assistant', assistantContent, metadata);
      
    } catch (error) {
      removeTypingIndicator();
      console.error('Chat error:', error);
      
      // Check if it's a service availability issue
      const isHealthy = await checkServiceHealth();
      if (!isHealthy) {
        showError('LLM service is not available. Please check that gpt-oss:20b is running.');
      } else {
        showError(error.message || 'Failed to send message');
      }
    } finally {
      isProcessing = false;
    }
  }

  // Form submission handler
  form.addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const message = input.value.trim();
    if (!message || isProcessing) return;
    
    // Clear input
    input.value = '';
    
    // Send message
    await sendMessage(message);
  });

  // Keyboard shortcuts
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      form.dispatchEvent(new Event('submit'));
    }
  });

  // Initial health check
  checkServiceHealth().then(isHealthy => {
    if (!isHealthy) {
      appendMessage('assistant', 
        '⚠️  LLM service appears to be offline. Please ensure gpt-oss:20b is running on your local machine.', 
        { timestamp: new Date().toISOString() }
      );
    } else {
      appendMessage('assistant', 
        '🤖 Hello! I\'m connected to gpt-oss:20b. Ask me anything to see Pydantic structured output in action!', 
        { timestamp: new Date().toISOString() }
      );
    }
  });
});

// Add CSS for typing animation
const style = document.createElement('style');
style.textContent = `
  .typing-animation {
    display: flex;
    gap: 3px;
  }
  
  .typing-animation span {
    height: 8px;
    width: 8px;
    border-radius: 50%;
    background-color: #6B7280;
    display: inline-block;
    animation: typing 1.4s ease-in-out infinite both;
  }
  
  .typing-animation span:nth-child(1) { animation-delay: -0.32s; }
  .typing-animation span:nth-child(2) { animation-delay: -0.16s; }
  
  @keyframes typing {
    0%, 80%, 100% {
      transform: scale(0.8);
      opacity: 0.5;
    }
    40% {
      transform: scale(1);
      opacity: 1;
    }
  }
`;
document.head.appendChild(style);
