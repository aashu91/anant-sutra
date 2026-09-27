# sutra_book_synthesizer.py — Paninian 615-Book Knowledge & Conversational Synthesizer
# Copyright (c) 2026 Ashutosh Singh (salvationfinder / Anant Anaadi Group)
# Distributed under the MIT License.

import os
import sys
import json
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MATRIX_FILE = os.path.join(BASE_DIR, "sutra_knowledge_matrix.json")

def load_matrix():
    if os.path.exists(MATRIX_FILE):
        try:
            with open(MATRIX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return {}

def search_615_books(query: str, top_k: int = 3) -> list:
    """Searches across all 615 ingested books on disk for query keywords."""
    matrix = load_matrix()
    books = matrix.get("DOMAIN_7_INGESTED_BOOKS_CORPUS", {}).get("books", {})
    if not books:
        return []

    stop_words = {"the", "a", "an", "is", "are", "and", "or", "in", "on", "at", "to", "for", "of", "with", "kya", "hai", "kaise", "batao", "bhai", "ko"}
    words = [w.lower() for w in re.split(r'\W+', query) if len(w) > 2 and w.lower() not in stop_words]
    if not words:
        return []

    results = []
    for bk_title, info in books.items():
        if isinstance(info, dict) and "path" in info:
            fpath = info["path"]
            if os.path.exists(fpath):
                try:
                    with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
                        text = f.read(50000) # Read first 50KB for fast indexing
                    c_lower = text.lower()
                    score = sum(c_lower.count(w) * (2 if w in bk_title.lower() else 1) for w in words)
                    if score > 0:
                        results.append({"title": bk_title, "score": score, "path": fpath, "text": text})
                except Exception:
                    continue

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:top_k]

def search_primary_domains(query: str) -> list:
    """Searches across primary Paninian, Polymath, and Systems Engineering domains."""
    matrix = load_matrix()
    insights = []
    q_lower = query.lower()

    for dom_key, dom_data in matrix.items():
        if dom_key == "DOMAIN_7_INGESTED_BOOKS_CORPUS":
            continue
        title = dom_data.get("title", "")
        for sub_k in ["concepts", "teachings", "rules", "projects"]:
            sub_dict = dom_data.get(sub_k, {})
            for k, val in sub_dict.items():
                if any(w in k.lower() or w in str(val).lower() for w in q_lower.split() if len(w) > 3):
                    insights.append(f"{k}: {val}")

    return insights[:5]

def synthesize_conversational_response(user_query: str) -> str:
    """
    Synthesizes a fluid, articulate, human-like response infused with 615-book knowledge
    in the authentic 'Cool professor in kurta & sneakers' voice.
    """
    book_matches = search_615_books(user_query, top_k=3)
    domain_insights = search_primary_domains(user_query)

    if not book_matches and not domain_insights:
        return f"Main 615-books corpus se '{user_query}' explore kar raha hoon. Paninian logic & systems perspective se yeh ek profound topic hai — batao isme kis angle (Linguistics, Cybernetics, ya Philosophy) par discuss karein?"

    extracted_snippets = []
    book_titles = []

    for item in book_matches:
        b_name = item["title"].replace(".txt", "").replace("_", " ").title()
        book_titles.append(b_name)
        # Extract clean 1-2 sentences containing query terms
        sentences = re.split(r'(?<=[.!?])\s+', item["text"][:3000])
        matching_sents = [s.strip() for s in sentences if len(s.strip()) > 20 and any(w in s.lower() for w in user_query.lower().split() if len(w) > 3)]
        if matching_sents:
            extracted_snippets.append(matching_sents[0])

    response_parts = []
    
    if domain_insights:
        primary_ref = domain_insights[0]
        response_parts.append(f"📚 {primary_ref}")

    if extracted_snippets:
        clean_text = " ".join(extracted_snippets[:2])
        response_parts.append(f"📖 Ingested Corpus Insight ({', '.join(book_titles[:2])}):\n\"{clean_text}\"")

    if not response_parts:
        response_parts.append(f"📚 {book_titles[0]} corpus se link establish ho gaya hai.")

    return "\n\n".join(response_parts)

if __name__ == "__main__":
    print("Testing SutraOS 615-Book Synthesizer...")
    res = synthesize_conversational_response("Mind and cognition in psychology and linguistics")
    print(res)
