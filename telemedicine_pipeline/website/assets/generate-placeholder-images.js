// Generate placeholder images for the portfolio
function generatePlaceholderImages() {
    // List of image IDs and their descriptions
    const images = [
        { id: 'overview', title: 'Project Overview', description: 'Telemedicine Appointment Data Pipeline Overview' },
        { id: 'appointment_status_chart', title: 'Appointment Status Distribution', description: 'Breakdown of appointments by status' },
        { id: 'wait_time_chart', title: 'Average Wait Time by Device Type', description: 'Comparison of wait times across devices' },
        { id: 'provider_rating_chart', title: 'Provider Ratings by Specialty', description: 'Average ratings across medical specialties' },
        { id: 'technical_issues_chart', title: 'Technical Issues by Device Type', description: 'Percentage of technical issues by device' },
        { id: 'architecture_diagram', title: 'Pipeline Architecture', description: 'System architecture diagram' }
    ];
    
    // Generate each image
    images.forEach(image => {
        createPlaceholderImage(image.id, image.title, image.description);
    });
    
    // Create a professional architecture diagram
    createArchitectureDiagram();
}

// Create a placeholder image with canvas
function createPlaceholderImage(id, title, description) {
    const canvas = document.createElement('canvas');
    canvas.width = 800;
    canvas.height = 500;
    const ctx = canvas.getContext('2d');
    
    // Background gradient
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#3498db');
    gradient.addColorStop(1, '#2c3e50');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Add title
    ctx.font = 'bold 32px Arial';
    ctx.fillStyle = 'white';
    ctx.textAlign = 'center';
    ctx.fillText(title, canvas.width/2, 100);
    
    // Add description
    ctx.font = '20px Arial';
    ctx.fillText(description, canvas.width/2, 150);
    
    // Add placeholder chart or image based on the ID
    if (id.includes('chart')) {
        drawPlaceholderChart(ctx, id, canvas.width, canvas.height);
    } else {
        drawPlaceholderGraphic(ctx, id, canvas.width, canvas.height);
    }
    
    // Add watermark
    ctx.font = '16px Arial';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.5)';
    ctx.textAlign = 'right';
    ctx.fillText('BorellyDataWorks.com', canvas.width - 20, canvas.height - 20);
    
    // Save the image
    const img = document.createElement('img');
    img.src = canvas.toDataURL('image/png');
    img.alt = title;
    img.id = id + '_img';
    img.className = 'img-fluid rounded shadow';
    document.body.appendChild(img);
    
    // Replace image sources in the document
    const images = document.querySelectorAll(`img[src*="${id}.png"]`);
    images.forEach(image => {
        image.src = img.src;
    });
}

// Draw a placeholder chart based on the chart type
function drawPlaceholderChart(ctx, id, width, height) {
    ctx.save();
    
    // Common chart elements
    const chartTop = 200;
    const chartBottom = height - 100;
    const chartLeft = 150;
    const chartRight = width - 150;
    const chartWidth = chartRight - chartLeft;
    const chartHeight = chartBottom - chartTop;
    
    // Draw chart background
    ctx.fillStyle = 'rgba(255, 255, 255, 0.1)';
    ctx.fillRect(chartLeft, chartTop, chartWidth, chartHeight);
    
    // Draw axes
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(chartLeft, chartTop);
    ctx.lineTo(chartLeft, chartBottom);
    ctx.lineTo(chartRight, chartBottom);
    ctx.stroke();
    
    // Different chart types based on ID
    if (id.includes('appointment_status')) {
        // Pie chart for appointment status
        drawPieChart(ctx, width/2, height/2 - 30, 120);
    } else if (id.includes('wait_time')) {
        // Bar chart for wait times
        drawBarChart(ctx, chartLeft, chartTop, chartWidth, chartHeight, 4);
    } else if (id.includes('provider_rating')) {
        // Line chart for provider ratings
        drawLineChart(ctx, chartLeft, chartTop, chartWidth, chartHeight, 5);
    } else if (id.includes('technical_issues')) {
        // Horizontal bar chart for technical issues
        drawHorizontalBarChart(ctx, chartLeft, chartTop, chartWidth, chartHeight, 3);
    }
    
    ctx.restore();
}

