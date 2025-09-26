document.addEventListener("DOMContentLoaded", () => {
  const refreshBtn = document.getElementById("refreshBtn");
  const lastUpdateElement = document.getElementById("lastUpdate");
  
  // Auto-refresh every 30 seconds
  let autoRefreshInterval;
  
  function updateTimestamp() {
    const now = new Date();
    lastUpdateElement.textContent = `Last updated: ${now.toLocaleTimeString()}`;
  }
  
  async function fetchStats() {
    try {
      const response = await fetch("/api/stats");
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const stats = await response.json();
      
      // Update stat cards
      document.getElementById("totalMessages").textContent = stats.total_messages || 0;
      document.getElementById("uniqueUsers").textContent = stats.unique_users || 0;
      document.getElementById("questionsCount").textContent = stats.questions_count || 0;
      document.getElementById("problemsCount").textContent = stats.problems_count || 0;
      
    } catch (error) {
      console.error("Error fetching stats:", error);
      // Show error in stat cards
      document.getElementById("totalMessages").textContent = "Error";
      document.getElementById("uniqueUsers").textContent = "Error";
      document.getElementById("questionsCount").textContent = "Error";
      document.getElementById("problemsCount").textContent = "Error";
    }
  }
  
  async function fetchInsights() {
    try {
      const response = await fetch("/api/insights");
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const insights = await response.json();
      
      // Update insight cards with rich formatting
      let problemsText = insights.problems || "No problems detected recently.";
      let questionsText = insights.questions || "No questions found recently.";
      let trendingText = insights.trending || "No trending topics identified.";
      
      // Clean up any remaining markdown
      problemsText = problemsText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      questionsText = questionsText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      trendingText = trendingText.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
      
      // Count items in each section
      const problemsCount = (problemsText.match(/\d+\./g) || []).length;
      const questionsCount = (questionsText.match(/&bull;/g) || []).length;
      const trendsCount = (trendingText.match(/<strong>.*?:<\/strong>/g) || []).length;
      
      // Update content and counts
      document.getElementById("problemsInsight").innerHTML = problemsText;
      document.getElementById("questionsInsight").innerHTML = questionsText;
      document.getElementById("trendingInsight").innerHTML = trendingText;
      
      // Update count badges
      document.getElementById("problemsCount").textContent = problemsCount;
      document.getElementById("questionsCount").textContent = questionsCount;
      document.getElementById("trendsCount").textContent = trendsCount;
      
    } catch (error) {
      console.error("Error fetching insights:", error);
      // Show error in insight cards
      document.getElementById("problemsInsight").textContent = "Error loading insights.";
      document.getElementById("questionsInsight").textContent = "Error loading insights.";
      document.getElementById("trendingInsight").textContent = "Error loading insights.";
    }
  }
  
  async function fetchRecentMessages() {
    try {
      const response = await fetch("/api/messages?limit=10");
      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
      
      const data = await response.json();
      const messages = data.messages || [];
      
      const messagesContainer = document.getElementById("recentMessages");
      
      if (messages.length === 0) {
        messagesContainer.innerHTML = '<p class="text-muted">No recent messages available.</p>';
        return;
      }
      
      // Format messages with better display
      const messagesHtml = messages.map(msg => {
        const timestamp = new Date(parseFloat(msg.ts) * 1000).toLocaleTimeString();
        const user = msg.user || "Unknown";
        let text = msg.text || "";
        
        // Clean up user mentions - show as actual usernames
        text = text.replace(/<@([A-Z0-9]+)>/g, (match, userId) => {
          return `<span class="badge bg-primary">@User ${userId.slice(-4)}</span>`;
        });
        
        // Highlight problem keywords
        const problemKeywords = ['problem', 'issue', 'error', 'bug', 'stuck', 'help', 'broken', 'failed', 'trouble'];
        problemKeywords.forEach(keyword => {
          const regex = new RegExp(`\\b(${keyword})\\b`, 'gi');
          text = text.replace(regex, '<span class="text-danger fw-bold">$1</span>');
        });
        
        // Highlight question keywords
        const questionKeywords = ['how', 'what', 'where', 'when', 'why', 'can', 'could', 'would', 'should'];
        questionKeywords.forEach(keyword => {
          const regex = new RegExp(`\\b(${keyword})\\b`, 'gi');
          text = text.replace(regex, '<span class="text-info fw-bold">$1</span>');
        });
        
        // Highlight question marks
        text = text.replace(/\?/g, '<span class="text-info fw-bold">?</span>');
        
        // Capitalize first letter of the text
        if (text && text.length > 0) {
          text = text.charAt(0).toUpperCase() + text.slice(1);
        }
        
        return `
          <div class="border-bottom pb-2 mb-2">
            <small class="text-muted">[${timestamp}] <strong>User ${user.slice(-4)}:</strong></small>
            <p class="mb-1">${text}</p>
          </div>
        `;
      }).join("");
      
      messagesContainer.innerHTML = messagesHtml;
      
    } catch (error) {
      console.error("Error fetching messages:", error);
      document.getElementById("recentMessages").innerHTML = '<p class="text-danger">Error loading messages.</p>';
    }
  }
  
  async function refreshAllData() {
    updateTimestamp();
    
    // Show loading state
    refreshBtn.disabled = true;
    refreshBtn.innerHTML = "🔄 Refreshing...";
    
    try {
      // Fetch all data in parallel
      await Promise.all([
        fetchStats(),
        fetchInsights(),
        fetchRecentMessages()
      ]);
      
      // Success feedback
      refreshBtn.innerHTML = "✅ Refreshed!";
      setTimeout(() => {
        refreshBtn.innerHTML = "🔄 Refresh Data";
        refreshBtn.disabled = false;
      }, 2000);
      
    } catch (error) {
      console.error("Error refreshing data:", error);
      refreshBtn.innerHTML = "❌ Error";
      setTimeout(() => {
        refreshBtn.innerHTML = "🔄 Refresh Data";
        refreshBtn.disabled = false;
      }, 2000);
    }
  }
  
  function startAutoRefresh() {
    // Refresh every 30 seconds
    autoRefreshInterval = setInterval(refreshAllData, 30000);
  }
  
  function stopAutoRefresh() {
    if (autoRefreshInterval) {
      clearInterval(autoRefreshInterval);
    }
  }
  
  // Event listeners
  refreshBtn.addEventListener("click", refreshAllData);
  
  // Start auto-refresh when page loads
  refreshAllData();
  startAutoRefresh();
  
  // Stop auto-refresh when page is hidden (battery saving)
  document.addEventListener("visibilitychange", () => {
    if (document.hidden) {
      stopAutoRefresh();
    } else {
      startAutoRefresh();
      refreshAllData(); // Refresh when page becomes visible again
    }
  });
  
  // Cleanup on page unload
  window.addEventListener("beforeunload", stopAutoRefresh);
});
