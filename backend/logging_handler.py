import os
import datetime

LOGS_DIR = '/tmp/conversation_logs'
os.makedirs(LOGS_DIR, exist_ok=True)

def log_conversation(user_id, user_input, lang, response, context, fallback):
    date_str = datetime.datetime.now().strftime('%Y-%m-%d')
    log_file = os.path.join(LOGS_DIR, f'log_{date_str}.txt')
    with open(log_file, 'a', encoding='utf-8') as f:
        f.write(f"User ({user_id}, {lang}): {user_input}\n")
        f.write(f"Bot: {response}\n")
        f.write(f"Context: {context}\n")
        f.write(f"Fallback: {fallback}\n")
        f.write("="*40 + "\n")
