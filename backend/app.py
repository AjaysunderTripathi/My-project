from flask import Flask, request, jsonify, session
from werkzeug.utils import secure_filename
import os

from rag_pipeline import process_pdf_and_index, answer_with_rag
from translation import detect_and_translate_in, translate_out
from intent_manager import update_context, get_context
from fallback_handler import check_fallback
from logging_handler import log_conversation
from auth import login_required, get_user_type
from feedback import save_feedback
from admin_dashboard import get_logs, get_flagged, update_flag

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change for production

UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ✅ Health check / root route
@app.route("/", methods=['GET'])
def home():
    return jsonify({"status": "Backend is running 🚀"}), 200

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    file = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    num_chunks = process_pdf_and_index(filepath)
    return jsonify({'message': 'PDF processed and indexed', 'chunks': num_chunks})

@app.route('/login', methods=['POST'])
def login():
    # Simple login endpoint (username/password in JSON)
    from auth import login_user
    data = request.json
    return login_user(data)

@app.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.json
    user_input = data.get('message', '')
    user_id = session.get('user_id', 'default')

    # Multilingual: detect and translate input to English
    lang, user_input_en = detect_and_translate_in(user_input)

    # Context management
    context = update_context(user_id, user_input)

    # RAG: get answer and confidence
    answer, confidence, retrieved = answer_with_rag(user_input_en, context)

    # Fallback to human if needed
    fallback, fallback_msg = check_fallback(answer, confidence)
    if fallback:
        answer = fallback_msg

    # Translate answer back to user's language if needed
    answer_out = translate_out(answer, lang)

    # Log conversation
    log_conversation(user_id, user_input, lang, answer_out, context, fallback)

    user_type = get_user_type(session.get('user_id', 'default'))
    # Response based on user type
    if user_type == 'admin':
        answer_out = f"[ADMIN MODE] {answer_out}"
    elif user_type == 'volunteer':
        answer_out = f"[VOLUNTEER MODE] {answer_out}"

    return jsonify({
        'response': answer_out,
        'context': get_context(user_id),
        'language': lang,
        'fallback': fallback,
        'user_type': user_type
    })

@app.route('/feedback', methods=['POST'])
@login_required
def feedback():
    data = request.json
    user_id = session.get('user_id', 'default')
    return save_feedback(user_id, data)

@app.route('/admin/logs', methods=['GET'])
@login_required
def admin_logs():
    if get_user_type(session.get('user_id')) != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(get_logs())

@app.route('/admin/flagged', methods=['GET'])
@login_required
def admin_flagged():
    if get_user_type(session.get('user_id')) != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    return jsonify(get_flagged())

@app.route('/admin/flag', methods=['POST'])
@login_required
def admin_flag():
    if get_user_type(session.get('user_id')) != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.json
    return update_flag(data)

@app.route('/privacy', methods=['GET'])
def privacy():
    with open(os.path.join(os.path.dirname(__file__), 'privacy_policy.txt'), 'r', encoding='utf-8') as f:
        policy = f.read()
    return jsonify({'privacy_policy': policy})

if __name__ == '__main__':
    app.run(debug=True)
