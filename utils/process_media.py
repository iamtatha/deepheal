import os
import datetime
import asyncio
from moviepy import AudioFileClip
from moviepy import VideoFileClip
import whisper


def process_media():
    parent_folder_path = "media/"
    output_path = "media/processed/"

    if not os.path.exists(output_path):
        os.makedirs(output_path)

    print(f"Processing media in {parent_folder_path}, saving to {output_path}")

    # await asyncio.gather(
    #     process_audio(parent_folder_path, output_path),
    #     process_video(parent_folder_path, output_path)
    # )

    file_aud = process_audio(parent_folder_path, output_path)
    file_vid = process_video(parent_folder_path, output_path)
    return file_aud, file_vid

def process_audio(parent_folder_path, output_path):
    folder_path = f"{parent_folder_path}/audio"
    webm_files = [f for f in os.listdir(folder_path) if f.endswith(".webm")]
    
    if not webm_files:
        print("No .webm files found!")
        return

    webm_files.sort() 
    latest_file = webm_files[-1]

    latest_file_path = os.path.join(folder_path, latest_file)

    processed_files = [f for f in os.listdir(output_path)]
    num = len(processed_files)//2 + 1
    output_file = f"{output_path}/audio{num}.mp3"

    audio_clip = AudioFileClip(latest_file_path)
    audio_clip.write_audiofile(output_file)
    audio_clip.close()

    return output_file


def audio_to_text(file):
    model = whisper.load_model("base")
    result = model.transcribe(file)
    text = result["text"].strip()
    return text



def process_video(parent_folder_path, output_path):
    folder_path = f"{parent_folder_path}/video"
    webm_files = [f for f in os.listdir(folder_path) if f.endswith(".webm")]
    # print(f"Found {len(webm_files)} .webm files.")
    
    if not webm_files:
        print("No .webm files found!")
        return

    webm_files.sort() 
    latest_file = webm_files[-1]

    latest_file_path = os.path.join(folder_path, latest_file)

    processed_files = [f for f in os.listdir(output_path)]
    num = len(processed_files)//2 + 1
    output_file = f"{output_path}/video{num}.mp4"

    clip = VideoFileClip(latest_file_path)
    clip.write_videofile(output_file, codec="libx264", audio_codec="aac")

    return output_file
