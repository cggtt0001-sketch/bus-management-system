/**
 * Chart.js initialization functions for the dashboard
 */

/**
 * Initialize a pie chart
 * @param {Object} data - Object with labels and data arrays
 * @param {string} canvasId - ID of the canvas element
 */
function initPieChart(data, canvasId) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    new Chart(ctx, {
        type: 'pie',
        data: {
            labels: data.labels,
            datasets: [{
                data: data.data,
                backgroundColor: [
                    '#007bff', // Blue
                    '#28a745', // Green
                    '#fd7e14', // Orange
                    '#6f42c1'  // Purple
                ],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 15,
                        font: {
                            size: 12
                        }
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const label = context.label || '';
                            const value = context.parsed || 0;
                            return label + ': ' + value + ' schedule(s)';
                        }
                    }
                }
            }
        }
    });
}

/**
 * Initialize a bar chart
 * @param {Object} data - Object with labels and data arrays
 * @param {string} canvasId - ID of the canvas element
 */
function initBarChart(data, canvasId) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: data.labels,
            datasets: [{
                label: 'Number of Schedules',
                data: data.data,
                backgroundColor: '#20c997',
                borderColor: '#17a2b8',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        font: {
                            size: 11
                        }
                    },
                    title: {
                        display: true,
                        text: 'Number of Schedules',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                },
                x: {
                    ticks: {
                        font: {
                            size: 11
                        }
                    },
                    title: {
                        display: true,
                        text: 'Routes',
                        font: {
                            size: 12,
                            weight: 'bold'
                        }
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const value = context.parsed.y || 0;
                            return value + ' schedule(s)';
                        }
                    }
                }
            }
        }
    });
}
