// Generate dashboard images for the website
function generateDashboardImages() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas dimensions
    canvas.width = 800;
    canvas.height = 500;
    
    // Create dashboard images
    createDashboardImage('appointment_status_chart.png', 'Appointment Status Distribution', 
        [
            {label: 'Completed', value: 74.9, color: '#3498db'},
            {label: 'Cancelled', value: 10.2, color: '#e74c3c'},
            {label: 'Rescheduled', value: 10.1, color: '#f39c12'},
            {label: 'No-show', value: 4.9, color: '#95a5a6'}
        ], 'pie');
    
    createDashboardImage('wait_time_chart.png', 'Average Wait Time by Device Type', 
        [
            {label: 'Tablet', value: 14.17, color: '#3498db'},
            {label: 'Desktop', value: 14.04, color: '#2ecc71'},
            {label: 'Laptop', value: 13.91, color: '#e74c3c'},
            {label: 'Mobile Phone', value: 13.60, color: '#f39c12'}
        ], 'bar');
    
    createDashboardImage('provider_rating_chart.png', 'Provider Ratings by Specialty', 
        [
            {label: 'Cardiology', value: 3.91, color: '#3498db'},
            {label: 'Internal Medicine', value: 3.61, color: '#2ecc71'},
            {label: 'Family Medicine', value: 3.77, color: '#e74c3c'},
            {label: 'Pediatrics', value: 3.52, color: '#f39c12'},
            {label: 'Dermatology', value: 3.48, color: '#9b59b6'}
        ], 'bar');
    
    createDashboardImage('technical_issues_chart.png', 'Technical Issues by Device Type', 
        [
            {label: 'Tablet', value: 17.04, color: '#3498db'},
            {label: 'Mobile Phone', value: 16.90, color: '#2ecc71'},
            {label: 'Desktop', value: 16.54, color: '#e74c3c'},
            {label: 'Laptop', value: 16.33, color: '#f39c12'}
        ], 'bar');
    
    createDashboardImage('appointment_duration_chart.png', 'Average Appointment Duration by Type', 
        [
            {label: 'Follow-up', value: 15.3, color: '#3498db'},
            {label: 'Initial Consultation', value: 28.7, color: '#2ecc71'},
            {label: 'Urgent Care', value: 22.1, color: '#e74c3c'},
            {label: 'Specialist Referral', value: 25.4, color: '#f39c12'}
        ], 'bar');
    
    createDashboardImage('patient_age_chart.png', 'Patient Age Distribution', 
        [
            {label: '0-18', value: 15, color: '#3498db'},
            {label: '19-35', value: 25, color: '#2ecc71'},
            {label: '36-50', value: 30, color: '#e74c3c'},
            {label: '51-65', value: 20, color: '#f39c12'},
            {label: '65+', value: 10, color: '#9b59b6'}
        ], 'pie');
    
    function createDashboardImage(filename, title, data, chartType) {
        // Clear canvas
        ctx.fillStyle = '#ffffff';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
        
        // Add title
        ctx.fillStyle = '#333333';
        ctx.font = 'bold 28px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(title, canvas.width / 2, 50);
        
        // Add border
        ctx.strokeStyle = '#dddddd';
        ctx.lineWidth = 2;
        ctx.strokeRect(10, 10, canvas.width - 20, canvas.height - 20);
        
        // Draw chart based on type
        if (chartType === 'pie') {
            drawPieChart(data);
        } else if (chartType === 'bar') {
            drawBarChart(data);
        }
        
        // Add legend
        drawLegend(data);
        
        // Save the image
        saveCanvasAsImage(filename);
    }
    
    function drawBarChart(data) {
        const barWidth = 80;
        const spacing = 30;
        const startX = (canvas.width - (barWidth * data.length + spacing * (data.length - 1))) / 2;
        const maxBarHeight = 300;
        const baseY = 400;
        
        // Find max value for scaling
        const maxValue = Math.max(...data.map(item => item.value));
        
        // Draw axes
        ctx.strokeStyle = '#333333';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(startX - 20, 100);
        ctx.lineTo(startX - 20, baseY);
        ctx.lineTo(canvas.width - startX + 20, baseY);
        ctx.stroke();
        
        // Draw y-axis labels
        ctx.fillStyle = '#333333';
        ctx.font = '14px Arial';
        ctx.textAlign = 'right';
        
        const yAxisSteps = 5;
        for (let i = 0; i <= yAxisSteps; i++) {
            const value = (maxValue * i / yAxisSteps).toFixed(1);
            const y = baseY - (i / yAxisSteps) * maxBarHeight;
            ctx.fillText(value, startX - 25, y + 5);
            
            // Draw horizontal grid line
            ctx.strokeStyle = '#dddddd';
            ctx.lineWidth = 1;
            ctx.beginPath();
            ctx.moveTo(startX - 20, y);
            ctx.lineTo(canvas.width - startX + 20, y);
            ctx.stroke();
        }
        
        // Draw bars
        for (let i = 0; i < data.length; i++) {
            const barHeight = (data[i].value / maxValue) * maxBarHeight;
            const x = startX + i * (barWidth + spacing);
            const y = baseY - barHeight;
            
            // Draw bar
            ctx.fillStyle = data[i].color;
            ctx.fillRect(x, y, barWidth, barHeight);
            
            // Draw border
            ctx.strokeStyle = '#333333';
            ctx.lineWidth = 1;
            ctx.strokeRect(x, y, barWidth, barHeight);
            
            // Draw value on top of bar
            ctx.fillStyle = '#333333';
            ctx.font = 'bold 14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(data[i].value.toFixed(1), x + barWidth / 2, y - 10);
            
            // Draw label below x-axis
            ctx.fillStyle = '#333333';
            ctx.font = '14px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(data[i].label, x + barWidth / 2, baseY + 20);
        }
    }
    
    function drawPieChart(data) {
        const centerX = canvas.width / 2;
        const centerY = 250;
        const radius = 150;
        
        // Calculate total for percentages
        const total = data.reduce((sum, item) => sum + item.value, 0);
        
        let startAngle = 0;
        
        for (let i = 0; i < data.length; i++) {
            const sliceAngle = (data[i].value / total) * Math.PI * 2;
            
            // Draw slice
            ctx.fillStyle = data[i].color;
            ctx.beginPath();
            ctx.moveTo(centerX, centerY);
            ctx.arc(centerX, centerY, radius, startAngle, startAngle + sliceAngle);
            ctx.closePath();
            ctx.fill();
            
            // Draw border
            ctx.strokeStyle = '#ffffff';
            ctx.lineWidth = 2;
            ctx.stroke();
            
            // Calculate percentage
            const percentage = ((data[i].value / total) * 100).toFixed(1) + '%';
            
            // Draw percentage in the middle of the slice
            const midAngle = startAngle + sliceAngle / 2;
            const labelRadius = radius * 0.7;
            const labelX = centerX + Math.cos(midAngle) * labelRadius;
            const labelY = centerY + Math.sin(midAngle) * labelRadius;
            
            ctx.fillStyle = '#ffffff';
            ctx.font = 'bold 16px Arial';
            ctx.textAlign = 'center';
            ctx.fillText(percentage, labelX, labelY);
            
            startAngle += sliceAngle;
        }
    }
    
    function drawLegend(data) {
        const legendX = 600;
        const legendY = 120;
        const itemHeight = 30;
        
        ctx.fillStyle = '#f8f9fa';
        ctx.fillRect(legendX - 20, legendY - 20, 200, data.length * itemHeight + 30);
        ctx.strokeStyle = '#dddddd';
        ctx.lineWidth = 1;
        ctx.strokeRect(legendX - 20, legendY - 20, 200, data.length * itemHeight + 30);
        
        for (let i = 0; i < data.length; i++) {
            // Draw color box
            ctx.fillStyle = data[i].color;
            ctx.fillRect(legendX, legendY + i * itemHeight, 20, 20);
            ctx.strokeStyle = '#333333';
            ctx.lineWidth = 1;
            ctx.strokeRect(legendX, legendY + i * itemHeight, 20, 20);
            
            // Draw label
            ctx.fillStyle = '#333333';
            ctx.font = '14px Arial';
            ctx.textAlign = 'left';
            ctx.fillText(data[i].label, legendX + 30, legendY + i * itemHeight + 15);
        }
    }
    
    function saveCanvasAsImage(filename) {
        // In a real environment, this would save the canvas as an image file
        // For this simulation, we'll create image elements in the DOM
        
        const img = document.createElement('img');
        img.src = canvas.toDataURL('image/png');
        img.alt = filename.replace('.png', '');
        img.className = 'dashboard-img';
        img.style.display = 'none';
        img.id = filename.replace('.png', '');
        document.body.appendChild(img);
        
        // Replace image sources in the document
        const images = document.querySelectorAll(`img[src="assets/${filename}"]`);
        images.forEach(image => {
            image.src = img.src;
        });
        
        console.log(`Generated image: ${filename}`);
    }
}

// Call the function when the page loads
window.addEventListener('DOMContentLoaded', generateDashboardImages);
