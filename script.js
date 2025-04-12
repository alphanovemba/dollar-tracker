// Fetch the data from GitHub
const githubRepo = "alphanovemba/dollar-tracker"; // Replace with your actual repo (e.g. "yourusername/dollar-tracker-mv")
const filePath = "rates.json";

async function fetchRates() {
    const response = await fetch(`https://api.github.com/repos/${githubRepo}/contents/${filePath}`);
    const data = await response.json();
    
    if (data.message === "Not Found") {
        alert("File not found or issues with repo. Please check.");
        return;
    }

    const downloadUrl = data.download_url;
    const rates = await fetch(downloadUrl).then(res => res.json());
    
    return rates;
}

// Update rate on the page
async function updateRateDisplay() {
    const rates = await fetchRates();
    if (!rates || rates.length === 0) {
        document.querySelector(".rate").textContent = "No data yet";
        return;
    }

    const latestRate = rates[rates.length - 1];
    const previousRate = rates[rates.length - 2] ? rates[rates.length - 2].rate : latestRate.rate;

    document.querySelector(".rate").textContent = `MVR ${latestRate.rate}`;
    
    // Set the rate change indicator
    const indicator = document.querySelector(".rate-change-indicator");
    if (latestRate.rate > previousRate) {
        indicator.textContent = "🔺 Rate is up from yesterday!";
        indicator.style.color = "#00FF00";
    } else if (latestRate.rate < previousRate) {
        indicator.textContent = "🔻 Rate is down from yesterday!";
        indicator.style.color = "#FF4500";
    } else {
        indicator.textContent = "Rate is the same as yesterday.";
        indicator.style.color = "#FFD700";
    }
    
    updateChart(rates);
}

// Update chart
let rateChart = null;

function updateChart(rates) {
    const dates = rates.map(r => r.date);
    const values = rates.map(r => r.rate);

    if (rateChart) {
        rateChart.destroy(); // Destroy old chart if it exists
    }

    const ctx = document.getElementById("rateChart").getContext("2d");
    rateChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: dates,
            datasets: [{
                label: 'USD Rate (Black Market)',
                data: values,
                borderColor: '#FF4500',
                backgroundColor: 'rgba(255, 69, 0, 0.2)',
                borderWidth: 2,
                fill: true,
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        precision: 2
                    }
                }
            }
        });
}

// Initialize
updateRateDisplay();
