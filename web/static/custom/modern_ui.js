/**
 * Modern UI Helpers for ReconPoint
 */

window.ReconpointUI = {
  /**
   * Opens the slide-over asset panel
   * @param {string} title - Panel title
   * @param {string} url - URL to fetch content from (optional)
   * @param {string} staticContent - HTML content (optional)
   */
  openAssetPanel: function(title, url, staticContent) {
    const loader = document.getElementById('asset-panel-loader');
    const container = document.getElementById('asset-panel-content');
    
    // Clear previous content and show loader
    if (container) container.innerHTML = '';
    if (loader) loader.classList.remove('hidden');
    
    // Dispatch event to Alpine to open the panel
    window.dispatchEvent(new CustomEvent('open-asset-panel', { 
      detail: { 
        title: title, 
        content: staticContent || '' 
      } 
    }));
    
    if (url) {
      // Use HTMX to fetch and swap content into the panel
      htmx.ajax('GET', url, {
        target: '#asset-panel-content',
        swap: 'innerHTML'
      }).then(() => {
        if (loader) loader.classList.add('hidden');
        // Re-init icons
        if (window.lucide) lucide.createIcons();
      });
    } else if (staticContent) {
      if (loader) loader.classList.add('hidden');
    }
  },
  
  closeAssetPanel: function() {
    window.dispatchEvent(new CustomEvent('close-asset-panel'));
  }
};
