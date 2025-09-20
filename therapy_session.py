from conversation_agent.fetch_disorders import Fetcher
from conversation_agent.therapist_agent import Therapist
from conversation_agent.conversation_monintor import ConversationMonitor


fetcher = Fetcher()
therapist = Therapist(model_type="openai", fetcher=fetcher, isAssistant=True)
monitor = ConversationMonitor(therapist=therapist)
monitor.set_limits(
    time_limit=5, 
    message_limit=None, 
    token_limit=None,
)

while True:
    query = input("Type: ")
    
    if query == "Q":
        break

    response = therapist.ask(query)
    print(f"AI: {response}\n")
