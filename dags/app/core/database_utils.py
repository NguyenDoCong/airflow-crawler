import logging
import uuid
from sqlalchemy.exc import SQLAlchemyError

from ..database import get_db
from ..models import Facebook, X, Tiktok, Instagram
# from core.extract_content import extract_content_from_transcript
from ..worker.schema import TaskStatus

logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# def get_video_from_db(db, video_id):
#     """Get data from database"""
#     try:
#         return db.query(Facebook).filter(Facebook.video_id == video_id).first()
#     except SQLAlchemyError as e:
#         logger.error(f"Error when query database: {str(e)}")
#         return None
#     finally:
#         db.close()

# def get_all_videos_from_db(db, platform=None):
#     """Get all data from database"""
#     try:
#         if platform == "x":
#             return db.query(X).filter(Tiktok.status == TaskStatus.SUCCESS.value).all()
#         elif platform == "tiktok":
#             return db.query(Tiktok).filter(Tiktok.status == TaskStatus.SUCCESS.value).all()
#         elif platform == "instagram":
#             return db.query(Instagram).filter(Tiktok.status == TaskStatus.SUCCESS.value).all()
#         else:
#             # Default to Facebook if no platform is specified
#             # or if the platform is not recognized
#             return db.query(Facebook).filter(Tiktok.status == TaskStatus.SUCCESS.value).all()
#     except SQLAlchemyError as e:
#         logger.error(f"Error when query database: {str(e)}")
#         return None
#     finally:
#         db.close()

def create_pending_video(video_id="", user_id="", url="", task_id=None, platform=None):
    """
    Create PENDING record in database while task assign
    
    Args:
        video_id (str): ID of video YouTube
        url (str): URL of video
        task_id (str): ID of Celery task
        
    Returns:
        str: task_id used
    """
    db = get_db()

    if task_id is None:
        task_id = str(uuid.uuid4())    
    try:
        # Check if video is exist
        if platform == "x":
            existing_video = db.query(X).filter(X.video_id == video_id).first()
        elif platform == "tiktok":
            existing_video = db.query(Tiktok).filter(Tiktok.video_id == video_id).first()
        elif platform == "instagram":
            existing_video = db.query(Instagram).filter(Instagram.video_id == video_id).first()
        else:
            existing_video = db.query(Facebook).filter(Facebook.video_id == video_id).first()
        
        if existing_video:
            # If video is succesfull insert, do nothing
            if existing_video.status == TaskStatus.SUCCESS.value:
                return existing_video.task_id
                
            # If video is pending, update task_id
            existing_video.task_id = task_id
            existing_video.status = TaskStatus.PENDING.value
        else:
            # Create new record with status is PENDING
            if platform == "x":
                new_video = X(
                    video_id=video_id,
                    url=url,
                    user_id=user_id,
                    task_id=task_id,
                    status=TaskStatus.PENDING.value
                )
            elif platform == "tiktok":
                new_video = Tiktok(
                    video_id=video_id,
                    url=url,
                    user_id=user_id,                    
                    task_id=task_id,
                    status=TaskStatus.PENDING.value
                )
            elif platform == "instagram":
                new_video = Instagram(
                    video_id=video_id,
                    url=url,
                    user_id=user_id,
                    task_id=task_id,
                    status=TaskStatus.PENDING.value
                )
            else:
                new_video = Facebook(
                    video_id=video_id,
                    url=url,
                    user_id=user_id,
                    task_id=task_id,
                    status=TaskStatus.PENDING.value
            )
            db.add(new_video)
            
        db.commit()
        return task_id
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error: {str(e)}")
        return None
    finally:
        db.close()

def update_video_status(video_id="", status="", transcript=None, content=None, platform=None, logs=None):
    """
    Update status of video in database
    
    Args:
        video_id (str): ID of video YouTube
        status (str): New sattus (từ TaskStatus)
        transcript (str, optional): Content of transcript 
        content (str, optional): Content when intergrate with LLM
        
    Returns:
        bool: True nếu thành công, False nếu thất bại
    """
    db = get_db()

    try:
        if platform == "x":
            video = db.query(X).filter(X.video_id == video_id).first()
        elif platform == "tiktok":
            video = db.query(Tiktok).filter(Tiktok.video_id == video_id).first()
        elif platform == "instagram":
            video = db.query(Instagram).filter(Instagram.video_id == video_id).first()
        else:
            video = db.query(Facebook).filter(Facebook.video_id == video_id).first()
        if not video:
            logger.error(f"Not found video {video_id} in database")
            return False
            
        video.status = status
        
        if transcript is not None:
            video.transcript = transcript
            
        if content is not None:
            video.content = content

        if logs is not None:
            video.logs = logs
            
        db.commit()
        return True
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error when update status in video: {str(e)}")
        return False
    finally:
        db.close()

