"""
Celery Tasks for Background Processing
"""

from celery import Celery
from celery.utils.log import get_task_logger
import os
import traceback
from datetime import datetime

from .config import Config
from ..core.processor import HypersequesterProcessor
from ..utils.helpers import ensure_directory, generate_unique_filename

# Initialize Celery
celery_app = Celery('hypersequester')
celery_app.config_from_object(Config)

logger = get_task_logger(__name__)

@celery_app.task(bind=True)
def process_carbon_assessment(self, assessment_id: str, input_file_path: str, 
                             metadata: dict, output_dir: str):
    """
    Background task for processing carbon assessments
    
    Args:
        assessment_id: Unique identifier for the assessment
        input_file_path: Path to the hyperspectral data file
        metadata: Assessment metadata
        output_dir: Directory for output files
    """
    
    logger.info(f"Starting carbon assessment processing for {assessment_id}")
    
    try:
        # Update task status
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Starting processing', 'progress': 0}
        )
        
        # Initialize processor
        processor = HypersequesterProcessor()
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Processor initialized', 'progress': 10}
        )
        
        # Process the assessment
        results = processor.process_assessment(
            input_file_path=input_file_path,
            output_dir=output_dir,
            metadata=metadata
        )
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Processing completed', 'progress': 90}
        )
        
        # Final result
        if results['status'] == 'completed':
            logger.info(f"Carbon assessment {assessment_id} completed successfully")
            return {
                'status': 'SUCCESS',
                'results': results,
                'assessment_id': assessment_id,
                'completed_at': datetime.utcnow().isoformat()
            }
        else:
            logger.error(f"Carbon assessment {assessment_id} failed: {results.get('error')}")
            return {
                'status': 'FAILURE',
                'error': results.get('error'),
                'assessment_id': assessment_id
            }
    
    except Exception as exc:
        logger.error(f"Error processing assessment {assessment_id}: {str(exc)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Processing failed',
                'error': str(exc),
                'assessment_id': assessment_id
            }
        )
        
        raise exc

@celery_app.task(bind=True)
def train_species_model(self, training_data_path: str, model_output_path: str):
    """
    Background task for training species classification models
    
    Args:
        training_data_path: Path to training data
        model_output_path: Path to save the trained model
    """
    
    logger.info("Starting species model training")
    
    try:
        from ..models.species_classifier import SpeciesClassifier
        
        # Update task status
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Loading training data', 'progress': 10}
        )
        
        # Load training data (implementation depends on data format)
        # This is a placeholder - actual implementation would load real data
        training_data = {}  # Load from training_data_path
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Initializing model', 'progress': 20}
        )
        
        # Initialize and train model
        classifier = SpeciesClassifier(model_type='random_forest')
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Training model', 'progress': 30}
        )
        
        # Train the model
        results = classifier.train(training_data)
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Saving model', 'progress': 90}
        )
        
        # Save the trained model
        classifier.save_model(model_output_path)
        
        logger.info("Species model training completed successfully")
        
        return {
            'status': 'SUCCESS',
            'results': results,
            'model_path': model_output_path,
            'completed_at': datetime.utcnow().isoformat()
        }
    
    except Exception as exc:
        logger.error(f"Error training species model: {str(exc)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Training failed',
                'error': str(exc)
            }
        )
        
        raise exc

@celery_app.task(bind=True)
def train_carbon_model(self, training_data_path: str, model_output_dir: str):
    """
    Background task for training carbon estimation models
    
    Args:
        training_data_path: Path to training data
        model_output_dir: Directory to save the trained models
    """
    
    logger.info("Starting carbon model training")
    
    try:
        from ..models.carbon_estimator import CarbonEstimator
        
        # Update task status
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Loading training data', 'progress': 10}
        )
        
        # Load training data
        training_data = {}  # Load from training_data_path
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Initializing models', 'progress': 20}
        )
        
        # Initialize and train models
        estimator = CarbonEstimator(model_type='random_forest')
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Training models', 'progress': 30}
        )
        
        # Train the models
        results = estimator.train(training_data)
        
        # Update progress
        self.update_state(
            state='PROCESSING',
            meta={'status': 'Saving models', 'progress': 90}
        )
        
        # Save the trained models
        ensure_directory(model_output_dir)
        estimator.save_models(model_output_dir)
        
        logger.info("Carbon model training completed successfully")
        
        return {
            'status': 'SUCCESS',
            'results': results,
            'model_dir': model_output_dir,
            'completed_at': datetime.utcnow().isoformat()
        }
    
    except Exception as exc:
        logger.error(f"Error training carbon models: {str(exc)}")
        logger.error(traceback.format_exc())
        
        self.update_state(
            state='FAILURE',
            meta={
                'status': 'Training failed',
                'error': str(exc)
            }
        )
        
        raise exc

@celery_app.task
def cleanup_old_files(days_old: int = 30):
    """
    Background task for cleaning up old files
    
    Args:
        days_old: Delete files older than this many days
    """
    
    logger.info(f"Starting cleanup of files older than {days_old} days")
    
    import os
    import time
    from pathlib import Path
    
    try:
        config = Config()
        cleanup_dirs = [config.UPLOAD_FOLDER, config.RESULTS_FOLDER]
        
        total_deleted = 0
        total_size_freed = 0
        
        for directory in cleanup_dirs:
            if not os.path.exists(directory):
                continue
            
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check file age
                    file_age = time.time() - os.path.getmtime(file_path)
                    if file_age > (days_old * 24 * 3600):
                        try:
                            file_size = os.path.getsize(file_path)
                            os.remove(file_path)
                            total_deleted += 1
                            total_size_freed += file_size
                            logger.debug(f"Deleted old file: {file_path}")
                        except Exception as e:
                            logger.warning(f"Could not delete {file_path}: {e}")
        
        logger.info(f"Cleanup completed: {total_deleted} files deleted, "
                   f"{total_size_freed / (1024*1024):.1f} MB freed")
        
        return {
            'status': 'SUCCESS',
            'files_deleted': total_deleted,
            'size_freed_mb': total_size_freed / (1024*1024),
            'completed_at': datetime.utcnow().isoformat()
        }
    
    except Exception as exc:
        logger.error(f"Error during cleanup: {str(exc)}")
        return {
            'status': 'FAILURE',
            'error': str(exc)
        }

# Periodic tasks configuration
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-old-files': {
        'task': 'src.backend.tasks.cleanup_old_files',
        'schedule': crontab(hour=2, minute=0),  # Run daily at 2 AM
        'args': (30,)  # Delete files older than 30 days
    },
}

celery_app.conf.timezone = 'UTC'
