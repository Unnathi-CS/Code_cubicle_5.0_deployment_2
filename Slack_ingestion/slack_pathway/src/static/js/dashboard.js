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
      
      // Update insight cards
      document.getElementById("problemsInsight").textContent = insights.problems || "No problems detected recently.";
      document.getElementById("questionsInsight").textContent = insights.questions || "No questions found recently.";
      document.getElementById("trendingInsight").textContent = insights.trending || "No trending topics identified.";
      
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
      
      // Format messages
      const messagesHtml = messages.map(msg => {
        const timestamp = new Date(parseFloat(msg.ts) * 1000).toLocaleTimeString();
        const user = msg.user || "Unknown";
        const text = msg.text || "";
        
        return `
          <div class="border-bottom pb-2 mb-2">
            <small class="text-muted">[${timestamp}] <strong>${user}:</strong></small>
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
