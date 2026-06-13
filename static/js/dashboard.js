/**
 * Dashboard chart controller.
 *
 * Fetches data from the /api/chart-data endpoint and renders
 * Chart.js line chart for weekly/monthly trends.
 */

(function () {
    'use strict';

    var trendCanvas = document.getElementById('trend-chart');
    if (!trendCanvas) return; // Not on dashboard page

    var trendChart = null;

    /**
     * Fetch chart data from API and render the trend line chart.
     * @param {number} days - Number of days to display
     */
    function loadTrendChart(days) {
        fetch('/api/chart-data?days=' + days, {
            credentials: 'same-origin',
            headers: {
                'Accept': 'application/json'
            }
        })
        .then(function (response) {
            if (!response.ok) throw new Error('Failed to fetch chart data');
            return response.json();
        })
        .then(function (data) {
            renderTrendChart(data, days);
        })
        .catch(function (err) {
            console.error('Chart data error:', err);
        });
    }

    /**
     * Render or update the trend line chart.
     * @param {Object} data - API response with labels and datasets
     * @param {number} days - Number of days displayed
     */
    function renderTrendChart(data, days) {
        if (trendChart) {
            trendChart.destroy();
        }

        var ctx = trendCanvas.getContext('2d');

        // Create gradient fill
        var gradient = ctx.createLinearGradient(0, 0, 0, 300);
        gradient.addColorStop(0, 'hsla(145, 80%, 42%, 0.3)');
        gradient.addColorStop(1, 'hsla(145, 80%, 42%, 0.02)');

        trendChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: data.labels,
                datasets: [
                    {
                        label: 'Your CO₂e (kg)',
                        data: data.datasets.total,
                        borderColor: 'hsl(145, 80%, 45%)',
                        backgroundColor: gradient,
                        fill: true,
                        tension: 0.4,
                        borderWidth: 2.5,
                        pointBackgroundColor: 'hsl(145, 80%, 45%)',
                        pointBorderColor: 'hsl(145, 80%, 55%)',
                        pointRadius: 4,
                        pointHoverRadius: 7,
                        spanGaps: true
                    },
                    {
                        label: 'India Avg',
                        data: data.labels.map(function () { return data.india_average; }),
                        borderColor: 'hsla(0, 0%, 60%, 0.5)',
                        borderDash: [8, 4],
                        borderWidth: 1.5,
                        pointRadius: 0,
                        fill: false
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index'
                },
                scales: {
                    x: {
                        grid: {
                            color: 'hsla(0, 0%, 100%, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: 'hsl(0, 0%, 55%)',
                            font: { family: 'Inter', size: 11 },
                            maxRotation: 45
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'hsla(0, 0%, 100%, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            color: 'hsl(0, 0%, 55%)',
                            font: { family: 'Inter', size: 11 },
                            callback: function (value) {
                                return value + ' kg';
                            }
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        align: 'end',
                        labels: {
                            color: 'hsl(0, 0%, 75%)',
                            font: { family: 'Inter', size: 12 },
                            padding: 16,
                            usePointStyle: true,
                            pointStyleWidth: 10
                        }
                    },
                    tooltip: {
                        backgroundColor: 'hsla(160, 20%, 10%, 0.95)',
                        titleFont: { family: 'Inter', size: 13 },
                        bodyFont: { family: 'Inter', size: 12 },
                        borderColor: 'hsla(145, 80%, 42%, 0.3)',
                        borderWidth: 1,
                        cornerRadius: 8,
                        padding: 12,
                        callbacks: {
                            label: function (context) {
                                return context.dataset.label + ': ' + (context.parsed.y !== null ? context.parsed.y.toFixed(2) : '—') + ' kg CO₂e';
                            }
                        }
                    }
                }
            }
        });
    }

    // Chart time range buttons
    var chartBtns = document.querySelectorAll('.chart-btn');
    chartBtns.forEach(function (btn) {
        btn.addEventListener('click', function () {
            chartBtns.forEach(function (b) {
                b.classList.remove('active');
                b.setAttribute('aria-pressed', 'false');
            });
            this.classList.add('active');
            this.setAttribute('aria-pressed', 'true');
            var days = parseInt(this.getAttribute('data-days')) || 7;
            loadTrendChart(days);
        });
    });

    // Initial load
    loadTrendChart(7);
})();
