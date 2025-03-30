import os
import subprocess
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/home/ubuntu/telemedicine_pipeline/data_processing/pipeline.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('telemedicine_pipeline')

# Define pipeline components
PIPELINE_COMPONENTS = [
    {
        'name': 'Data Transformation',
        'script': '/home/ubuntu/telemedicine_pipeline/data_processing/etl/transform_data.py',
        'description': 'Transform raw data into dimensional model',
        'timeout': 300  # 5 minutes
    },
    {
        'name': 'Data Quality Checks',
        'script': '/home/ubuntu/telemedicine_pipeline/data_processing/etl/data_quality_checks.py',
        'description': 'Perform data quality checks on transformed data',
        'timeout': 180  # 3 minutes
    }
]

def run_component(component):
    """Run a pipeline component and return the result"""
    start_time = time.time()
    logger.info(f"Starting component: {component['name']}")
    logger.info(f"Description: {component['description']}")
    
    try:
        # Run the script
        result = subprocess.run(
            ['python3', component['script']],
            capture_output=True,
            text=True,
            timeout=component['timeout']
        )
        
        # Check if the script ran successfully
        if result.returncode == 0:
            logger.info(f"Component {component['name']} completed successfully")
            logger.info(f"Output: {result.stdout}")
            status = 'SUCCESS'
        else:
            logger.error(f"Component {component['name']} failed with return code {result.returncode}")
            logger.error(f"Error: {result.stderr}")
            status = 'FAILED'
        
        # Calculate duration
        duration = time.time() - start_time
        
        return {
            'component': component['name'],
            'status': status,
            'duration': duration,
            'stdout': result.stdout,
            'stderr': result.stderr,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    except subprocess.TimeoutExpired:
        logger.error(f"Component {component['name']} timed out after {component['timeout']} seconds")
        return {
            'component': component['name'],
            'status': 'TIMEOUT',
            'duration': time.time() - start_time,
            'stdout': '',
            'stderr': f"Timed out after {component['timeout']} seconds",
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    except Exception as e:
        logger.error(f"Error running component {component['name']}: {str(e)}")
        return {
            'component': component['name'],
            'status': 'ERROR',
            'duration': time.time() - start_time,
            'stdout': '',
            'stderr': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

def run_pipeline():
    """Run the complete data processing pipeline"""
    logger.info("Starting data processing pipeline")
    
    # Create results directory
    results_dir = '/home/ubuntu/telemedicine_pipeline/data_processing/results'
    os.makedirs(results_dir, exist_ok=True)
    
    # Run each component in sequence
    pipeline_start_time = time.time()
    results = []
    
    for component in PIPELINE_COMPONENTS:
        result = run_component(component)
        results.append(result)
        
        # If a component fails, stop the pipeline
        if result['status'] != 'SUCCESS':
            logger.error(f"Pipeline stopped due to component failure: {component['name']}")
            break
    
    # Calculate pipeline duration
    pipeline_duration = time.time() - pipeline_start_time
    
    # Generate pipeline summary
    summary = {
        'pipeline_start': datetime.fromtimestamp(pipeline_start_time).strftime('%Y-%m-%d %H:%M:%S'),
        'pipeline_end': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'pipeline_duration': pipeline_duration,
        'components_total': len(PIPELINE_COMPONENTS),
        'components_completed': sum(1 for r in results if r['status'] == 'SUCCESS'),
        'components_failed': sum(1 for r in results if r['status'] != 'SUCCESS'),
        'overall_status': 'SUCCESS' if all(r['status'] == 'SUCCESS' for r in results) else 'FAILED',
        'component_results': results
    }
    
    # Save summary to file
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    summary_file = os.path.join(results_dir, f'pipeline_summary_{timestamp}.txt')
    
    with open(summary_file, 'w') as f:
        f.write(f"Pipeline Summary\n")
        f.write(f"===============\n\n")
        f.write(f"Start Time: {summary['pipeline_start']}\n")
        f.write(f"End Time: {summary['pipeline_end']}\n")
        f.write(f"Duration: {summary['pipeline_duration']:.2f} seconds\n")
        f.write(f"Status: {summary['overall_status']}\n\n")
        f.write(f"Components: {summary['components_completed']}/{summary['components_total']} completed\n\n")
        
        f.write(f"Component Details\n")
        f.write(f"----------------\n\n")
        
        for result in results:
            f.write(f"Component: {result['component']}\n")
            f.write(f"Status: {result['status']}\n")
            f.write(f"Duration: {result['duration']:.2f} seconds\n")
            f.write(f"Timestamp: {result['timestamp']}\n")
            f.write(f"Output: {result['stdout'][:500]}{'...' if len(result['stdout']) > 500 else ''}\n")
            
            if result['stderr']:
                f.write(f"Error: {result['stderr'][:500]}{'...' if len(result['stderr']) > 500 else ''}\n")
            
            f.write("\n")
    
    logger.info(f"Pipeline completed with status: {summary['overall_status']}")
    logger.info(f"Summary saved to: {summary_file}")
    
    return summary

if __name__ == "__main__":
    run_pipeline()