// Draw a pie chart
function drawPieChart(ctx, centerX, centerY, radius) {
    const colors = ['#e74c3c', '#3498db', '#2ecc71', '#f1c40f'];
    const slices = [0.45, 0.25, 0.15, 0.15]; // Percentages
    
    let startAngle = 0;
    
    // Draw slices
    slices.forEach((slice, i) => {
        const endAngle = startAngle + (slice * Math.PI * 2);
        
        ctx.fillStyle = colors[i];
        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.arc(centerX, centerY, radius, startAngle, endAngle);
        ctx.closePath();
        ctx.fill();
        
        // Draw labels
        const midAngle = startAngle + (endAngle - startAngle) / 2;
        const labelRadius = radius * 1.3;
        const labelX = centerX + Math.cos(midAngle) * labelRadius;
        const labelY = centerY + Math.sin(midAngle) * labelRadius;
        
        ctx.fillStyle = 'white';
        ctx.font = '16px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${Math.round(slice * 100)}%`, labelX, labelY);
        
        startAngle = endAngle;
    });
    
    // Draw legend
    const labels = ['Completed', 'Cancelled', 'Rescheduled', 'No-show'];
    const legendTop = centerY + radius + 30;
    
    labels.forEach((label, i) => {
        const legendX = centerX - 150 + (i * 100);
        
        // Color box
        ctx.fillStyle = colors[i];
        ctx.fillRect(legendX, legendTop, 15, 15);
        
        // Label text
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(label, legendX + 20, legendTop + 12);
    });
}

