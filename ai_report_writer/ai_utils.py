"""
AI Utilities for intelligent model fallback and management
"""

import logging
from typing import Dict, List, Optional, Any, Callable
from .model_config import get_model_list, get_next_model

logger = logging.getLogger(__name__)


class ModelFallbackManager:
    """
    Manages automatic fallback to different AI models when one fails.
    """
    
    def __init__(self):
        self.failed_models = {}
        self.model_performance = {}
    
    def get_working_model(self, task_type: str, current_model: str) -> str:
        """
        Get the next working model to try when the current one fails.
        
        Args:
            task_type: Type of task (breakdown, reviewer, finalizer, reanalyzer)
            current_model: The model that just failed
            
        Returns:
            Next model to try, or None if all models exhausted
        """
        if task_type not in self.failed_models:
            self.failed_models[task_type] = []
        
        # Add current model to failed list
        if current_model not in self.failed_models[task_type]:
            self.failed_models[task_type].append(current_model)
        
        # Get next model to try
        next_model = get_next_model(
            task_type, 
            current_model, 
            self.failed_models[task_type]
        )
        
        if next_model:
            logger.info(f"Switching from {current_model} to {next_model} for {task_type}")
            return next_model
        else:
            logger.warning(f"All models exhausted for {task_type}")
            return None
    
    def reset_failures(self, task_type: str = None):
        """
        Reset failure tracking for a specific task type or all tasks.
        
        Args:
            task_type: Specific task type to reset, or None for all
        """
        if task_type:
            self.failed_models.pop(task_type, None)
            logger.info(f"Reset failure tracking for {task_type}")
        else:
            self.failed_models.clear()
            logger.info("Reset failure tracking for all tasks")
    
    def record_success(self, task_type: str, model: str, performance_metrics: Dict = None):
        """
        Record successful completion of a task with a model.
        
        Args:
            task_type: Type of task completed
            model: Model that successfully completed the task
            performance_metrics: Optional performance metrics
        """
        if task_type not in self.model_performance:
            self.model_performance[task_type] = {}
        
        if model not in self.model_performance[task_type]:
            self.model_performance[task_type][model] = {
                'success_count': 0,
                'failure_count': 0,
                'avg_response_time': 0,
                'last_used': None
            }
        
        # Update success metrics
        self.model_performance[task_type][model]['success_count'] += 1
        if performance_metrics:
            self.model_performance[task_type][model].update(performance_metrics)
        
        # Remove from failed models if it was there
        if task_type in self.failed_models and model in self.failed_models[task_type]:
            self.failed_models[task_type].remove(model)
            logger.info(f"Model {model} recovered for {task_type}")
    
    def get_best_performing_model(self, task_type: str) -> Optional[str]:
        """
        Get the best performing model for a task type based on success rate.
        
        Args:
            task_type: Type of task
            
        Returns:
            Best performing model, or None if no data available
        """
        if task_type not in self.model_performance:
            return None
        
        best_model = None
        best_score = -1
        
        for model, metrics in self.model_performance[task_type].items():
            if metrics['success_count'] > 0:
                # Calculate success rate
                total = metrics['success_count'] + metrics['failure_count']
                success_rate = metrics['success_count'] / total
                
                if success_rate > best_score:
                    best_score = success_rate
                    best_model = model
        
        return best_model


def execute_with_fallback(
    task_type: str,
    current_model: str,
    execution_func: Callable,
    fallback_manager: ModelFallbackManager = None,
    max_retries: int = 3,
    **kwargs
) -> Any:
    """
    Execute a function with automatic model fallback.
    
    Args:
        task_type: Type of task being executed
        current_model: Current model to try first
        execution_func: Function to execute (should accept 'model' parameter)
        fallback_manager: ModelFallbackManager instance
        max_retries: Maximum number of retries with different models
        **kwargs: Additional arguments to pass to execution_func
        
    Returns:
        Result of successful execution
        
    Raises:
        Exception: If all models fail after max_retries
    """
    if fallback_manager is None:
        fallback_manager = ModelFallbackManager()
    
    last_error = None
    models_tried = [current_model]
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting {task_type} with model: {current_model}")
            
            # Execute the function with current model
            result = execution_func(model=current_model, **kwargs)
            
            # Record success
            fallback_manager.record_success(task_type, current_model)
            logger.info(f"Successfully completed {task_type} with {current_model}")
            
            return result
            
        except Exception as e:
            last_error = e
            logger.warning(f"Model {current_model} failed for {task_type}: {str(e)}")
            
            # Get next model to try
            next_model = fallback_manager.get_working_model(task_type, current_model)
            
            if next_model and next_model not in models_tried:
                current_model = next_model
                models_tried.append(current_model)
                logger.info(f"Retrying with model: {current_model}")
            else:
                logger.error(f"No more models available for {task_type}")
                break
    
    # All attempts failed
    error_msg = f"All models failed for {task_type}. Models tried: {models_tried}"
    logger.error(error_msg)
    raise Exception(error_msg) from last_error


def get_model_info(task_type: str) -> Dict[str, Any]:
    """
    Get information about available models for a task type.
    
    Args:
        task_type: Type of task
        
    Returns:
        Dictionary with model information
    """
    try:
        from .model_config import get_model_list, MODEL_CATEGORIES, MODEL_METADATA
        
        models = get_model_list(task_type)
        model_info = {
            'task_type': task_type,
            'total_models': len(models),
            'models': []
        }
        
        for i, model in enumerate(models):
            info = {
                'name': model,
                'priority': i + 1,
                'category': 'Unknown',
                'description': 'No description available',
                'reliability': 'Unknown',
                'speed': 'Unknown',
                'cost': 'Unknown'
            }
            
            # Get metadata if available
            if model in MODEL_METADATA:
                info.update(MODEL_METADATA[model])
            
            model_info['models'].append(info)
        
        return model_info
        
    except ImportError:
        return {
            'task_type': task_type,
            'total_models': 0,
            'models': [],
            'error': 'Model configuration not available'
        }


# Global fallback manager instance
fallback_manager = ModelFallbackManager()
