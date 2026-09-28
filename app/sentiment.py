import re

# Comprehensive lexicon of positive words
POSITIVE_WORDS = {
    'excellent', 'amazing', 'great', 'good', 'love', 'loved', 'fantastic',
    'outstanding', 'superb', 'best', 'wonderful', 'perfect', 'flawless',
    'fast', 'smooth', 'prompt', 'helpful', 'friendly', 'polite', 'courteous',
    'satisfied', 'happy', 'pleased', 'impressive', 'impressed', 'reliable',
    'recommend', 'recommended', 'awesome', 'brilliant', 'clean', 'neat',
    'efficient', 'responsive', 'quality', 'valuable', 'exceptional', 'easy',
    'intuitive', 'quick', 'effective', 'pleasant', 'delighted', 'top-notch'
}

# Comprehensive lexicon of negative words
NEGATIVE_WORDS = {
    'terrible', 'horrible', 'bad', 'poor', 'slow', 'worst', 'awful',
    'rude', 'broken', 'defect', 'defective', 'disappointed', 'disappointing',
    'unhelpful', 'unprofessional', 'frustrating', 'frustrated', 'useless',
    'trash', 'waste', 'buggy', 'crash', 'crashing', 'error', 'failed',
    'failure', 'late', 'delayed', 'delay', 'hate', 'hated', 'annoying',
    'difficult', 'complicated', 'pathetic', 'issue', 'problem', 'garbage',
    'unacceptable', 'regret', 'unhappy', 'dissatisfied', 'mess', 'damaged'
}

# Negation words that flip polarity of subsequent words
NEGATION_WORDS = {
    'not', 'no', 'never', 'hardly', 'barely', 'scarcely', 'without',
    "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't",
    "hadn't", "won't", "wouldn't", "don't", "doesn't", "didn't",
    "can't", "couldn't", "shouldn't", 'neither', 'nor'
}

# Intensifiers that boost the sentiment magnitude
INTENSIFIERS = {
    'very': 1.5,
    'extremely': 1.8,
    'super': 1.6,
    'highly': 1.5,
    'really': 1.4,
    'deeply': 1.5,
    'absolutely': 1.7,
    'truly': 1.4,
    'completely': 1.5,
    'exceptionally': 1.7
}

def analyze_sentiment(text, rating=None):
    """
    Analyzes sentiment of customer feedback using a hybrid approach:
    1. Lexicon-based keyword matching with negation handling & intensifiers.
    2. Optional rating weighting (1 to 5 stars) to produce a calibrated compound score.

    Returns:
        dict: {
            'sentiment': 'Positive' | 'Neutral' | 'Negative',
            'score': float (-1.0 to 1.0),
            'positive_keywords': list of matched positive words,
            'negative_keywords': list of matched negative words,
            'explanation': descriptive explanation of why this sentiment was chosen
        }
    """
    if not text:
        text = ""

    # Clean and tokenize words
    cleaned_text = re.sub(r'[^\w\s\']', ' ', text.lower())
    tokens = cleaned_text.split()

    pos_found = []
    neg_found = []
    text_score = 0.0

    i = 0
    while i < len(tokens):
        word = tokens[i]
        intensifier_mult = 1.0

        # Check if preceding token was an intensifier
        if i > 0 and tokens[i - 1] in INTENSIFIERS:
            intensifier_mult = INTENSIFIERS[tokens[i - 1]]

        # Check for negation in the previous 2 words (e.g., "not very good", "not good")
        is_negated = False
        if i > 0 and tokens[i - 1] in NEGATION_WORDS:
            is_negated = True
        elif i > 1 and tokens[i - 2] in NEGATION_WORDS:
            is_negated = True

        if word in POSITIVE_WORDS:
            if is_negated:
                # "not good" -> counted as negative
                neg_found.append(f"not {word}")
                text_score -= (1.0 * intensifier_mult)
            else:
                pos_found.append(word)
                text_score += (1.0 * intensifier_mult)

        elif word in NEGATIVE_WORDS:
            if is_negated:
                # "not bad" -> counted as mildly positive / neutral
                pos_found.append(f"not {word}")
                text_score += (0.5 * intensifier_mult)
            else:
                neg_found.append(word)
                text_score -= (1.0 * intensifier_mult)

        i += 1

    # Normalize text score to range [-1.0, 1.0]
    total_matches = len(pos_found) + len(neg_found)
    if total_matches > 0:
        normalized_text_score = max(-1.0, min(1.0, text_score / total_matches))
    else:
        normalized_text_score = 0.0

    # Rating factor normalization (-1.0 for 1 star, 0.0 for 3 stars, +1.0 for 5 stars)
    if rating is not None and 1 <= rating <= 5:
        rating_score = (rating - 3) / 2.0  # 1->-1.0, 2->-0.5, 3->0.0, 4->0.5, 5->1.0

        if total_matches > 0:
            # Combined weighted score: 65% text semantics, 35% star rating
            compound_score = (0.65 * normalized_text_score) + (0.35 * rating_score)
        else:
            # If text has no strong sentiment keywords, rely directly on the star rating
            compound_score = rating_score
    else:
        compound_score = normalized_text_score

    # Determine classification label
    if compound_score >= 0.20:
        sentiment = 'Positive'
    elif compound_score <= -0.20:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'

    # Build student/examiner friendly explanation
    explanation_parts = []
    if pos_found:
        explanation_parts.append(f"Positive signals detected: {', '.join(set(pos_found))}")
    if neg_found:
        explanation_parts.append(f"Negative signals detected: {', '.join(set(neg_found))}")
    if not pos_found and not neg_found:
        explanation_parts.append("No explicit polarity keywords detected in text.")
    if rating:
        explanation_parts.append(f"Customer assigned a {rating}-star rating.")

    explanation_parts.append(f"Calibrated compound score: {compound_score:+.2f} ({sentiment}).")
    explanation = " | ".join(explanation_parts)

    return {
        'sentiment': sentiment,
        'score': round(compound_score, 2),
        'positive_keywords': list(set(pos_found)),
        'negative_keywords': list(set(neg_found)),
        'explanation': explanation
    }
