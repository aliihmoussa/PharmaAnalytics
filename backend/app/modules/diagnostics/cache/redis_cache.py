"""Redis cache implementation for ML module with performance optimizations."""

import json
import hashlib
from typing import Optional, Any
import redis
from backend.app.config import config
import logging

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache wrapper for ML features and profiling results."""
    
    def __init__(self):
        """Initialize Redis connection."""
        try:
            redis_host = config.REDIS_HOST or 'localhost'
            redis_port = config.REDIS_PORT
            redis_db = config.REDIS_DB if hasattr(config, 'REDIS_DB') else 0
            
            self.client = redis.Redis(
                host=redis_host,
                port=redis_port,
                db=redis_db,
                decode_responses=True,
                socket_connect_timeout=2,
                socket_timeout=2
            )
            # Test connection
            self.client.ping()
            self.enabled = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis not available, caching disabled: {str(e)}")
            self.client = None
            self.enabled = False
    
    def _make_key(self, prefix: str, *args) -> str:
        """Create cache key from prefix and arguments."""
        key_parts = [prefix] + [str(arg) for arg in args]
        key_string = ':'.join(key_parts)
        # Hash long keys to keep them manageable
        if len(key_string) > 200:
            key_string = prefix + ':' + hashlib.md5(key_string.encode()).hexdigest()
        return f"ml:{key_string}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if not self.enabled:
            return None
        
        try:
            value = self.client.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {str(e)}")
            return None
    
    def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600
    ) -> bool:
        """Set value in cache with TTL."""
        if not self.enabled:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            return self.client.setex(key, ttl, serialized)
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {str(e)}")
            return False
    
    def delete(self, key: str) -> bool:
        """Delete key from cache."""
        if not self.enabled:
            return False
        
        try:
            return bool(self.client.delete(key))
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {str(e)}")
            return False
    
    def get_profiling(
        self,
        drug_code: str,
        department: Optional[int] = None
    ) -> Optional[dict]:
        """Get profiling results from cache."""
        key = self._make_key('profiling', drug_code, department or 'all')
        return self.get(key)
    
    def set_profiling(
        self,
        drug_code: str,
        department: Optional[int],
        value: dict,
        ttl: int = 86400  # 24 hours
    ) -> bool:
        """Cache profiling results."""
        key = self._make_key('profiling', drug_code, department or 'all')
        return self.set(key, value, ttl)
    
    def invalidate_profiling(self, drug_code: str, department: Optional[int] = None):
        """Invalidate profiling cache."""
        key = self._make_key('profiling', drug_code, department or 'all')
        self.delete(key)

