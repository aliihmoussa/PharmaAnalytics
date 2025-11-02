"""Background job processing system for async file ingestion."""

import threading
import queue
import logging
from typing import Callable, Dict, Any, Optional
from enum import Enum
from datetime import datetime
import traceback

logger = logging.getLogger(__name__)


class JobStatus(Enum):
    """Job status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BackgroundJob:
    """Represents a background job."""
    
    def __init__(self, job_id: str, func: Callable, args: tuple = (), kwargs: dict = None):
        self.job_id = job_id
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.status = JobStatus.PENDING
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.progress = 0  # 0-100
        self.progress_message = ""
        self._lock = threading.Lock()
    
    def update_progress(self, progress: int, message: str = ""):
        """Update job progress."""
        with self._lock:
            self.progress = max(0, min(100, progress))
            self.progress_message = message
    
    def execute(self):
        """Execute the job."""
        with self._lock:
            self.status = JobStatus.PROCESSING
            self.started_at = datetime.now()
        
        try:
            logger.info(f"Executing job {self.job_id}")
            self.result = self.func(*self.args, **self.kwargs)
            
            with self._lock:
                self.status = JobStatus.COMPLETED
                self.completed_at = datetime.now()
                self.progress = 100
            
            logger.info(f"Job {self.job_id} completed successfully")
            return self.result
        
        except Exception as e:
            with self._lock:
                self.status = JobStatus.FAILED
                self.error = str(e)
                self.completed_at = datetime.now()
            
            logger.error(f"Job {self.job_id} failed: {e}", exc_info=True)
            raise
    
    def cancel(self):
        """Cancel the job (if pending)."""
        with self._lock:
            if self.status == JobStatus.PENDING:
                self.status = JobStatus.CANCELLED
                self.completed_at = datetime.now()
                return True
            return False
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert job to dictionary."""
        with self._lock:
            return {
                'job_id': self.job_id,
                'status': self.status.value,
                'progress': self.progress,
                'progress_message': self.progress_message,
                'error': self.error,
                'created_at': self.created_at.isoformat() if self.created_at else None,
                'started_at': self.started_at.isoformat() if self.started_at else None,
                'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            }


class BackgroundJobExecutor:
    """Manages background job execution using thread pool."""
    
    def __init__(self, num_workers: int = 2):
        self.num_workers = num_workers
        self.job_queue = queue.Queue()
        self.jobs: Dict[str, BackgroundJob] = {}
        self.jobs_lock = threading.Lock()
        self.workers = []
        self.running = False
    
    def start(self):
        """Start worker threads."""
        if self.running:
            return
        
        self.running = True
        for i in range(self.num_workers):
            worker = threading.Thread(target=self._worker, daemon=True, name=f"JobWorker-{i}")
            worker.start()
            self.workers.append(worker)
        
        logger.info(f"Started {self.num_workers} background job workers")
    
    def stop(self):
        """Stop worker threads (waits for current jobs to finish)."""
        self.running = False
        # Add sentinel values to wake up workers
        for _ in range(self.num_workers):
            self.job_queue.put(None)
        
        for worker in self.workers:
            worker.join(timeout=5.0)
        
        self.workers.clear()
        logger.info("Background job workers stopped")
    
    def submit(self, job_id: str, func: Callable, args: tuple = (), kwargs: dict = None) -> BackgroundJob:
        """Submit a job for execution."""
        job = BackgroundJob(job_id, func, args, kwargs)
        
        with self.jobs_lock:
            self.jobs[job_id] = job
        
        self.job_queue.put(job)
        logger.info(f"Submitted job {job_id}")
        return job
    
    def get_job(self, job_id: str) -> Optional[BackgroundJob]:
        """Get job by ID."""
        with self.jobs_lock:
            return self.jobs.get(job_id)
    
    def cancel_job(self, job_id: str) -> bool:
        """Cancel a pending job."""
        job = self.get_job(job_id)
        if job:
            return job.cancel()
        return False
    
    def _worker(self):
        """Worker thread that processes jobs."""
        while self.running:
            try:
                job = self.job_queue.get(timeout=1.0)
                
                if job is None:  # Sentinel value to stop
                    break
                
                if job.status == JobStatus.CANCELLED:
                    continue
                
                job.execute()
            
            except queue.Empty:
                continue
            
            except Exception as e:
                logger.error(f"Worker error: {e}", exc_info=True)


# Global executor instance
_executor: Optional[BackgroundJobExecutor] = None


def get_executor() -> BackgroundJobExecutor:
    """Get or create the global job executor."""
    global _executor
    if _executor is None:
        _executor = BackgroundJobExecutor(num_workers=2)
        _executor.start()
    return _executor


def shutdown_executor():
    """Shutdown the global executor."""
    global _executor
    if _executor:
        _executor.stop()
        _executor = None

