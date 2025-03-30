// Generate a simple AWS architecture diagram
function generateAwsArchitectureDiagram() {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    
    // Set canvas dimensions
    canvas.width = 1000;
    canvas.height = 600;
    
    // Clear canvas
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    
    // Add title
    ctx.fillStyle = '#333333';
    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'center';
    ctx.fillText('AWS Architecture - Telemedicine Appointment Data Pipeline', canvas.width / 2, 40);
    
    // Define colors
    const colors = {
        dataSources: '#8dd3c7',
        ingestion: '#ffffb3',
        processing: '#bebada',
        storage: '#fb8072',
        analytics: '#80b1d3',
        monitoring: '#fdb462'
    };
    
    // Draw layers
    drawLayer('Data Sources', 80, colors.dataSources);
    drawLayer('Ingestion Layer', 200, colors.ingestion);
    drawLayer('Processing Layer', 320, colors.processing);
    drawLayer('Storage Layer', 440, colors.storage);
    drawLayer('Analytics Layer', 560, colors.analytics);
    
    // Draw components
    // Data Sources
    drawComponent('Appointment Logs (External API)', 100, 110, colors.dataSources);
    drawComponent('Patient Feedback (S3 JSON Files)', 350, 110, colors.dataSources);
    drawComponent('Provider Data (RDS)', 600, 110, colors.dataSources);
    
    // Ingestion Layer
    drawComponent('Amazon MSK (Kafka)', 100, 230, colors.ingestion);
    drawComponent('Amazon MWAA (Airflow)', 350, 230, colors.ingestion);
    drawComponent('API Gateway / S3 Connector', 600, 230, colors.ingestion);
    
    // Processing Layer
    drawComponent('AWS Glue (ETL)', 100, 350, colors.processing);
    drawComponent('Data Quality Checks', 350, 350, colors.processing);
    drawComponent('AWS Step Functions', 600, 350, colors.processing);
    
    // Storage Layer
    drawComponent('S3 Raw Data', 100, 470, colors.storage);
    drawComponent('S3 Processed Data', 350, 470, colors.storage);
    drawComponent('Amazon Redshift', 600, 470, colors.storage);
    
    // Analytics Layer
    drawComponent('Amazon QuickSight', 350, 590, colors.analytics);
    
    // Draw arrows
    drawArrow(150, 140, 150, 200);  // Appointment Logs to MSK
    drawArrow(350, 140, 350, 200);  // Patient Feedback to MWAA
    drawArrow(600, 140, 600, 200);  // Provider Data to API Gateway
    
    drawArrow(150, 260, 150, 320);  // MSK to Glue
    drawArrow(350, 260, 350, 320);  // MWAA to Data Quality
    drawArrow(600, 260, 350, 320);  // API Gateway to Data Quality
    
    drawArrow(150, 380, 150, 440);  // Glue to S3 Raw
    drawArrow(350, 380, 350, 440);  // Data Quality to S3 Processed
    drawArrow(600, 380, 600, 440);  // Step Functions to Redshift
    
    drawArrow(350, 500, 350, 560);  // S3 Processed to QuickSight
    drawArrow(600, 500, 400, 560);  // Redshift to QuickSight
    
    // Draw monitoring components
    drawComponent('Amazon CloudWatch', 800, 230, colors.monitoring);
    drawComponent('Amazon SNS (Alerts)', 800, 350, colors.monitoring);
    
    // Draw monitoring connections
    drawDashedArrow(700, 230, 770, 230);  // Ingestion to CloudWatch
    drawDashedArrow(700, 350, 770, 350);  // Processing to CloudWatch
    drawDashedArrow(800, 260, 800, 320);  // CloudWatch to SNS
    
    // Save the image
    const img = document.createElement('img');
    img.src = canvas.toDataURL('image/png');
    img.alt = 'AWS Architecture Diagram';
    img.id = 'aws_architecture_diagram';
    img.className = 'img-fluid rounded shadow';
    document.body.appendChild(img);
    
    // Replace image sources in the document
    const images = document.querySelectorAll('img[src="assets/aws_architecture_diagram.png"]');
    images.forEach(image => {
        image.src = img.src;
    });
    
    function drawLayer(name, y, color) {
        // Draw layer background
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.3;
        ctx.fillRect(50, y - 30, 900, 100);
        ctx.globalAlpha = 1.0;
        
        // Draw layer border
        ctx.strokeStyle = '#555555';
        ctx.lineWidth = 1;
        ctx.strokeRect(50, y - 30, 900, 100);
        
        // Draw layer name
        ctx.fillStyle = '#333333';
        ctx.font = 'bold 16px Arial';
        ctx.textAlign = 'left';
        ctx.fillText(name, 60, y - 10);
    }
    
    function drawComponent(name, x, y, color) {
        // Draw component background
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.7;
        ctx.beginPath();
        ctx.roundRect(x - 100, y - 20, 200, 40, 5);
        ctx.fill();
        ctx.globalAlpha = 1.0;
        
        // Draw component border
        ctx.strokeStyle = '#555555';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.roundRect(x - 100, y - 20, 200, 40, 5);
        ctx.stroke();
        
        // Draw component name
        ctx.fillStyle = '#333333';
        ctx.font = '14px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(name, x, y + 5);
    }
    
    function drawArrow(x1, y1, x2, y2) {
        const headLength = 10;
        const angle = Math.atan2(y2 - y1, x2 - x1);
        
        // Draw line
        ctx.strokeStyle = '#555555';
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
        ctx.fillStyle = '#555555';
        ctx.fill();
    }
    
    function drawDashedArrow(x1, y1, x2, y2) {
        const headLength = 10;
        const angle = Math.atan2(y2 - y1, x2 - x1);
        
        // Draw dashed line
        ctx.strokeStyle = '#555555';
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
        ctx.fillStyle = '#555555';
        ctx.fill();
    }
}

// Call the function when the page loads
window.addEventListener('DOMContentLoaded', generateAwsArchitectureDiagram);
