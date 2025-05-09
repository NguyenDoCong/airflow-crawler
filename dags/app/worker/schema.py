from enum import Enum

# ======================== Schema for the Task Celery ========================
class TaskStatus(Enum):
    PENDING: str = "PENDING"
    PROCESSING: str = "PROCESSING"
    DOWNLOADED: str = "DOWNLOADED"
    SUCCESS: str = "SUCCESS"
    FAILURE: str = "FAILURE"
    RETRY: str = "RETRY"
    FAILED_RETRY: str = "FAILED_RETRY"

