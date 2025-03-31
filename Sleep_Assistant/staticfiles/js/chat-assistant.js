// Chat Assistant JavaScript
// Theme toggle functionality
const themeToggle = document.getElementById('themeToggle');
const body = document.body;

// Check for saved theme in localStorage
const savedTheme = localStorage.getItem('theme');
if (savedTheme) {
    body.setAttribute('data-theme', savedTheme);
    themeToggle.classList.toggle('active', savedTheme === 'dark');
}

themeToggle.addEventListener('click', () => {
    const isDark = body.getAttribute('data-theme') === 'dark';
    body.setAttribute('data-theme', isDark ? 'light' : 'dark');
    localStorage.setItem('theme', isDark ? 'light' : 'dark');
    themeToggle.classList.toggle('active', !isDark);
});

// Role selector functionality
const roleButtons = document.querySelectorAll('.role-btn');
roleButtons.forEach(button => {
    button.addEventListener('click', () => {
        roleButtons.forEach(btn => btn.classList.remove('active'));
        button.classList.add('active');
        // Add logic to change assistant role here
    });
});

// Loading state for send button
const sendBtn = document.getElementById('sendBtn');
sendBtn.addEventListener('click', () => {
    sendBtn.classList.add('loading');
    // Add your chat logic here
    setTimeout(() => {
        sendBtn.classList.remove('loading');
    }, 2000); // Simulate loading for 2 seconds
});
document.addEventListener('DOMContentLoaded', function() {
    // Chat elements
    const chatBody = document.getElementById('chatBody');
    const chatInput = document.getElementById('chatInput');
    const sendBtn = document.getElementById('sendBtn');
    const stopBtn = document.getElementById('stopBtn');
    const roleButtons = document.querySelectorAll('.role-btn');
    
    let controller = null;
    let isStreaming = false;
    let currentRole = 'default';
    let conversationHistory = [];

    // Role prompts
    const rolePrompts = {
        default: "你是一个专业的睡眠助手，请用专业但友好的语气回答用户关于睡眠的问题。",
        sister: "你是一个知心大姐姐，请用温暖、关怀的语气与用户交流，帮助他们解决睡眠问题。",
        doctor: "你是一个专业的睡眠医生，请用专业的医学知识帮助用户分析和解决睡眠问题。",
        coach: "你是一个睡眠教练，请用激励和指导的方式帮助用户改善睡眠习惯。"
    };

    // Initialize role selection
    roleButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Remove active class from all buttons
            roleButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            this.classList.add('active');
            // Update current role
            currentRole = this.dataset.role;
            // Clear conversation history when changing roles
            conversationHistory = [{
                role: "system",
                content: rolePrompts[currentRole]
            }];
            // Clear chat body
            chatBody.innerHTML = '';
            // Add welcome message
            addMessage('assistant', getWelcomeMessage(currentRole));
        });
    });

    // Set default role
    roleButtons[0].click();

    // Send message handler
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendMessage();
        }
    });

    // Stop streaming handler
    stopBtn.addEventListener('click', function() {
        if (controller && isStreaming) {
            controller.abort();
            isStreaming = false;
            stopBtn.disabled = true;
            addMessage('assistant', '响应已停止');
        }
    });

    async function sendMessage() {
        const message = chatInput.value.trim();
        if (!message) return;

        // Add user message
        addMessage('user', message);
        conversationHistory.push({role: "user", content: message});
        chatInput.value = '';
        stopBtn.disabled = false;
        isStreaming = true;

        try {
            controller = new AbortController();
            const signal = controller.signal;

            const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer sk-45418e33045a453b9b00a7d63b161c9e`
                },
                body: JSON.stringify({
                    model: "deepseek-chat",
                    messages: conversationHistory,
                    temperature: 0.7,
                    stream: true
                }),
                signal
            });

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessage = '';

            // Create message container
            const messageDiv = document.createElement('div');
            messageDiv.classList.add('message', 'assistant-message');
            chatBody.appendChild(messageDiv);

            while (true) {
                const { done, value } = await reader.read();
                if (done) {
                    isStreaming = false;
                    stopBtn.disabled = true;
                    // Add final message to history
                    conversationHistory.push({role: "assistant", content: assistantMessage});
                    break;
                }

                const chunk = decoder.decode(value);
                const lines = chunk.split('\n');
                
                lines.forEach(line => {
                    if (line.startsWith('data: ')) {
                        const data = line.replace('data: ', '');
                        if (data === '[DONE]') return;
                        
                        try {
                            const json = JSON.parse(data);
                            const content = json.choices[0].delta.content;
                            if (content) {
                                assistantMessage += content;
                                messageDiv.textContent = assistantMessage;
                                chatBody.scrollTop = chatBody.scrollHeight;
                            }
                        } catch (error) {
                            console.error('Error parsing stream:', error);
                        }
                    }
                });
            }
        } catch (error) {
            if (error.name !== 'AbortError') {
                console.error('Error:', error);
                addMessage('assistant', '抱歉，出现了一些问题，请稍后再试。');
            }
            isStreaming = false;
            stopBtn.disabled = true;
        }
    }

    function addMessage(sender, text) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(sender === 'user' ? 'user-message' : 'assistant-message');
        messageDiv.textContent = text;
        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    function getWelcomeMessage(role) {
        switch(role) {
            case 'sister':
                return "你好呀~我是你的知心大姐姐，有什么睡眠方面的烦恼都可以跟我说哦！";
            case 'doctor':
                return "您好，我是您的睡眠医生，请详细描述您的睡眠问题，我会为您提供专业的建议。";
            case 'coach':
                return "你好！我是你的睡眠教练，让我们一起制定计划，改善你的睡眠质量吧！";
            default:
                return "您好，我是您的睡眠助手，请问有什么可以帮助您的吗？";
        }
    }
});
