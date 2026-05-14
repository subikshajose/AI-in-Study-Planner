"""
pdf_flashcard.py - PDF Upload & Flashcard MCQ Generator
Extracts text from uploaded PDFs and generates MCQ-style flashcards
using rule-based NLP techniques (no ML/AI API needed).

How it works:
1. Extract raw text from PDF using PyMuPDF (fitz)
2. Split text into meaningful sentences
3. Identify key terms using keyword frequency + capitalization rules
4. Generate fill-in-the-blank / definition MCQs with distractors
5. Return structured flashcard objects
"""

import re
import random
import string
from collections import Counter

# ─── PDF TEXT EXTRACTION ──────────────────────────────────────────────────────

def extract_text_from_pdf(uploaded_file):
    """
    Extract all text from an uploaded PDF file.

    Parameters:
        uploaded_file: Streamlit UploadedFile object

    Returns:
        str: Full extracted text, or error message string
    """
    try:
        import fitz  # PyMuPDF
        import io

        # Read bytes from the uploaded file
        pdf_bytes = uploaded_file.read()
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")

        full_text = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            if text.strip():
                full_text.append(text)

        doc.close()
        combined = "\n".join(full_text)
        return combined.strip()

    except ImportError:
        return "ERROR: PyMuPDF not installed. Run: pip install pymupdf"
    except Exception as e:
        return f"ERROR: Could not read PDF — {str(e)}"


def clean_text(raw_text):
    """
    Clean extracted PDF text:
    - Remove excessive whitespace and line breaks
    - Remove page numbers and headers/footers (simple heuristic)
    - Normalize punctuation
    """
    # Replace multiple newlines with a single space
    text = re.sub(r'\n+', ' ', raw_text)
    # Remove multiple spaces
    text = re.sub(r' +', ' ', text)
    # Remove stray page numbers like "Page 1", "1.", etc. at line boundaries
    text = re.sub(r'\bPage\s+\d+\b', '', text, flags=re.IGNORECASE)
    # Strip
    text = text.strip()
    return text


# ─── TEXT CHUNKING ────────────────────────────────────────────────────────────

def split_into_sentences(text):
    """
    Split text into individual sentences using punctuation rules.
    Filters out very short sentences (< 8 words).
    """
    # Split on . ! ? followed by space and capital letter
    raw_sentences = re.split(r'(?<=[.!?])\s+(?=[A-Z])', text)

    clean_sentences = []
    for s in raw_sentences:
        s = s.strip()
        word_count = len(s.split())
        # Only keep sentences with 8–80 words (meaningful content)
        if 8 <= word_count <= 80:
            clean_sentences.append(s)

    return clean_sentences


def chunk_text(text, chunk_size=500):
    """
    Split large text into smaller chunks for processing.
    Each chunk is roughly chunk_size characters.
    """
    words = text.split()
    chunks = []
    current_chunk = []
    current_len = 0

    for word in words:
        current_chunk.append(word)
        current_len += len(word) + 1
        if current_len >= chunk_size:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_len = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


# ─── KEY TERM EXTRACTION ──────────────────────────────────────────────────────

def extract_key_terms(text, top_n=30):
    """
    Extract important keywords from text using frequency + capitalization rules.

    Rules:
    - Words that appear frequently → likely important
    - Capitalized words (not at sentence start) → likely proper nouns / terms
    - Exclude common stopwords

    Returns:
        list of key term strings
    """
    STOPWORDS = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
        'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
        'should', 'may', 'might', 'shall', 'can', 'need', 'dare', 'ought',
        'used', 'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
        'as', 'into', 'through', 'during', 'before', 'after', 'above', 'below',
        'between', 'out', 'up', 'down', 'and', 'or', 'but', 'if', 'because',
        'so', 'yet', 'both', 'either', 'neither', 'not', 'only', 'also',
        'than', 'then', 'when', 'where', 'which', 'who', 'whom', 'that',
        'this', 'these', 'those', 'it', 'its', 'they', 'them', 'their',
        'he', 'she', 'we', 'you', 'i', 'me', 'my', 'our', 'your', 'his', 'her',
        'what', 'how', 'why', 'all', 'each', 'every', 'any', 'some', 'such',
        'no', 'nor', 'too', 'very', 'just', 'more', 'most', 'other', 'same',
        'there', 'here', 'about', 'against', 'while', 'although', 'however',
    }

    # Tokenize into words (remove punctuation)
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)

    # Count frequency (case-insensitive)
    freq = Counter(w.lower() for w in words if w.lower() not in STOPWORDS)

    # Collect capitalized terms (mid-sentence proper nouns / technical terms)
    sentences = split_into_sentences(text)
    capitalized_terms = set()
    for sent in sentences:
        sent_words = sent.split()
        # Skip the first word (it's always capitalized)
        for word in sent_words[1:]:
            cleaned = word.strip(string.punctuation)
            if cleaned and cleaned[0].isupper() and len(cleaned) > 3:
                capitalized_terms.add(cleaned.lower())

    # Score: frequency * 1.5 if also a capitalized term
    scored = {}
    for term, count in freq.items():
        score = count
        if term in capitalized_terms:
            score *= 1.5
        scored[term] = score

    # Sort by score and return top N
    top_terms = sorted(scored, key=scored.get, reverse=True)[:top_n]
    return top_terms


