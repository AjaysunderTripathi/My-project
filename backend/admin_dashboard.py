import os
import json
import glob

LOGS_DIR = '/tmp/conversation_logs'
FEEDBACK_FILE = '/tmp/feedback.json'

def get_logs():
    logs = []
    for log_file in glob.glob(os.path.join(LOGS_DIR, 'log_*.txt')):
        with open(log_file, 'r', encoding='utf-8') as f:
            logs.append({'file': log_file, 'content': f.read()})
    return logs

def get_flagged():
    if not os.path.exists(FEEDBACK_FILE):
        return []
    with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
        feedback = json.load(f)
    return [fb for fb in feedback if fb.get('flag')]

def update_flag(data):
    if not os.path.exists(FEEDBACK_FILE):
        return {'error': 'No feedback found'}
    with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
        feedback = json.load(f)
    for fb in feedback:
        if fb['timestamp'] == data.get('timestamp'):
            fb['flag'] = data.get('flag')
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(feedback, f, ensure_ascii=False, indent=2)
    return {'message': 'Flag updated'}
