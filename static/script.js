/**
 * ChatCure AI - Frontend Medical Application Engine
 * ==================================================
 * Provides interactive medical chat behaviors, markdown parsing,
 * conversation management, modals, dark/light theme switching,
 * auto-scroll, copy utilities, and export capabilities.
 */

document.addEventListener("DOMContentLoaded", () => {
  // -------------------------------------------------------------------------
  // DOM Elements
  // -------------------------------------------------------------------------
  const chatForm = document.getElementById("chatForm");
  const messageInput = document.getElementById("messageInput");
  const sendBtn = document.getElementById("sendBtn");
  const sendSpinner = document.getElementById("sendSpinner");
  const clearInputBtn = document.getElementById("clearInputBtn");
  const charCounter = document.getElementById("charCounter");
  const chatMessages = document.getElementById("chatMessages");
  const welcomeCard = document.getElementById("welcomeCard");
  const typingIndicator = document.getElementById("typingIndicator");
  const scrollBottomBtn = document.getElementById("scrollBottomBtn");
  const themeToggleBtn = document.getElementById("themeToggleBtn");
  const clearChatBtn = document.getElementById("clearChatBtn");
  const exportChatBtn = document.getElementById("exportChatBtn");
  const toastContainer = document.getElementById("toastContainer");

  // Modals
  const emergencyModal = document.getElementById("emergencyModal");
  const disclaimerModal = document.getElementById("disclaimerModal");
  const topicsModal = document.getElementById("topicsModal");
  const confirmClearModal = document.getElementById("confirmClearModal");
  const confirmClearBtn = document.getElementById("confirmClearBtn");

  // Triggers
  const openEmergencyBtn = document.getElementById("openEmergencyBtn");
  const openDisclaimerBtn = document.getElementById("openDisclaimerBtn");
  const openTopicsBtn = document.getElementById("openTopicsBtn");
  const footerEmergencyBtn = document.getElementById("footerEmergencyBtn");
  const footerDisclaimerBtn = document.getElementById("footerDisclaimerBtn");
  const footerTopicsBtn = document.getElementById("footerTopicsBtn");

  // -------------------------------------------------------------------------
  // State
  // -------------------------------------------------------------------------
  let conversationHistory = []; // Array of { role: 'user'|'assistant', content: string, timestamp: string }
  let isAwaitingResponse = false;
  const STORAGE_KEY = "chatcure_conversation_v1";
  const THEME_KEY = "chatcure_theme";

  // -------------------------------------------------------------------------
  // Theme Management
  // -------------------------------------------------------------------------
  function initTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY);
    const prefersDark = window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches;
    const initialTheme = savedTheme || (prefersDark ? "dark" : "light");
    document.documentElement.setAttribute("data-theme", initialTheme);
  }

  function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute("data-theme") || "light";
    const newTheme = currentTheme === "light" ? "dark" : "light";
    document.documentElement.setAttribute("data-theme", newTheme);
    localStorage.setItem(THEME_KEY, newTheme);
    showToast(`Switched to ${newTheme === "dark" ? "Clinical Dark" : "Clean Hospital"} theme`);
  }

  themeToggleBtn.addEventListener("click", toggleTheme);
  initTheme();

  // -------------------------------------------------------------------------
  // Markdown Configuration & Sanitization
  // -------------------------------------------------------------------------
  if (typeof marked !== "undefined") {
    marked.setOptions({
      gfm: true,
      breaks: true,
      sanitize: false // We use DOMPurify instead
    });
  }

  function renderSafeMarkdown(content) {
    if (typeof marked !== "undefined" && typeof DOMPurify !== "undefined") {
      const rawHtml = marked.parse(content);
      return DOMPurify.sanitize(rawHtml);
    }
    // Fallback: simple text with escaped HTML and line breaks
    const div = document.createElement("div");
    div.textContent = content;
    return div.innerHTML.replace(/\n/g, "<br>");
  }

  // -------------------------------------------------------------------------
  // Time Formatting
  // -------------------------------------------------------------------------
  function formatTimestamp(isoOrDate = new Date()) {
    const date = typeof isoOrDate === "string" ? new Date(isoOrDate) : isoOrDate;
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  // -------------------------------------------------------------------------
  // Toast Notifications
  // -------------------------------------------------------------------------
  function showToast(message, type = "success") {
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `<span>${type === "success" ? "✓" : "⚠️"}</span> <span>${message}</span>`;
    toastContainer.appendChild(toast);

    setTimeout(() => {
      toast.style.opacity = "0";
      toast.style.transform = "translateX(40px)";
      toast.style.transition = "all 0.3s ease";
      setTimeout(() => toast.remove(), 300);
    }, 3200);
  }

  // -------------------------------------------------------------------------
  // Auto-scroll Logic
  // -------------------------------------------------------------------------
  function scrollToBottom(smooth = true) {
    chatMessages.scrollTo({
      top: chatMessages.scrollHeight,
      behavior: smooth ? "smooth" : "auto"
    });
  }

  chatMessages.addEventListener("scroll", () => {
    const distanceFromBottom = chatMessages.scrollHeight - chatMessages.scrollTop - chatMessages.clientHeight;
    if (distanceFromBottom > 150) {
      scrollBottomBtn.classList.remove("hidden");
    } else {
      scrollBottomBtn.classList.add("hidden");
    }
  });

  scrollBottomBtn.addEventListener("click", () => {
    scrollToBottom(true);
  });

  // -------------------------------------------------------------------------
  // Message Rendering
  // -------------------------------------------------------------------------
  function appendUserMessage(text, timestamp = new Date()) {
    if (welcomeCard) {
      welcomeCard.style.display = "none";
    }

    const row = document.createElement("div");
    row.className = "message-row user-row";

    const timeStr = formatTimestamp(timestamp);

    row.innerHTML = `
      <div class="message-avatar user-avatar" title="You">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
          <circle cx="12" cy="7" r="4"/>
        </svg>
      </div>
      <div class="message-bubble-wrapper">
        <div class="message-bubble user-bubble">${escapeHtml(text)}</div>
        <div class="message-meta">
          <span class="message-timestamp">${timeStr}</span>
        </div>
      </div>
    `;

    chatMessages.appendChild(row);
    scrollToBottom(true);
  }

  function appendAIMessage(content, timestamp = new Date(), model = "") {
    if (welcomeCard) {
      welcomeCard.style.display = "none";
    }

    const row = document.createElement("div");
    row.className = "message-row ai-row";

    const timeStr = formatTimestamp(timestamp);
    const renderedHtml = renderSafeMarkdown(content);

    row.innerHTML = `
      <div class="message-avatar ai-avatar" title="Dr. ChatCure AI">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M12 2v20"/>
          <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
        </svg>
      </div>
      <div class="message-bubble-wrapper">
        <div class="message-bubble ai-bubble">${renderedHtml}</div>
        <div class="message-meta">
          <span class="medical-tag">⚕️ Health Info</span>
          <span class="message-timestamp">${timeStr}</span>
          <button type="button" class="btn-copy-msg" title="Copy response to clipboard">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
              <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
            </svg>
            <span>Copy</span>
          </button>
        </div>
      </div>
    `;

    // Attach copy button action
    const copyBtn = row.querySelector(".btn-copy-msg");
    copyBtn.addEventListener("click", () => {
      copyToClipboard(content, copyBtn);
    });

    chatMessages.appendChild(row);
    scrollToBottom(true);
  }

  function escapeHtml(string) {
    const p = document.createElement("p");
    p.textContent = string;
    return p.innerHTML;
  }

  // -------------------------------------------------------------------------
  // Copy Utility
  // -------------------------------------------------------------------------
  async function copyToClipboard(text, buttonElement) {
    try {
      await navigator.clipboard.writeText(text);
      if (buttonElement) {
        const originalText = buttonElement.innerHTML;
        buttonElement.innerHTML = `
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:13px;height:13px;color:var(--emerald-500);">
            <polyline points="20 6 9 17 4 12"/>
          </svg>
          <span style="color:var(--emerald-500);font-weight:700;">Copied!</span>
        `;
        setTimeout(() => {
          buttonElement.innerHTML = originalText;
        }, 2000);
      }
      showToast("Medical guidance copied to clipboard");
    } catch (err) {
      console.error("Clipboard copy failed: ", err);
      showToast("Unable to copy to clipboard", "error");
    }
  }

  // -------------------------------------------------------------------------
  // Input Handling & Auto-Expanding Textarea
  // -------------------------------------------------------------------------
  function updateTextareaHeight() {
    messageInput.style.height = "auto";
    messageInput.style.height = `${Math.min(messageInput.scrollHeight, 150)}px`;
  }

  function updateInputControls() {
    const text = messageInput.value;
    const len = text.length;
    charCounter.textContent = `${len}/3000`;

    if (len > 0) {
      clearInputBtn.classList.remove("hidden");
    } else {
      clearInputBtn.classList.add("hidden");
    }
    updateTextareaHeight();
  }

  messageInput.addEventListener("input", updateInputControls);

  clearInputBtn.addEventListener("click", () => {
    messageInput.value = "";
    updateInputControls();
    messageInput.focus();
  });

  // Enter to send, Shift+Enter for newline
  messageInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      if (!isAwaitingResponse && messageInput.value.trim().length > 0) {
        sendMessage();
      }
    }
  });

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    if (!isAwaitingResponse && messageInput.value.trim().length > 0) {
      sendMessage();
    }
  });

  // -------------------------------------------------------------------------
  // Send Message Logic (Async OpenRouter /chat Endpoint)
  // -------------------------------------------------------------------------
  async function sendMessage(presetText = null) {
    const rawText = presetText || messageInput.value;
    const cleanText = rawText.trim();

    if (!cleanText || isAwaitingResponse) return;

    // Reset input
    if (!presetText) {
      messageInput.value = "";
      updateInputControls();
    }

    const userTimestamp = new Date();
    appendUserMessage(cleanText, userTimestamp);

    // Save to conversation history
    conversationHistory.push({
      role: "user",
      content: cleanText,
      timestamp: userTimestamp.toISOString()
    });
    saveHistoryToStorage();

    // Set UI Loading state
    setLoadingState(true);

    try {
      // Prepare payload with history context
      const payload = {
        message: cleanText,
        history: conversationHistory.slice(-8).map(m => ({
          role: m.role,
          content: m.content
        }))
      };

      const response = await fetch("/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
      });

      const data = await response.json();

      if (!response.ok || !data.success) {
        const errorMsg = data.error || `Server responded with status ${response.status}`;
        appendAIMessage(`### ⚠️ Consultation Error\n\n${errorMsg}\n\n*Please ensure your server and API key are configured properly.*`);
        showToast(errorMsg, "error");
      } else {
        const aiText = data.response;
        const aiTimestamp = data.timestamp || new Date().toISOString();
        appendAIMessage(aiText, aiTimestamp, data.model);

        conversationHistory.push({
          role: "assistant",
          content: aiText,
          timestamp: aiTimestamp
        });
        saveHistoryToStorage();
      }
    } catch (networkError) {
      console.error("Chat communication failure:", networkError);
      const errMsg = "Unable to connect to the medical AI service. Please verify your connection or check if the backend server is running.";
      appendAIMessage(`### 🔌 Network Disconnection\n\n${errMsg}`);
      showToast("Network connection error", "error");
    } finally {
      setLoadingState(false);
      messageInput.focus();
    }
  }

  function setLoadingState(loading) {
    isAwaitingResponse = loading;
    sendBtn.disabled = loading;

    if (loading) {
      sendSpinner.classList.remove("hidden");
      document.querySelector(".btn-send-text").textContent = "Thinking...";
      document.querySelector(".btn-send-icon").classList.add("hidden");
      typingIndicator.classList.remove("hidden");
      scrollToBottom(true);
    } else {
      sendSpinner.classList.add("hidden");
      document.querySelector(".btn-send-text").textContent = "Send";
      document.querySelector(".btn-send-icon").classList.remove("hidden");
      typingIndicator.classList.add("hidden");
    }
  }

  // -------------------------------------------------------------------------
  // LocalStorage Persistence
  // -------------------------------------------------------------------------
  function saveHistoryToStorage() {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(conversationHistory));
    } catch (e) {
      console.warn("Storage quota exceeded or disabled", e);
    }
  }

  function loadHistoryFromStorage() {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      if (saved) {
        const parsed = JSON.parse(saved);
        if (Array.isArray(parsed) && parsed.length > 0) {
          conversationHistory = parsed;
          if (welcomeCard) welcomeCard.style.display = "none";

          parsed.forEach(msg => {
            if (msg.role === "user") {
              appendUserMessage(msg.content, msg.timestamp);
            } else {
              appendAIMessage(msg.content, msg.timestamp);
            }
          });
          scrollToBottom(false);
        }
      }
    } catch (e) {
      console.warn("Could not load stored conversation", e);
    }
  }

  loadHistoryFromStorage();

  // -------------------------------------------------------------------------
  // Clear Chat Functionality
  // -------------------------------------------------------------------------
  clearChatBtn.addEventListener("click", () => {
    if (conversationHistory.length === 0) {
      showToast("No active conversation to clear");
      return;
    }
    openModal(confirmClearModal);
  });

  confirmClearBtn.addEventListener("click", () => {
    conversationHistory = [];
    localStorage.removeItem(STORAGE_KEY);

    // Remove all message rows
    const rows = chatMessages.querySelectorAll(".message-row");
    rows.forEach(r => r.remove());

    // Restore welcome card
    if (welcomeCard) {
      welcomeCard.style.display = "flex";
    }

    closeModal(confirmClearModal);
    showToast("Consultation history cleared successfully");
  });

  // -------------------------------------------------------------------------
  // Export Chat
  // -------------------------------------------------------------------------
  exportChatBtn.addEventListener("click", () => {
    if (conversationHistory.length === 0) {
      showToast("Nothing to export yet!", "error");
      return;
    }

    let markdown = `# ChatCure AI - Medical Consultation Record\n`;
    markdown += `Generated on: ${new Date().toLocaleString()}\n`;
    markdown += `*Disclaimer: Educational health notes only. Consult a doctor for clinical care.*\n\n---\n\n`;

    conversationHistory.forEach((msg, idx) => {
      const speaker = msg.role === "user" ? "Patient" : "Dr. ChatCure AI";
      const time = formatTimestamp(msg.timestamp);
      markdown += `### [${time}] ${speaker}:\n\n${msg.content}\n\n---\n\n`;
    });

    const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `chatcure-consultation-${new Date().toISOString().slice(0, 10)}.md`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);

    showToast("Medical consultation transcript downloaded");
  });

  // -------------------------------------------------------------------------
  // Quick Suggestion Chips & Modal Topic Clicks
  // -------------------------------------------------------------------------
  document.getElementById("suggestionChips").addEventListener("click", (e) => {
    const btn = e.target.closest(".chip-btn");
    if (btn) {
      const query = btn.getAttribute("data-query");
      if (query) {
        sendMessage(query);
      }
    }
  });

  topicsModal.addEventListener("click", (e) => {
    const box = e.target.closest(".topic-box");
    if (box) {
      const query = box.getAttribute("data-query");
      if (query) {
        closeModal(topicsModal);
        sendMessage(query);
      }
    }
  });

  // -------------------------------------------------------------------------
  // Modal Management
  // -------------------------------------------------------------------------
  function openModal(modal) {
    if (!modal) return;
    modal.classList.remove("hidden");
    document.body.style.overflow = "hidden";
  }

  function closeModal(modal) {
    if (!modal) return;
    modal.classList.add("hidden");
    document.body.style.overflow = "";
  }

  // Close modal via data-close attribute
  document.addEventListener("click", (e) => {
    const closeBtn = e.target.closest("[data-close]");
    if (closeBtn) {
      const targetId = closeBtn.getAttribute("data-close");
      const targetModal = document.getElementById(targetId);
      if (targetModal) closeModal(targetModal);
    }

    // Close when clicking directly on backdrop
    if (e.target.classList.contains("modal-backdrop")) {
      closeModal(e.target);
    }
  });

  // Close modals on Escape key
  document.addEventListener("keydown", (e) => {
    if (e.key === "Escape") {
      const openModals = document.querySelectorAll(".modal-backdrop:not(.hidden)");
      openModals.forEach(m => closeModal(m));
    }
  });

  // Trigger bindings
  if (openEmergencyBtn) openEmergencyBtn.addEventListener("click", () => openModal(emergencyModal));
  if (footerEmergencyBtn) footerEmergencyBtn.addEventListener("click", () => openModal(emergencyModal));

  if (openDisclaimerBtn) openDisclaimerBtn.addEventListener("click", () => openModal(disclaimerModal));
  if (footerDisclaimerBtn) footerDisclaimerBtn.addEventListener("click", () => openModal(disclaimerModal));

  if (openTopicsBtn) openTopicsBtn.addEventListener("click", () => openModal(topicsModal));
  if (footerTopicsBtn) footerTopicsBtn.addEventListener("click", () => openModal(topicsModal));

  // Current year in footer
  const currentYearSpan = document.getElementById("currentYear");
  if (currentYearSpan) {
    currentYearSpan.textContent = new Date().getFullYear();
  }
});
