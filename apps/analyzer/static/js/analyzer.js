// Archivo: apps/analyzer/static/js/analyzer.js
document.addEventListener('DOMContentLoaded', function() {
  // Obtener el formulario
  const form = document.querySelector('form[action*="analyzer"]');
  
  if (form) {
      // Capturar el evento de envío del formulario
      form.addEventListener('submit', function() {
          // Guardar la posición actual de scroll en localStorage
          localStorage.setItem('scrollPosition', window.pageYOffset);
          localStorage.setItem('scrollToResults', 'true');
      });
  }
  
  // Verificar si venimos de un envío de formulario
  const resultsSection = document.getElementById('results-section');
  const shouldRestore = localStorage.getItem('scrollPosition');
  const shouldScrollToResults = localStorage.getItem('scrollToResults');
  
  if (shouldRestore) {
      // Primero restaurar la posición original
      window.scrollTo(0, parseInt(shouldRestore));
      
      // Luego, si hay resultados y debemos hacer scroll, hacerlo después de un breve retraso
      if (resultsSection && shouldScrollToResults) {
          setTimeout(function() {
              resultsSection.scrollIntoView({
                  behavior: 'smooth',
                  block: 'start'
              });
          }, 300); // Retraso para asegurar que la página está lista
      }
      
      // Limpiar localStorage para no afectar futuras navegaciones
      localStorage.removeItem('scrollPosition');
      localStorage.removeItem('scrollToResults');
  }
});