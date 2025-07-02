document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const chatInput = document.getElementById("chat-input");
  const chatWindow = document.getElementById("chat-window");
  const typingIndicator = document.getElementById("typing-indicator");
  const blogUrlInput = document.getElementById("blog-url");
  let conversationHistory = [];

  chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const message = chatInput.value.trim();
    const url = blogUrlInput.value.trim();

    if (!message) return;

    appendMessage(message, "user");
    chatInput.value = "";
    blogUrlInput.value = ""; // Clear URL input as well
    chatInput.style.height = "auto"; // Reset height

    showTypingIndicator();

    try {
      let endpoint = "/api/v1/agent/run";
      let body = { task: message, history: conversationHistory };

      if (url) {
        endpoint = "/api/v1/scraper/scrape-and-run";
        body = { url: url, task: message, history: conversationHistory };
      }

      const response = await fetch(endpoint, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(body),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }

      // Handle cases where the backend might send a JSON error instead of a stream
      const contentType = response.headers.get("content-type");
      if (contentType && contentType.includes("application/json")) {
        const errorData = await response.json();
        console.error("Received JSON instead of stream:", errorData);
        const errorMessage = errorData.detail || JSON.stringify(errorData);
        appendMessage(`An error occurred: ${errorMessage}`, "ai", true);
        hideTypingIndicator();
        return;
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let aiMessageContainer = appendMessage("", "ai");
      let isFirstChunk = true;
      let fullResponse = "";

      while (true) {
        const { value, done } = await reader.read();
        if (isFirstChunk) {
          hideTypingIndicator();
          isFirstChunk = false;
        }

        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        fullResponse += chunk;
        aiMessageContainer.innerHTML = marked.parse(fullResponse);
        chatWindow.scrollTop = chatWindow.scrollHeight;
      }
      conversationHistory.push({ user: message, ai: fullResponse });
    } catch (error) {
      hideTypingIndicator();
      console.error("Error running agent:", error);
      appendMessage(
        "An error occurred. Please check the console for details.",
        "ai",
        true
      );
    }
  });

  function appendMessage(content, type, isError = false) {
    const messageWrapper = document.createElement("div");
    messageWrapper.classList.add("chat-message", `${type}-message`);

    if (isError) {
      messageWrapper.style.color = "#d9534f"; // Bootstrap's danger color
    }

    // Use marked.parse to render markdown content for AI messages
    if (type === "ai") {
      messageWrapper.innerHTML = marked.parse(content);
    } else {
      messageWrapper.textContent = content;
    }

    chatWindow.appendChild(messageWrapper);
    chatWindow.scrollTop = chatWindow.scrollHeight;
    return messageWrapper; // Return for streaming updates
  }

  function showTypingIndicator() {
    typingIndicator.classList.remove("hidden");
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function hideTypingIndicator() {
    typingIndicator.classList.add("hidden");
  }

  // Handle Enter/Shift+Enter for input
  chatInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault(); // Prevent new line on Enter
      chatForm.requestSubmit(); // Trigger form submission
    }
  });

  // Auto-resize textarea
  chatInput.addEventListener("input", () => {
    chatInput.style.height = "auto";
    chatInput.style.height = `${chatInput.scrollHeight}px`;
  });
});
