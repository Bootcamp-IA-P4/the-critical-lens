// Wait for the DOM to be fully loaded before running
document.addEventListener('DOMContentLoaded', function() {
  // Check if chart data is available
  if (!window.chartData) {
      console.error('Chart data not available');
      return;
  }

  // Create verification categories pie chart
  const verificationChart = document.getElementById('verification-chart');
  if (verificationChart) {
      new Chart(verificationChart, {
          type: 'pie',
          data: {
              labels: window.chartData.verification.labels,
              datasets: [{
                  data: window.chartData.verification.percentages,
                  backgroundColor: window.chartData.verification.colors || 
                      ['#ff6b6b', '#feca57', '#54a0ff', '#1dd1a1'],
                  borderWidth: 1
              }]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              plugins: {
                  legend: {
                      position: 'right',
                  },
                  tooltip: {
                      callbacks: {
                          label: function(context) {
                              const label = context.label || '';
                              const value = context.parsed || 0;
                              const count = window.chartData.verification.counts[context.dataIndex];
                              return `${label}: ${value}% (${count} artículos)`;
                          }
                      }
                  }
              }
          }
      });
  }

  // Create source bar chart
  const sourceChart = document.getElementById('source-chart');
  if (sourceChart) {
      new Chart(sourceChart, {
          type: 'bar',
          data: {
              labels: window.chartData.source.labels,
              datasets: [{
                  label: 'Artículos por fuente',
                  data: window.chartData.source.counts,
                  backgroundColor: '#54a0ff',
                  borderWidth: 1
              }]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              indexAxis: 'y',  // Horizontal bar chart
              plugins: {
                  tooltip: {
                      callbacks: {
                          label: function(context) {
                              const value = context.raw || 0;
                              const percentage = window.chartData.source.percentages[context.dataIndex];
                              return `${value} artículos (${percentage}%)`;
                          }
                      }
                  }
              }
          }
      });
  }

  // Create tags bar chart
  const tagsChart = document.getElementById('tags-chart');
  if (tagsChart) {
      new Chart(tagsChart, {
          type: 'bar',
          data: {
              labels: window.chartData.tags.labels,
              datasets: [{
                  label: 'Artículos por temática',
                  data: window.chartData.tags.counts,
                  backgroundColor: '#1dd1a1',
                  borderWidth: 1
              }]
          },
          options: {
              responsive: true,
              maintainAspectRatio: false,
              indexAxis: 'y',  // Horizontal bar chart
              plugins: {
                  tooltip: {
                      callbacks: {
                          label: function(context) {
                              const value = context.raw || 0;
                              const percentage = window.chartData.tags.percentages[context.dataIndex];
                              return `${value} artículos (${percentage}%)`;
                          }
                      }
                  }
              }
          }
      });
  }
});