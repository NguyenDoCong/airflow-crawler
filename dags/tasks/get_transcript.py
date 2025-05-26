from airflow.decorators import task
from app.core.database_utils import update_video_status
from app.worker.schema import TaskStatus
import os
import subprocess

def split_audio_ffmpeg(audio_path, chunk_length=30):
    """
    Chia nhỏ file audio thành các file nhỏ hơn bằng ffmpeg.
    Args:
        audio_path (str): Đường dẫn file audio gốc.
        chunk_length (int): Độ dài mỗi đoạn (giây).
    Returns:
        List[str]: Danh sách đường dẫn các file audio nhỏ.
    """
    output_dir = os.path.dirname(audio_path)
    base_name = os.path.splitext(os.path.basename(audio_path))[0]
    output_pattern = os.path.join(output_dir, f"{base_name}_chunk_%03d.wav")
    cmd = [
        "ffmpeg",
        "-i", audio_path,
        "-f", "segment",
        "-segment_time", str(chunk_length),
        "-c", "copy",
        output_pattern
    ]
    subprocess.run(cmd, check=True)
    # Lấy danh sách file đã tạo
    chunk_files = sorted([
        os.path.join(output_dir, f)
        for f in os.listdir(output_dir)
        if f.startswith(f"{base_name}_chunk_") and f.endswith(".wav")
    ])
    return chunk_files

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
    # task_ids = context.get("task_ids", f"{platform}_videos_scraper_task")

    ti = context["ti"]
    downloads = ti.xcom_pull(task_ids="batch_download_task")
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
                model = WhisperModel(model_size, device="cpu", compute_type="int8")
                
                # Remove this block (transcribes the whole file, not needed)
                # segments, info = model.transcribe(audio_path, beam_size=5)
                # logging.info(f"Detected language '{info.language}' with probability {info.language_probability}")

                # Only split and transcribe chunks
                chunk_files = split_audio_ffmpeg(audio_path, chunk_length=30)
                transcription = ""
                for chunk_file in chunk_files:
                    segments, info = model.transcribe(chunk_file, beam_size=5)
                    for segment in segments:
                        text = segment.text.strip()
                        transcription += text + " "

                update_video_status(id,
                                    TaskStatus.SUCCESS.value,
                                    transcript=transcription.strip(),
                                    platform=platform)
            except Exception as e:
                logging.info(f"Video has no sound {id}: {str(e)}")
                update_video_status(id,
                                    TaskStatus.SUCCESS.value,
                                    platform=platform,
                                    logs=f"Video has no sound: {str(e)}")


