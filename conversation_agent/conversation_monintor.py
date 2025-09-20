import json
from datetime import datetime


class ConversationMonitor:
    def __init__(self, therapist=None):
        self.therapist = therapist
        self.conversation_log = self.therapist.log_file if therapist else None
        self.set_limits()
        self.set_alerts()

    def set_limits(self, time_limit=None, message_limit=None, token_limit=None, flag_range=0.2):
        self.time_limit = time_limit
        self.message_limit = message_limit
        self.token_limit = token_limit
        self.flag_range = flag_range
        
        self.token_count = 0
        self.message_count = 0
        self.start_time = None

    def set_alerts(self):
        self.final_lap = False
        self.end_flag = False

    def read(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    yield entry
                except json.JSONDecodeError as e:
                    print(f"Skipping malformed line: {e}")

    def read_log(self):
        count_msg = 0
        for entry in self.read(self.conversation_log):
            role = entry.get("role")
            timestamp = entry.get("timestamp")
            details = entry.get("details")

            if role == "Human":
                count_msg += 1

            if self.start_time is None:
                self.start_time = timestamp
        
        self.message_count = count_msg


    def update_alerts(self):
        if self.message_limit and (self.message_limit - self.message_count) <= (self.flag_range * self.message_limit):
            if not self.final_lap:
                print(f"Final lap: Approaching message limit of {self.message_limit}. Current count: {self.message_count}")
                self.final_lap = True
        if self.message_limit and self.message_count >= self.message_limit:
            print(f"Message limit of {self.message_limit} reached. Ending session.")
            self.end_flag = True

        if self.token_limit and (self.token_limit - self.token_count) <= (self.flag_range * self.token_limit):
            if not self.final_lap:
                print(f"Final lap: Approaching token limit of {self.token_limit}. Current count: {self.token_count}")
                self.final_lap = True
        if self.token_limit and self.token_count >= self.token_limit:
            print(f"Token limit of {self.token_limit} reached. Ending session.")
            self.end_flag = True

        if self.time_limit and self.start_time:
            elapsed_time = (datetime.now() - datetime.fromisoformat(self.start_time)).total_seconds() / 60
            if (self.time_limit - elapsed_time) <= (self.flag_range * self.time_limit):
                if not self.final_lap:
                    print(f"Final lap: Approaching time limit of {self.time_limit} minutes. Elapsed time: {elapsed_time:.2f} minutes")
                    self.final_lap = True
            if elapsed_time >= self.time_limit:
                print(f"Time limit of {self.time_limit} minutes reached. Ending session.")
                self.end_flag = True



    def routine(self):
        self.read_log()
        self.update_alerts()

