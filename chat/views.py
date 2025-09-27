from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
from pathlib import Path
import tempfile
import datetime
from dotenv import load_dotenv
load_dotenv()

from conversation_agent.fetch_disorders import Fetcher
from conversation_agent.therapist_agent import Therapist
from utils.process_media import process_media,audio_to_text

isAssistant = os.getenv("THERAPIST_ASSISTANT", "False").lower() in ("true", "1", "t")
mock = os.getenv("MOCK_MODE", "True").lower() in ("true", "1", "t")

fetcher = Fetcher()


therapist = Therapist(model_type="openai", fetcher=fetcher, isAssistant=isAssistant, mock=mock)
log_file_name = f"{therapist.log_file}"
LOG_FILE = Path(settings.BASE_DIR) / log_file_name  # adjust filename

print(f"Log file path: {LOG_FILE}")


MEDIA_DIR = Path(settings.BASE_DIR) / "media"
AUDIO_DIR = MEDIA_DIR / "audio"
VIDEO_DIR = MEDIA_DIR / "video"
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
VIDEO_DIR.mkdir(parents=True, exist_ok=True)

def chat_page(request):
    return render(request, "chat/chat.html")

@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        # Check if it's a file upload
        if request.FILES:
            user_message = request.POST.get("message", "")
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")

            # Save uploaded audio/video
            audio_file = request.FILES.get("audio")
            video_file = request.FILES.get("video")

            if audio_file:
                audio_path = AUDIO_DIR / f"{timestamp}_audio.webm"
                with open(audio_path, "wb") as f:
                    for chunk in audio_file.chunks():
                        f.write(chunk)

            if video_file:
                video_path = VIDEO_DIR / f"{timestamp}_video.webm"
                with open(video_path, "wb") as f:
                    for chunk in video_file.chunks():
                        f.write(chunk)

            aud, vid = process_media()
            text = audio_to_text(aud)
            user_message += f"\n{text}"

        else:
            # If not files, treat as JSON text
            try:
                data = json.loads(request.body.decode("utf-8"))
                user_message = data.get("message", "")
            except Exception as e:
                return JsonResponse({"error": "Invalid request format", "details": str(e)}, status=400)

        # Process the message via AI
        if user_message.strip().upper() == "START":
            ai_reply = therapist.proactive_start()
        else:
            ai_reply = therapist.ask(user_message)

        # asyncio.run(process_media())
        print("Processing media files...")
        return JsonResponse({"transcript": user_message, "reply": ai_reply})

    return JsonResponse({"error": "Only POST allowed"}, status=400)


@csrf_exempt
def process_audio(request):
    """
    Receive audio file from frontend, convert to text, and return AI response
    """
    print("Processing audio request...")
    if request.method == "POST" and request.FILES.get("audio"):
        audio_file = request.FILES["audio"]

        # Save temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
            tmp_path = tmp.name

        # TODO: Use speech-to-text (e.g., OpenAI Whisper or SpeechRecognition)
        user_text = "dummy transcription"  # placeholder

        # Send to AI
        ai_reply = therapist.ask(user_text)

        return JsonResponse({"text": ai_reply})
    
    return JsonResponse({"error": "Only POST with audio file allowed"}, status=400)




def logs_view(request):
    logs = []
    if LOG_FILE.exists():
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    logs.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    continue
    return render(request, "chat/logs.html", {"logs": logs})