// Draw a bar chart
function drawBarChart(ctx, left, top, width, height, bars) {
    const barWidth = width / (bars * 2);
    const colors = ['#3498db', '#2ecc71', '#e74c3c', '#f1c40f'];
    
    // Draw bars
    for (let i = 0; i < bars; i++) {
        const barHeight = Math.random() * height * 0.6 + height * 0.2;
        const barX = left + (i * barWidth * 2) + barWidth/2;
        const barY = top + height - barHeight;
        
        ctx.fillStyle = colors[i % colors.length];
        ctx.fillRect(barX, barY, barWidth, barHeight);
        
        // Draw value on top of bar
        ctx.fillStyle = 'white';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${Math.round(barHeight / height * 20)}m`, barX + barWidth/2, barY - 10);
        
        // Draw x-axis label
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        const labels = ['Mobile', 'Desktop', 'Tablet', 'Other'];
        ctx.fillText(labels[i], barX + barWidth/2, top + height + 20);
    }
    
    // Draw y-axis labels
    ctx.fillStyle = 'white';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    for (let i = 0; i <= 5; i++) {
        const labelY = top + height - (i * height / 5);
        ctx.fillText(`${i * 5}m`, left - 10, labelY + 5);
    }
}

// Draw a line chart
function drawLineChart(ctx, left, top, width, height, points) {
    const pointWidth = width / (points - 1);
    
    // Generate random data points
    const data = [];
    for (let i = 0; i < points; i++) {
        data.push(Math.random() * height * 0.6 + height * 0.2);
    }
    
    // Draw line
    ctx.strokeStyle = '#3498db';
    ctx.lineWidth = 3;
    ctx.beginPath();
    for (let i = 0; i < points; i++) {
        const x = left + (i * pointWidth);
        const y = top + height - data[i];
        if (i === 0) {
            ctx.moveTo(x, y);
        } else {
            ctx.lineTo(x, y);
        }
    }
    ctx.stroke();
    
    // Draw points
    for (let i = 0; i < points; i++) {
        const x = left + (i * pointWidth);
        const y = top + height - data[i];
        
        ctx.fillStyle = 'white';
        ctx.beginPath();
        ctx.arc(x, y, 5, 0, Math.PI * 2);
        ctx.fill();
        
        // Draw value above point
        ctx.fillStyle = 'white';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(`${(data[i] / height * 5).toFixed(1)}`, x, y - 15);
        
        // Draw x-axis label
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.textAlign = 'center';
        const labels = ['Cardio', 'Neuro', 'Ortho', 'Pedia', 'General'];
        ctx.fillText(labels[i], x, top + height + 20);
    }
    
    // Draw y-axis labels
    ctx.fillStyle = 'white';
    ctx.font = '12px Arial';
    ctx.textAlign = 'right';
    for (let i = 0; i <= 5; i++) {
        const labelY = top + height - (i * height / 5);
        ctx.fillText(`${i}`, left - 10, labelY + 5);
    }
}

// Draw a horizontal bar chart
function drawHorizontalBarChart(ctx, left, top, width, height, bars) {
    const barHeight = height / (bars * 2);
    const colors = ['#e74c3c', '#3498db', '#2ecc71'];
    
    // Draw bars
    for (let i = 0; i < bars; i++) {
        const barWidth = Math.random() * width * 0.6 + width * 0.1;
        const barX = left;
        const barY = top + (i * barHeight * 2) + barHeight/2;
        
        ctx.fillStyle = colors[i % colors.length];
        ctx.fillRect(barX, barY, barWidth, barHeight);
        
        // Draw value at end of bar
        ctx.fillStyle = 'white';
        ctx.font = '14px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(`${Math.round(barWidth / width * 30)}%`, barX + barWidth + 10, barY + barHeight/2 + 5);
        
        // Draw y-axis label
        ctx.fillStyle = 'white';
        ctx.font = '12px Arial';
        ctx.textAlign = 'right';
        const labels = ['Tablet', 'Mobile', 'Desktop'];
        ctx.fillText(labels[i], left - 10, barY + barHeight/2 + 5);
    }
    
    // Draw x-axis labels
    ctx.fillStyle = 'white';
    ctx.font = '12px Arial';
    ctx.textAlign = 'center';
    for (let i = 0; i <= 5; i++) {
        const labelX = left + (i * width / 5);
        ctx.fillText(`${i * 6}%`, labelX, top + height + 20);
    }
}

// Draw a placeholder graphic for non-chart images
function drawPlaceholderGraphic(ctx, id, width, height) {
    if (id === 'overview') {
        // Draw overview graphic with icons
        drawOverviewGraphic(ctx, width, height);
    } else {
        // Generic placeholder with icon
        drawGenericPlaceholder(ctx, id, width, height);
    }
}

// Draw overview graphic
function drawOverviewGraphic(ctx, width, height) {
    // Draw a flow diagram
    const centerY = height/2 + 30;
    const boxWidth = 120;
    const boxHeight = 60;
    const spacing = 50;
    
    // Draw boxes and arrows
    const boxes = [
        { x: width/2 - boxWidth*2 - spacing*1.5, label: 'Data Sources' },
        { x: width/2 - boxWidth - spacing/2, label: 'Ingestion' },
        { x: width/2, label: 'Processing' },
        { x: width/2 + boxWidth + spacing/2, label: 'Storage' },
        { x: width/2 + boxWidth*2 + spacing*1.5, label: 'Analytics' }
    ];
    
    // Draw arrows
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 2;
    for (let i = 0; i < boxes.length - 1; i++) {
        const startX = boxes[i].x + boxWidth/2;
        const endX = boxes[i+1].x - boxWidth/2;
        
        ctx.beginPath();
        ctx.moveTo(startX, centerY);
        ctx.lineTo(endX, centerY);
        
        // Arrow head
        ctx.lineTo(endX - 10, centerY - 5);
        ctx.moveTo(endX, centerY);
        ctx.lineTo(endX - 10, centerY + 5);
        
        ctx.stroke();
    }
    
    // Draw boxes
    boxes.forEach(box => {
        // Box
        ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
        ctx.fillRect(box.x - boxWidth/2, centerY - boxHeight/2, boxWidth, boxHeight);
        
        // Border
        ctx.strokeStyle = 'white';
        ctx.lineWidth = 2;
        ctx.strokeRect(box.x - boxWidth/2, centerY - boxHeight/2, boxWidth, boxHeight);
        
        // Label
        ctx.fillStyle = 'white';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(box.label, box.x, centerY + 5);
    });
}

// Draw generic placeholder
function drawGenericPlaceholder(ctx, id, width, height) {
    // Draw icon
    ctx.fillStyle = 'rgba(255, 255, 255, 0.2)';
    ctx.beginPath();
    ctx.arc(width/2, height/2, 100, 0, Math.PI * 2);
    ctx.fill();
    
    // Draw icon based on ID
    ctx.fillStyle = 'white';
    ctx.font = '80px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    
    let icon = '📊';
    if (id.includes('architecture')) {
        icon = '🏗️';
    }
    
    ctx.fillText(icon, width/2, height/2);
}

// Create a professional architecture diagram
function createArchitectureDiagram() {
    const canvas = document.createElement('canvas');
    canvas.width = 1000;
    canvas.height = 600;
    const ctx = canvas.getContext('2d');
    
    // Background
    const gradient = ctx.createLinearGradient(0, 0, 0, canvas.height);
    gradient.addColorStop(0, '#2c3e50');
    gradient.addColorStop(1, '#1a2530');
    ctx.fillStyle = gradient;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Title
    ctx.fillStyle = 'white';
    ctx.font = 'bold 28px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('Telemedicine Appointment Data Pipeline - Architecture', canvas.width/2, 40);
    
    // Draw layers
    drawArchitectureLayer(ctx, 'Data Sources', 80, '#8dd3c7');
    drawArchitectureLayer(ctx, 'Ingestion Layer', 200, '#ffffb3');
    drawArchitectureLayer(ctx, 'Processing Layer', 320, '#bebada');
    drawArchitectureLayer(ctx, 'Storage Layer', 440, '#fb8072');
    drawArchitectureLayer(ctx, 'Analytics Layer', 560, '#80b1d3');
    
    // Draw components
    // Data Sources
    drawArchitectureComponent(ctx, 'Appointment Logs (External API)', 150, 110, '#8dd3c7');
    drawArchitectureComponent(ctx, 'Patient Feedback (S3 JSON Files)', 500, 110, '#8dd3c7');
    drawArchitectureComponent(ctx, 'Provider Data (RDS)', 850, 110, '#8dd3c7');
    
    // Ingestion Layer
    drawArchitectureComponent(ctx, 'Kafka / Kinesis', 150, 230, '#ffffb3');
    drawArchitectureComponent(ctx, 'Airflow', 500, 230, '#ffffb3');
    drawArchitectureComponent(ctx, 'API Gateway', 850, 230, '#ffffb3');
    
    // Processing Layer
    drawArchitectureComponent(ctx, 'ETL Scripts', 150, 350, '#bebada');
    drawArchitectureComponent(ctx, 'Data Quality Checks', 500, 350, '#bebada');
    drawArchitectureComponent(ctx, 'Dimensional Modeling', 850, 350, '#bebada');
    
    // Storage Layer
    drawArchitectureComponent(ctx, 'S3 Raw Data', 150, 470, '#fb8072');
    drawArchitectureComponent(ctx, 'S3 Processed Data', 500, 470, '#fb8072');
    drawArchitectureComponent(ctx, 'Redshift', 850, 470, '#fb8072');
    
    // Analytics Layer
    drawArchitectureComponent(ctx, 'QuickSight Dashboards', 500, 590, '#80b1d3');
    
    // Draw arrows
    drawArchitectureArrow(ctx, 150, 140, 150, 200);  // Appointment Logs to Kafka
    drawArchitectureArrow(ctx, 500, 140, 500, 200);  // Patient Feedback to Airflow
    drawArchitectureArrow(ctx, 850, 140, 850, 200);  // Provider Data to API Gateway
    
    drawArchitectureArrow(ctx, 150, 260, 150, 320);  // Kafka to ETL
    drawArchitectureArrow(ctx, 500, 260, 500, 320);  // Airflow to Data Quality
    drawArchitectureArrow(ctx, 850, 260, 500, 320);  // API Gateway to Data Quality
    
    drawArchitectureArrow(ctx, 150, 380, 150, 440);  // ETL to S3 Raw
    drawArchitectureArrow(ctx, 500, 380, 500, 440);  // Data Quality to S3 Processed
    drawArchitectureArrow(ctx, 850, 380, 850, 440);  // Dimensional Modeling to Redshift
    
    drawArchitectureArrow(ctx, 500, 500, 500, 560);  // S3 Processed to QuickSight
    drawArchitectureArrow(ctx, 850, 500, 550, 560);  // Redshift to QuickSight
    
    // Draw monitoring components
    drawArchitectureComponent(ctx, 'CloudWatch', 325, 290, '#fdb462');
    drawArchitectureComponent(ctx, 'SNS Alerts', 325, 410, '#fdb462');
    
    // Draw monitoring connections
    drawDashedArchitectureArrow(ctx, 250, 230, 275, 290);  // Kafka to CloudWatch
    drawDashedArchitectureArrow(ctx, 250, 350, 275, 350);  // ETL to CloudWatch
    drawDashedArchitectureArrow(ctx, 325, 320, 325, 380);  // CloudWatch to SNS
    
    // Add AWS logo
    ctx.font = '16px Arial';
    ctx.fillStyle = 'rgba(255, 255, 255, 0.7)';
    ctx.textAlign = 'right';
    ctx.fillText('Powered by AWS', canvas.width - 20, canvas.height - 20);
    
    // Save the image
    const img = document.createElement('img');
    img.src = canvas.toDataURL('image/png');
    img.alt = 'Architecture Diagram';
    img.id = 'architecture_diagram_img';
    img.className = 'img-fluid rounded shadow';
    document.body.appendChild(img);
    
    // Replace image sources in the document
    const images = document.querySelectorAll('img[src*="architecture_diagram.png"]');
    images.forEach(image => {
        image.src = img.src;
    });
}

// Draw architecture layer
function drawArchitectureLayer(ctx, name, y, color) {
    // Draw layer background
    ctx.fillStyle = color;
    ctx.globalAlpha = 0.2;
    ctx.fillRect(50, y - 30, 900, 100);
    ctx.globalAlpha = 1.0;
    
    // Draw layer border
    ctx.strokeStyle = color;
    ctx.lineWidth = 2;
    ctx.strokeRect(50, y - 30, 900, 100);
    
    // Draw layer name
    ctx.fillStyle = 'white';
    ctx.font = 'bold 16px Arial';
    ctx.textAlign = 'left';
    ctx.fillText(name, 60, y - 10);
}

// Draw architecture component
function drawArchitectureComponent(ctx, name, x, y, color) {
    // Draw component background
    ctx.fillStyle = color;
    ctx.globalAlpha = 0.7;
    ctx.beginPath();
    ctx.roundRect(x - 100, y - 20, 200, 40, 5);
    ctx.fill();
    ctx.globalAlpha = 1.0;
    
    // Draw component border
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.roundRect(x - 100, y - 20, 200, 40, 5);
    ctx.stroke();
    
    // Draw component name
    ctx.fillStyle = 'white';
    ctx.font = '14px Arial';
    ctx.textAlign = 'center';
    ctx.fillText(name, x, y + 5);
}

// Draw architecture arrow
function drawArchitectureArrow(ctx, x1, y1, x2, y2) {
    const headLength = 10;
    const angle = Math.atan2(y2 - y1, x2 - x1);
    
    // Draw line
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 1.5;
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    
    // Draw arrowhead
    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - headLength * Math.cos(angle - Math.PI/6), y2 - headLength * Math.sin(angle - Math.PI/6));
    ctx.lineTo(x2 - headLength * Math.cos(angle + Math.PI/6), y2 - headLength * Math.sin(angle + Math.PI/6));
    ctx.closePath();
    ctx.fillStyle = 'white';
    ctx.fill();
}

// Draw dashed architecture arrow
function drawDashedArchitectureArrow(ctx, x1, y1, x2, y2) {
    const headLength = 10;
    const angle = Math.atan2(y2 - y1, x2 - x1);
    
    // Draw dashed line
    ctx.strokeStyle = 'white';
    ctx.lineWidth = 1.5;
    ctx.setLineDash([5, 3]);
    ctx.beginPath();
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
    ctx.stroke();
    ctx.setLineDash([]);
    
    // Draw arrowhead
    ctx.beginPath();
    ctx.moveTo(x2, y2);
    ctx.lineTo(x2 - headLength * Math.cos(angle - Math.PI/6), y2 - headLength * Math.sin(angle - Math.PI/6));
    ctx.lineTo(x2 - headLength * Math.cos(angle + Math.PI/6), y2 - headLength * Math.sin(angle + Math.PI/6));
    ctx.closePath();
    ctx.fillStyle = 'white';
    ctx.fill();
}

// Call the function when the page loads
window.addEventListener('DOMContentLoaded', generatePlaceholderImages);
