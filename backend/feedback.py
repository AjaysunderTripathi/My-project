import os
import datetime
import json

FEEDBACK_FILE = '/tmp/feedback.json'

def save_feedback(user_id, data):
    feedback = {
        'user_id': user_id,
        'message': data.get('message'),
        'response': data.get('response'),
        'rating': data.get('rating'),
        'flag': data.get('flag'),
        'timestamp': datetime.datetime.now().isoformat()
    }
    if os.path.exists(FEEDBACK_FILE):
        with open(FEEDBACK_FILE, 'r', encoding='utf-8') as f:
            all_feedback = json.load(f)
    else:
        all_feedback = []
    all_feedback.append(feedback)
    with open(FEEDBACK_FILE, 'w', encoding='utf-8') as f:
        json.dump(all_feedback, f, ensure_ascii=False, indent=2)
    return {'message': 'Feedback saved'}
