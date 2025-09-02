function formatText(text) {
    // Если потребуется обработка Markdown (сейчас можно оставить как есть)
    return text;
  }
  
  function addMessage(role, text) {
    const chatBox = document.getElementById("chat-box");
    const messageDiv = document.createElement("div");
    messageDiv.classList.add("message");
    messageDiv.classList.add(role === "user" ? "user-message" : "bot-message");
    messageDiv.innerHTML = `<div class="message-text">${formatText(text)}</div>`;
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
  }
  
  function askQuestion(customQuestion) {
    const inputEl = document.getElementById("question");
    const question = customQuestion || inputEl.value;
    if (!question.trim()) return;
    
    // Добавляем сообщение пользователя
    addMessage("user", question);
    inputEl.value = "";
    
    // Показываем индикатор "Печатает..."
    const typingIndicator = document.getElementById("typing-indicator");
    typingIndicator.style.display = "block";
    
    fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question })
    })
    .then(response => response.json())
    .then(data => {
      addMessage("bot", data.answer);
      typingIndicator.style.display = "none";
    })
    .catch(err => {
      console.error(err);
      typingIndicator.style.display = "none";
    });
  }
  
  document.addEventListener("DOMContentLoaded", function() {
    // Если чат пустой – автоматически отправляем "Расскажи о себе"
    const chatBox = document.getElementById("chat-box");
    if (chatBox.children.length === 0) {
      askQuestion("Расскажи о себе");
    }
  });
  