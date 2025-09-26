document.addEventListener("DOMContentLoaded", () => {
  const chatWindow = document.getElementById("chatWindow");
  const userInput = document.getElementById("userInput");
  const sendBtn = document.getElementById("sendBtn");

  // Add loading indicator
  function showLoading() {
    const loadingDiv = document.createElement("div");
    loadingDiv.id = "loading-indicator";
    loadingDiv.classList.add("message", "bot", "loading");
    loadingDiv.innerHTML = '<p><strong>AI:</strong> <em>Thinking...</em> 🤔</p>';
    chatWindow.appendChild(loadingDiv);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function hideLoading() {
    const loadingDiv = document.getElementById("loading-indicator");
    if (loadingDiv) {
      loadingDiv.remove();
    }
  }

  function addMessage(text, sender) {
    const div = document.createElement("div");
    div.classList.add("message", sender);
    div.innerHTML = `<p><strong>${sender === "user" ? "You" : "AI"}:</strong> ${text}</p>`;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  async function getAIResponse(userMessage) {
    try {
      const response = await fetch("/api/query", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage })
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      const data = await response.json();
      return data.reply;
    } catch (err) {
      console.error("Error getting AI response:", err);
      return "Sorry, I'm having trouble connecting to the AI service right now. Please try again later.";
    }
  }

  async function handleSend() {
    const text = userInput.value.trim();
    if (!text) return;

    // Add user message
    addMessage(text, "user");
    userInput.value = "";
    
    // Disable input while processing
    userInput.disabled = true;
    sendBtn.disabled = true;
    
    // Show loading
    showLoading();

    try {
      // Get AI response
      const aiReply = await getAIResponse(text);
      
      // Hide loading and show response
      hideLoading();
      addMessage(aiReply, "bot");
    } catch (error) {
      hideLoading();
      addMessage("Error: " + error.message, "bot");
    } finally {
      // Re-enable input
      userInput.disabled = false;
      sendBtn.disabled = false;
      userInput.focus();
    }
  }

  // Add predefined query buttons
  function addPredefinedQueries() {
    const predefinedQueries = [
      "What problems are teams facing right now?",
      "What are the most asked questions?",
      "What topics are trending in the chat?",
      "Summarize the current hackathon activity"
    ];

    const queryContainer = document.createElement("div");
    queryContainer.className = "predefined-queries mt-3";
    queryContainer.innerHTML = `
      <h6>Quick Questions:</h6>
      <div class="d-flex flex-wrap gap-2">
        ${predefinedQueries.map(query => 
          `<button class="btn btn-outline-primary btn-sm query-btn" data-query="${query}">${query}</button>`
        ).join('')}
      </div>
    `;

    // Insert after chat window
    chatWindow.parentNode.insertBefore(queryContainer, chatWindow.nextSibling);

    // Add click handlers for predefined queries
    document.querySelectorAll('.query-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const query = btn.getAttribute('data-query');
        userInput.value = query;
        handleSend();
      });
    });
  }

  // Initialize predefined queries
  addPredefinedQueries();

  // 🔹 Button click
  sendBtn.addEventListener("click", handleSend);

  // 🔹 Press Enter key
  userInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
      e.preventDefault(); // stop form submit
      handleSend();
    }
  });

  // Auto-focus input
  userInput.focus();
});
