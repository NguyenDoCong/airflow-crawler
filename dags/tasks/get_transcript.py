from airflow.decorators import task
from app.core.database_utils import update_video_status
from app.worker.schema import TaskStatus

# @task.virtualenv(
#     requirements=[
#         'faster-whisper==1.1.1',
#     ],
#     system_site_packages=False,
# )
# @task
# def audio_to_transcript(downloads, platform="tiktok"):
def audio_to_transcript(**context):
    """
    Convert audio file to transcript using Faster Whisper.
    
    Args:
        audio_path (str): Path to audio file
        
    Returns:
        str: Transcribed text
    """
    import logging
    from faster_whisper import WhisperModel #type: ignore[import]
    
    platform = context.get("platform", "tiktok")
    task_ids = context.get("task_ids", f"{platform}_videos_scraper_task")

    ti = context["ti"]
    downloads = ti.xcom_pull(task_ids=task_ids)
    if not downloads:
        logging.info("No downloads to process.")
        return
    # from faster_whisper import WhisperModel
    # if len(downloads) == 0:
    #     logging.info("No downloads to process.")
    #     return
    else:
        logging.info(f"Number of downloads to process: {len(downloads)}")
        for download in downloads:
            try: 
                id = download["video_id"]
                audio_path = download["file_path"]
                logging.info(f"Processing audio file: {audio_path}")
                
                # Initialize model
                model_size = "tiny"
                # model = WhisperModel("large-v3", device="cpu", compute_type="int8")
                model = WhisperModel(model_size, device="cpu", compute_type="int8")
                
                # Transcribe audio
                segments, info = model.transcribe(audio_path, beam_size=5)

                logging.info(f"Detected language '{info.language}' with probability {info.language_probability}")

                # Combine transcript segments
                transcription = ""
                for segment in segments:
                    text = segment.text.strip()
                    transcription += text + " "

                # return transcription.strip()
                update_video_status(id,
                                    TaskStatus.SUCCESS.value,
                                    transcript=transcription.strip(),
                                    platform=platform)
            except Exception as e:
                logging.error(f"Error transcripting video from {id}: {str(e)}")
                update_video_status(id,
                                    TaskStatus.FAILURE.value,
                                    platform=platform,
                                    logs=f"Error transcripting video: {str(e)}")