# def save_video_to_db(db, video_id, url, transcript, content=None, status=TaskStatus.SUCCESS.value):
#     """
#     Save/update information of video into database
    
#     Args:
#         video_id (str): ID of video YouTube
#         url (str): URL of video
#         transcript (str): Content of transcript
#         content (str, optional): Content. If None, extract from transcript
#         status (str, optional): Status of video (default is SUCCESS)
        
#     Returns:
#         bool: True if succesfull, False if failure
#     """
#     # if content is None and transcript:
#     #     content = extract_content_from_transcript(transcript)
    
#     try:
#         # Check existing video
#         existing_video = db.query(Facebook).filter(Facebook.video_id == video_id).first()
        
#         if existing_video:
#             # Update if information is exist
#             existing_video.transcript = transcript
#             existing_video.content = content
#             existing_video.status = status
#         else:
#             # Create new if not exist
#             facebook = Facebook(
#                 video_id=video_id,
#                 url=url,
#                 transcript=transcript,
#                 content=content,
#                 status=status
#             )
#             db.add(facebook)
        
#         db.commit()
#         return True
#     except SQLAlchemyError as e:
#         db.rollback()
#         logger.error(f"Error when insert to database: {str(e)}")
#         return False
#     finally:
#         db.close()

# def delete_video_record(db, video_id):
#     try:
#         video = db.query(Facebook).filter(Facebook.video_id == video_id).first()
#         if video:
#             db.delete(video)
#             db.commit()
#             logger.info(f"Deleted video record for {video_id}")
#             return True
#         return False
#     except Exception as e:
#         logger.error(f"Error deleting video record for {video_id}: {str(e)}")
#         db.rollback()
#         return False
#     finally:
#         db.close()

# def get_distinct_user_ids_from_db(db, platform=None):
#     """Get distinct user IDs from database"""
#     try:
#         if platform == "X":
#             return db.query(X.user_id).distinct().all()
#         elif platform == "tiktok":
#             return db.query(Tiktok.user_id).distinct().all()
#         elif platform == "instagram":
#             return db.query(Instagram.user_id).distinct().all()
#         else:
#             # Default to Facebook if no platform is specified
#             # or if the platform is not recognized
#             return db.query(Facebook.user_id).distinct().all()
#     except SQLAlchemyError as e:
#         logger.error(f"Error when query database: {str(e)}")
#         return None
#     finally:
#         db.close()

def get_info_by_user_id(user_id="", platform=None):
    """Get all data from database"""
    db = get_db()

    try:
        if platform == "X":
            return db.query(X).filter(X.user_id == user_id, X.status=="SUCCESS").all()
        elif platform == "tiktok":
            return db.query(Tiktok).filter(Tiktok.user_id == user_id, Tiktok.status=='SUCCESS').all()
        elif platform == "instagram":
            return db.query(Instagram).filter(Instagram.user_id == user_id, Instagram.status=='SUCCESS').all()
        else:
            # Default to Facebook if no platform is specified
            # or if the platform is not recognized
            return db.query(Facebook).filter(Facebook.user_id == user_id, Facebook.status=='SUCCESS').all()
    except SQLAlchemyError as e:
        logger.error(f"Error when query database: {str(e)}")
        return None
    finally:
        db.close()

# def delete_user_by_id(db, user_id, platform=None):
#     """Delete user by ID from database"""
#     try:
#         if platform == "X":
#             db.query(X).filter(X.user_id == user_id).delete()
#         elif platform == "tiktok":
#             db.query(Tiktok).filter(Tiktok.user_id == user_id).delete()
#         elif platform == "instagram":
#             db.query(Instagram).filter(Instagram.user_id == user_id).delete()
#         else:
#             # Default to Facebook if no platform is specified
#             # or if the platform is not recognized
#             db.query(Facebook).filter(Facebook.user_id == user_id).delete()
#         db.commit()
#     except SQLAlchemyError as e:
#         logger.error(f"Error when delete user: {str(e)}")
#         db.rollback()
#     finally:
#         db.close()