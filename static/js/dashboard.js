/**
 * Customer Feedback Dashboard - Interactive Chart.js Initializer
 */

document.addEventListener('DOMContentLoaded', function () {
  // Check if chart payload exists on the page
  const chartDataEl = document.getElementById('chartDataPayload');
  if (!chartDataEl) return;

  let payload;
  try {
    payload = JSON.parse(chartDataEl.textContent);
  } catch (err) {
    console.error('Failed to parse chart payload:', err);
    return;
  }

  // Global Chart.js styling defaults
  Chart.defaults.font.family = "'Plus Jakarta Sans', -apple-system, sans-serif";
  Chart.defaults.color = '#64748B';
  Chart.defaults.plugins.tooltip.padding = 10;
  Chart.defaults.plugins.tooltip.cornerRadius = 8;

  // -------------------------------------------------------------
  // 1. Rating Distribution Chart (Bar)
  // -------------------------------------------------------------
  const ratingCtx = document.getElementById('ratingChart');
  if (ratingCtx && payload.ratings) {
    new Chart(ratingCtx, {
      type: 'bar',
      data: {
        labels: payload.ratings.labels,
        datasets: [{
          label: 'Feedback Count',
          data: payload.ratings.data,
          backgroundColor: [
            '#EF4444', // 1 Star - Rose
            '#F97316', // 2 Stars - Orange
            '#F59E0B', // 3 Stars - Amber
            '#3B82F6', // 4 Stars - Blue
            '#10B981'  // 5 Stars - Emerald
          ],
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: function (context) {
                return ` ${context.parsed.y} ratings`;
              }
            }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: {
              precision: 0,
              stepSize: 1
            },
            grid: {
              color: '#F1F5F9'
            }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  }

  // -------------------------------------------------------------
  // 2. Sentiment Distribution Chart (Doughnut)
  // -------------------------------------------------------------
  const sentimentCtx = document.getElementById('sentimentChart');
  if (sentimentCtx && payload.sentiments) {
    new Chart(sentimentCtx, {
      type: 'doughnut',
      data: {
        labels: payload.sentiments.labels,
        datasets: [{
          data: payload.sentiments.data,
          backgroundColor: [
            '#10B981', // Positive - Emerald
            '#F59E0B', // Neutral - Amber
            '#EF4444'  // Negative - Rose
          ],
          borderWidth: 2,
          borderColor: '#FFFFFF',
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'bottom',
            labels: {
              padding: 16,
              usePointStyle: true,
              pointStyle: 'circle'
            }
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const val = context.parsed;
                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                return ` ${context.label}: ${val} (${pct}%)`;
              }
            }
          }
        },
        cutout: '70%'
      }
    });
  }

  // -------------------------------------------------------------
  // 3. Category-Wise Distribution Chart (Horizontal Bar)
  // -------------------------------------------------------------
  const categoryCtx = document.getElementById('categoryChart');
  if (categoryCtx && payload.categories) {
    new Chart(categoryCtx, {
      type: 'bar',
      data: {
        labels: payload.categories.labels,
        datasets: [{
          label: 'Total Feedback',
          data: payload.categories.data,
          backgroundColor: 'rgba(79, 70, 229, 0.85)',
          borderRadius: 6,
          borderSkipped: false
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0, stepSize: 1 },
            grid: { color: '#F1F5F9' }
          },
          y: {
            grid: { display: false }
          }
        }
      }
    });
  }

  // -------------------------------------------------------------
  // 4. Feedback Trend Chart (Line)
  // -------------------------------------------------------------
  const trendCtx = document.getElementById('trendChart');
  if (trendCtx && payload.trends) {
    new Chart(trendCtx, {
      type: 'line',
      data: {
        labels: payload.trends.labels,
        datasets: [{
          label: 'Feedback Received',
          data: payload.trends.data,
          borderColor: '#4F46E5',
          backgroundColor: 'rgba(79, 70, 229, 0.1)',
          fill: true,
          tension: 0.35,
          pointBackgroundColor: '#4F46E5',
          pointBorderColor: '#FFFFFF',
          pointBorderWidth: 2,
          pointRadius: 4,
          pointHoverRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0, stepSize: 1 },
            grid: { color: '#F1F5F9' }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  }
});
