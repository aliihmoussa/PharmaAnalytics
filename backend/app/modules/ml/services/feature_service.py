"""Service for feature/profiling endpoint with caching."""

from typing import Optional, Dict
from datetime import date
from backend.app.modules.ml.diagnostics import DrugProfiler
from backend.app.modules.ml.cache import RedisCache
from backend.app.shared.base_service import BaseService
import logging

logger = logging.getLogger(__name__)


class FeatureService(BaseService):
    """Service for drug feature/profiling endpoint."""
    
    def __init__(self):
        """Initialize service."""
        super().__init__()
        self.profiler = DrugProfiler(use_cache=True)
        self.cache = RedisCache()
    
    def get_features(
        self,
        drug_code: str,
        department: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        use_cache: bool = True
    ) -> Dict:
        """
        Get drug features/profiling data with caching.
        
        Args:
            drug_code: Drug code
            department: Optional department filter
            start_date: Optional start date
            end_date: Optional end date
            use_cache: Whether to use cache
        
        Returns:
            Dictionary with profiling results
        """
        # Try cache first
        if use_cache:
            cached_result = self.cache.get_profiling(drug_code, department)
            if cached_result:
                logger.info(f"Cache hit for drug_code={drug_code}, department={department}")
                return cached_result
        
        # Generate profiling
        logger.info(f"Generating profiling for drug_code={drug_code}, department={department}")
        try:
            result = self.profiler.profile(
                drug_code=drug_code,
                department=department,
                start_date=start_date,
                end_date=end_date
            )
            
            # Cache result (24 hours TTL)
            if use_cache:
                self.cache.set_profiling(
                    drug_code=drug_code,
                    department=department,
                    value=result,
                    ttl=86400
                )
            
            return {
                'success': True,
                'data': result,
                'meta': {'status_code': 200}
            }
            
        except ValueError as e:
            logger.warning(f"Profiling error: {str(e)}")
            return {
                'success': False,
                'data': {'error': str(e)},
                'meta': {'status_code': 404}
            }
        except Exception as e:
            logger.error(f"Unexpected error in profiling: {str(e)}", exc_info=True)
            return {
                'success': False,
                'data': {'error': 'Internal server error'},
                'meta': {'status_code': 500}
            }

