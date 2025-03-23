# Mock Celery implementation for production deployments where Celery isn't needed
class CeleryAppMock:
    """Mock of Celery app that provides basic functionality without requiring Celery package"""
    
    def __init__(self, name):
        self.name = name
        self.conf = type('conf', (object,), {
            'update': lambda *args, **kwargs: None,
            'beat_schedule': {}
        })
    
    def task(self, *args, **kwargs):
        """Mock decorator that returns the function unchanged"""
        def decorator(func):
            return func
        # Handle both @app.task and @app.task(...)
        if len(args) == 1 and callable(args[0]):
            return args[0]
        return decorator
    
    def autodiscover_tasks(self, *args, **kwargs):
        """Mock implementation of autodiscover_tasks"""
        pass
    
    def config_from_object(self, *args, **kwargs):
        """Mock implementation of config_from_object"""
        pass

# Create a mock celery app
celery_app = CeleryAppMock('kriangle')

# Export the mock app
__all__ = ('celery_app',)


