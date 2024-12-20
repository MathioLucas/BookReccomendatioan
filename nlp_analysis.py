import spacy
from textblob import TextBlob
from collections import Counter

# Load spaCy's language model
nlp = spacy.load("en_core_web_sm")

def analyze_text_tone_and_style(sample_text):
    """
    Analyze the tone, style, and keywords of a given text.

    Args:
        sample_text (str): The text to analyze.

    Returns:
        dict: Analysis results including tone, style, and keywords.
    """
    # Analyze tone using TextBlob (polarity)
    blob = TextBlob(sample_text)
    tone = "Neutral"
    if blob.sentiment.polarity > 0.1:
        tone = "Positive"
    elif blob.sentiment.polarity < -0.1:
        tone = "Negative"

    # Analyze style and extract keywords using spaCy
    doc = nlp(sample_text)
    word_frequencies = Counter(token.text.lower() for token in doc if token.is_alpha and not token.is_stop)
    most_common_keywords = [word for word, _ in word_frequencies.most_common(10)]

    # Identify literary style based on sentence patterns
    style = "Unknown"
    sentence_count = len(list(doc.sents))
    if sentence_count < 5:
        style = "Concise"
    elif sentence_count > 15:
        style = "Expansive"

    return {
        "tone": tone,
        "style": style,
        "keywords": most_common_keywords
    }

if __name__ == "__main__":
    # Example input
    sample_text = (
        "Once upon a time, in a faraway kingdom, there lived a kind and noble king. "
        "His reign was marked by peace and prosperity. However, dark clouds loomed "
        "on the horizon as the neighboring lands grew restless."
    )

    # Analyze the sample text
    analysis_results = analyze_text_tone_and_style(sample_text)

    print("Analysis Results:")
    for key, value in analysis_results.items():
        print(f"{key.capitalize()}: {value}")
