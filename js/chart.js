document.addEventListener('DOMContentLoaded', function () {
    // Mengambil data dari endpoint Flask
    fetch('/grafik_data_tamu')
        .then(response => response.json())
        .then(data => {
            // Mendapatkan konteks canvas
            var ctx = document.getElementById('myChart').getContext('2d');

            // Membuat grafik menggunakan data dari Flask
            var myChart = new Chart(ctx, {
                type: 'bar',
                data: {
                    labels: data.labels,
                    datasets: [{
                        label: 'Grafik Jenis Kelamin Tamu',
                        data: data.values,
                        backgroundColor: [
                            'rgba(255, 99, 132, 0.2)',
                            'rgba(54, 162, 235, 0.2)',
                        ],
                        borderColor: [
                            'rgba(255, 99, 132, 1)',
                            'rgba(54, 162, 235, 1)',
                        ],
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: {
                            beginAtZero: true
                        }
                    }
                }
            });
        });
});
