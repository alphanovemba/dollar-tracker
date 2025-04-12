fetch('rates.json')
  .then(res => res.json())
  .then(data => {
    const today = data[data.length - 1];
    const yesterday = data[data.length - 2];

    document.getElementById('rate').textContent = `$${today.rate.toFixed(2)}`;
    document.getElementById('last-updated').textContent = `Last updated: ${today.date}`;

    const indicator = document.getElementById('indicator');
    if (today.rate > yesterday.rate) {
      indicator.textContent = '▲';
      indicator.style.color = 'lime';
    } else if (today.rate < yesterday.rate) {
      indicator.textContent = '▼';
      indicator.style.color = 'red';
    } else {
      indicator.textContent = '—';
      indicator.style.color = 'gray';
    }

    const ctx = document.getElementById('rateChart').getContext('2d');
    new Chart(ctx, {
      type: 'line',
      data: {
        labels: data.map(d => d.date),
        datasets: [{
          label: 'USD Rate',
          data: data.map(d => d.rate),
          borderColor: '#4ade80',
          backgroundColor: 'rgba(74, 222, 128, 0.1)',
          tension: 0.2,
          fill: true
        }]
      },
      options: {
        plugins: {
          legend: { display: false }
        },
        scales: {
          x: { ticks: { color: '#ccc' } },
          y: { ticks: { color: '#ccc' } }
        }
      }
    });
  });


// rates.json
[
  { "date": "2025-04-10", "rate": 17.0 },
  { "date": "2025-04-11", "rate": 17.1 },
  { "date": "2025-04-12", "rate": 17.3 }
]