# ─── FLASHCARD / MCQ GENERATION ──────────────────────────────────────────────

def generate_flashcards(text, num_cards=10):
    """
    Generate MCQ flashcards from extracted text.

    Strategy:
    1. Find sentences that contain key terms
    2. Blank out the key term → this becomes the question
    3. Use other key terms as wrong options (distractors)
    4. Shuffle options

    Parameters:
        text (str): Cleaned text from PDF
        num_cards (int): How many flashcards to generate

    Returns:
        list of dicts: [{'question': ..., 'options': [...], 'answer': ..., 'hint': ...}]
    """
    sentences = split_into_sentences(text)
    key_terms = extract_key_terms(text, top_n=40)

    if not sentences or not key_terms:
        return []

    flashcards = []
    used_terms = set()

    # Shuffle sentences for variety
    random.shuffle(sentences)

    for sentence in sentences:
        if len(flashcards) >= num_cards:
            break

        sentence_lower = sentence.lower()

        # Find which key terms appear in this sentence
        matching_terms = [
            term for term in key_terms
            if term in sentence_lower and term not in used_terms
        ]

        if not matching_terms:
            continue

        # Pick the highest-priority matching term as the answer
        answer_term = matching_terms[0]
        used_terms.add(answer_term)

        # Find the actual cased version in the sentence
        match = re.search(re.escape(answer_term), sentence, re.IGNORECASE)
        if not match:
            continue

        actual_answer = match.group(0)  # Preserve original casing

        # Create question by blanking out the answer term
        question_text = re.sub(
            re.escape(answer_term),
            "________",
            sentence,
            count=1,
            flags=re.IGNORECASE
        )
        question_text = f"Fill in the blank: \"{question_text}\""

        # Generate distractors (wrong options) from other key terms
        distractors = [
            t for t in key_terms
            if t != answer_term and t not in sentence_lower
        ]
        random.shuffle(distractors)
        wrong_options = distractors[:3]  # Pick 3 wrong options

        # Pad if not enough distractors
        fallback_options = ["concept", "theory", "principle", "process", "system"]
        while len(wrong_options) < 3:
            fallback = random.choice(fallback_options)
            if fallback not in wrong_options and fallback != answer_term:
                wrong_options.append(fallback)

        # Build options list and shuffle
        all_options = [actual_answer] + wrong_options
        random.shuffle(all_options)

        # Create a hint from surrounding context
        hint = sentence[:60] + "..." if len(sentence) > 60 else sentence

        flashcards.append({
            "question": question_text,
            "options": all_options,
            "answer": actual_answer,
            "hint": hint,
            "source_sentence": sentence
        })

    return flashcards


def generate_definition_cards(text, num_cards=5):
    """
    Generate definition-style flashcards.
    Finds sentences that look like definitions (contain 'is', 'are', 'refers to', 'defined as').

    Returns:
        list of dicts: [{'term': ..., 'definition': ..., 'options': [...], 'answer': ...}]
    """
    sentences = split_into_sentences(text)
    definition_patterns = [
        r'(.+?)\s+is\s+(?:a|an|the)\s+(.+)',
        r'(.+?)\s+refers to\s+(.+)',
        r'(.+?)\s+is defined as\s+(.+)',
        r'(.+?)\s+means\s+(.+)',
        r'(.+?)\s+are\s+(?:a|an|the)\s+(.+)',
    ]

    definition_cards = []
    key_terms = extract_key_terms(text, top_n=30)

    for sentence in sentences:
        if len(definition_cards) >= num_cards:
            break

        for pattern in definition_patterns:
            match = re.match(pattern, sentence, re.IGNORECASE)
            if match:
                term = match.group(1).strip()
                definition = match.group(2).strip()

                # Validate: term should be short (1–4 words)
                if 1 <= len(term.split()) <= 4 and len(definition) > 15:
                    # Create MCQ: "Which term matches this definition?"
                    distractors = [t for t in key_terms if t.lower() != term.lower()]
                    random.shuffle(distractors)
                    wrong_opts = distractors[:3]

                    all_options = [term] + wrong_opts
                    random.shuffle(all_options)

                    definition_cards.append({
                        "question": f"Which term is defined as: \"{definition[:120]}...\"?" if len(definition) > 120 else f"Which term is defined as: \"{definition}\"?",
                        "options": all_options,
                        "answer": term,
                        "hint": f"Look for this in the section about: {sentence[:50]}...",
                        "type": "definition"
                    })
                    break  # Move to next sentence after one match

    return definition_cards


def get_text_stats(text):
    """
    Return basic statistics about the extracted text.
    Useful to show the user what was extracted.
    """
    sentences = split_into_sentences(text)
    words = text.split()
    key_terms = extract_key_terms(text, top_n=10)

    return {
        "total_characters": len(text),
        "total_words": len(words),
        "total_sentences": len(sentences),
        "estimated_pages": max(1, len(words) // 250),  # ~250 words/page
        "top_keywords": key_terms,
        "reading_time_minutes": max(1, len(words) // 200)  # ~200 wpm reading speed
    }