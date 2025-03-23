document.addEventListener('DOMContentLoaded', function() {
  // Get the form
  const form = document.querySelector('form[action*="analyzer"]');
  
  if (form) {
      // Capture the form submission event
      form.addEventListener('submit', function() {
          // Save the current scroll position in localStorage
          localStorage.setItem('scrollPosition', window.pageYOffset);
          localStorage.setItem('scrollToResults', 'true');
      });
  }
  
  // Check if we're coming from a form submission
  const resultsSection = document.getElementById('results-section');
  const shouldRestore = localStorage.getItem('scrollPosition');
  const shouldScrollToResults = localStorage.getItem('scrollToResults');
  
  if (shouldRestore) {
      // First restore the original position
      window.scrollTo(0, parseInt(shouldRestore));
      
      // Then, if there are results and we should scroll, do it after a brief delay
      if (resultsSection && shouldScrollToResults) {
          setTimeout(function() {
              resultsSection.scrollIntoView({
                  behavior: 'smooth',
                  block: 'start'
              });
          }, 300); // Delay to ensure the page is ready
      }
      
      // Clear localStorage to not affect future navigation
      localStorage.removeItem('scrollPosition');
      localStorage.removeItem('scrollToResults');
  }
});