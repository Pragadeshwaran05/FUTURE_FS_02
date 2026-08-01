document.addEventListener("DOMContentLoaded", function () {

    // ===== Sample Data =====
    const statusData = [10, 8, 5, 3];

    const sourceLabels = [
        "Website",
        "Facebook",
        "Instagram",
        "LinkedIn",
        "Referral"
    ];

    const sourceData = [8, 6, 4, 3, 2];

    // ==========================
    // BAR CHART
    // ==========================

    const statusCanvas = document.getElementById("statusChart");

    if (statusCanvas) {

        new Chart(statusCanvas, {

            type: "bar",

            data: {

                labels: [
                    "New",
                    "Contacted",
                    "Follow-up",
                    "Converted"
                ],

                datasets: [{
                    label: "Leads",
                    data: statusData,
                    backgroundColor: [
                        "#3B82F6",
                        "#F59E0B",
                        "#8B5CF6",
                        "#10B981"
                    ],
                    borderRadius: 10,
                    borderSkipped: false
                }]

            },

            options: {

                responsive: true,
                maintainAspectRatio: false,

                plugins: {

                    legend: {
                        display: false
                    }

                },

                scales: {

                    x: {

                        grid: {
                            display: false
                        }

                    },

                    y: {

                        beginAtZero: true,

                        ticks: {
                            stepSize: 1
                        }

                    }

                }

            }

        });

    }

    // ==========================
    // PIE CHART
    // ==========================

    const sourceCanvas = document.getElementById("sourceChart");

    if (sourceCanvas) {

        new Chart(sourceCanvas, {

            type: "pie",

            data: {

                labels: sourceLabels,

                datasets: [{

                    data: sourceData,

                    backgroundColor: [
                        "#3B82F6",
                        "#10B981",
                        "#F59E0B",
                        "#8B5CF6",
                        "#EF4444"
                    ],

                    borderWidth: 2

                }]

            },

            options: {

                responsive: true,

                maintainAspectRatio: false,

                plugins: {

                    legend: {

                        position: "bottom"

                    }

                }

            }

        });

    }

});