# Example: Intent Classifier Skeleton
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
import pandas as pd
import joblib
import PyPDF2
import os

# Load your labeled data
data = pd.read_csv('faq_intents.csv')  # columns: question, intent

vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(data['question'])
y = data['intent']

model = LogisticRegression()
model.fit(X, y)

# Save model and vectorizer for later use
joblib.dump(model, 'project_intent_model.pkl')
joblib.dump(vectorizer, 'project_vectorizer.pkl')

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF file."""
    text = ""
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text() or ""
    return text

def curate_faq_from_pdf(pdf_path, output_csv='faq_intents.csv'):
    """
    Extracts Q&A pairs from PDF and appends to the FAQ CSV.
    Assumes questions end with '?' and answers follow.
    """
    text = extract_text_from_pdf(pdf_path)
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    faqs = []
    question, answer = None, ""
    for line in lines:
        if line.endswith('?'):
            if question and answer:
                faqs.append({'question': question, 'intent': 'general'})  # Default intent
            question = line
            answer = ""
        else:
            answer += " " + line
    if question and answer:
        faqs.append({'question': question, 'intent': 'general'})
    # Append to CSV
    if os.path.exists(output_csv):
        df = pd.read_csv(output_csv)
        new_df = pd.DataFrame(faqs)
        df = pd.concat([df, new_df], ignore_index=True)
    else:
        df = pd.DataFrame(faqs)
    df.to_csv(output_csv, index=False)
    print(f"Curated {len(faqs)} Q&A pairs from PDF.")

# Example usage:
# curate_faq_from_pdf('your_uploaded_file.pdf')