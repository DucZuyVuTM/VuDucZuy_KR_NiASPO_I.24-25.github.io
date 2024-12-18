async function fetchData() {
    const response = await fetch('/data');
    const data = await response.json();
    document.getElementById('data').innerText = JSON.stringify(data, null, 2);
}

let chart1, chart2, chart3;  // Khai báo biến chart ngoài hàm

async function performGraph() {
    const response = await fetch('/graph', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
    const result = await response.json();

    const x_values = result.x_values;
    console.log('x_values:', x_values);

    const y1_values = result.y1_values;
    console.log('y1_values:', y1_values);

    const y2_values = result.y2_values;
    console.log('y2_values:', y2_values);

    const y3_values = result.y3_values;
    console.log('y3_values:', y3_values);

    // Hàm tạo biểu đồ
    function createChart(chartId, observedData, observedLabel, color) {
        const ctx = document.getElementById(chartId).getContext('2d');
        return new Chart(ctx, {
            type: 'scatter',
            data: {
                datasets: [
                    {
                        label: observedLabel,
                        data: x_values.map((x, i) => ({ x: x, y: observedData[i] })),
                        backgroundColor: color,
                    },
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: observedLabel
                    }
                },
                scales: {
                    x: {
                        type: 'linear',
                        position: 'bottom'
                    }
                }
            }
        });
    }

    // Tạo 3 biểu đồ riêng biệt
    if (chart1) chart1.destroy();
    if (chart2) chart2.destroy();
    if (chart3) chart3.destroy();

    chart1 = createChart('chartConfirmed', y1_values, 'Observed Data (Confirmed)', 'red');
    chart2 = createChart('chartRecovered', y2_values, 'Observed Data (Recovered)', 'blue');
    chart3 = createChart('chartDeaths', y3_values, 'Observed Data (Deaths)', 'green');

    // Hiển thị hoặc ẩn biểu đồ
    const chartContainer = document.getElementById('chartContainer');
    if (chartContainer.style.display === 'none') {
        chartContainer.style.display = 'block'; // Hiện biểu đồ
    } else {
        chartContainer.style.display = 'none'; // Ẩn biểu đồ
    }
}

async function sendData() {
    const response = await fetch('/send');
    const result = await response.json();
    alert(result.status);
}