def check_fallback(answer, confidence, threshold=0.4):
    if not answer.strip() or (confidence is not None and confidence < threshold):
        return True, "I'm not confident about the answer. Please contact a human staff member for further assistance."
    return False, ""
