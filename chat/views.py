from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import json
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from conversation_agent.fetch_disorders import Fetcher
from conversation_agent.therapist_agent import Therapist

isAssistant = os.getenv("THERAPIST_ASSISTANT", "False").lower() in ("true", "1", "t")
mock = os.getenv("MOCK_MODE", "True").lower() in ("true", "1", "t")

fetcher = Fetcher()


therapist = Therapist(model_type="openai", fetcher=fetcher, isAssistant=isAssistant, mock=mock)
log_file_name = f"{therapist.log_file}"
LOG_FILE = Path(settings.BASE_DIR) / log_file_name  # adjust filename

print(f"Log file path: {LOG_FILE}")


def chat_page(request):
    return render(request, "chat/chat.html")


@csrf_exempt
def chat_api(request):
    if request.method == "POST":
        data = json.loads(request.body.decode("utf-8"))
        print(f"\nGot Chat Request with Message: {data}\n")

        user_message = data.get("message", "")
        if user_message.strip() == "START":
            print(f"Initial message from the user")
            ai_reply = therapist.proactive_start()
            print(f"AI Reply: {ai_reply}")
            return JsonResponse({"reply": ai_reply})
        
        ai_reply = therapist.ask(user_message)
        print(f"AI Reply: {ai_reply}")
        return JsonResponse({"reply": ai_reply})
    return JsonResponse({"error": "Only POST allowed"}, status=400)



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
