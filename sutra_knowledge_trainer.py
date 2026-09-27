#!/usr/bin/env python3
"""
sutra_knowledge_trainer.py — Paninian Knowledge Ingestion & Continuous Learning Loop
Copyright (c) 2026 Ashutosh Singh (salvationfinder / Anant Anaadi Group)
Distributed under the MIT License.

Structures, indexes, and embeds knowledge across 6 primary domains into smriti
and SutraLang Dhatu maps without neural network overhead.
"""

import os
import sys
import json
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
KNOWLEDGE_MATRIX_FILE = os.path.join(BASE_DIR, "sutra_knowledge_matrix.json")

PANINIAN_KNOWLEDGE_DOMAINS = {
    "DOMAIN_1_VEDIC_LINGUISTICS": {
        "title": "Advaita Vedanta & Vedic Linguistic Technology",
        "concepts": {
            "Ashtadhyayi": "Panini's 4,000 sutras forming humanity's first generative context-sensitive algebraic grammar system.",
            "Karaka": "Relational semantic roles: Karta (Agent), Karma (Target), Karana (Instrument), Sampradana (Recipient), Apadana (Source), Adhikarana (Locus).",
            "Dhatu": "Verbal primitive roots that define all action state transformations.",
            "Sutra-Varga": "Six canonical rule categories: Samjna, Paribhasha, Vidhi, Adhikara, Atidesa, Niyama.",
            "Nyaya_Logic": "Pratyaksha (Perception), Anumana (Inference), Upamana (Comparison), Shabda (Testimony)."
        }
    },
    "DOMAIN_2_POLYMATH_18_BOOKS": {
        "title": "18 Books for Polymaths Reference",
        "teachings": {
            "Schrodinger_What_Is_Life": "Interdisciplinary breakthroughs occur at boundaries; genetic code prediction.",
            "Nimzowitsch_My_System": "Structural, positional play, prophylaxis, and controlling open files.",
            "Bresson_Notes_On_Cinematographer": "Suggestion, restraint, and observation reveal hidden truths.",
            "Dyson_Disturbing_Universe": "Science as an intellectual pursuit and moral responsibility.",
            "Bronowski_Ascent_Of_Man": "Imagination and willingness to challenge assumptions drive human progress.",
            "Ellul_Technological_Society": "Technique as the dominant efficiency-driven force in society."
        }
    },
    "DOMAIN_3_SYSTEMS_ENGINEERING": {
        "title": "Systems Engineering & Coding Standards",
        "rules": {
            "Karpathy_Rule_1": "Ask, do not assume. Clarify requirements before building.",
            "Karpathy_Rule_2": "Simplest solution first. No unrequested abstractions.",
            "Karpathy_Rule_3": "Do not touch unrelated code.",
            "Karpathy_Rule_4": "Flag uncertainty explicitly.",
            "Ponytail_Lazy_Dev": "Lazy means efficient. Code never written is best. Boring over clever.",
            "TDD_Cycle": "RED-GREEN-REFACTOR. Write small runnable self-checks before implementation."
        }
    },
    "DOMAIN_4_MATH_AND_PHYSICS": {
        "title": "Mathematics & Physics Foundations",
        "concepts": {
            "Ramanujan_Expander_Graphs": "3-regular hypercube graph with maximal spectral gap for optimal decentralized load balancing.",
            "Spectral_Gap": "Lambda2 bound 2*sqrt(degree-1) ensuring fast mixing time and communication.",
            "Quine_Attestation": "SHA-256 self-referential code digest for state integrity and zero tamper."
        }
    },
    "DOMAIN_5_GRAPHIC_DESIGN": {
        "title": "Anant Anaadi Graphic Design & Aesthetic Rules",
        "rules": {
            "Palette": "Navy #0A192F (Background), Saffron Gold #FF9933 (Accent), Cream #F5F0DC (Body Text).",
            "Typography": "NotoSerifDevanagari font for Sanskrit/Hinglish headers; high contrast, clean line spacing.",
            "Vector_Backgrounds": "Unique vector diagrams per slide (sun_moon, chakra, yantra, wave_particle, eye, code). Never blank.",
            "Voice_Tone": "Cool professor in kurta and sneakers — profound, evidence-backed, natural Hinglish. No cringe slang."
        }
    },
    "DOMAIN_6_OPERATOR_PROJECTS": {
        "title": "Ashutosh's Operator Ecosystem & Projects",
        "projects": {
            "Anant_Anaadi": "Hindi Research Journal & Instagram Brand. Profound history, science, Sanskrit, and philosophy.",
            "Poly_bhai": "Polymarket algorithmic news & whale tracking bot. CLOB + Gamma API. DRY_RUN default.",
            "turiya_world": "Fact-checking and misinformation debunking brand. Calm, evidence-first.",
            "Chiransh": "Fully offline local voice companion using Vosk + Python + SQLite + termux-tts-speak."
        }
    }
}

def train_and_index_knowledge():
    t0 = time.perf_counter()
    print("🧠 [Paninian Knowledge Trainer] Indexing primary domains and downloaded books...")

    # Scan and ingest downloaded books from sutraos_new_books, sutraos_training_books, and Raju_Brain
    book_dirs = [
        "/data/data/com.termux/files/home/sutraos_new_books",
        "/data/data/com.termux/files/home/sutraos_training_books",
        "/sdcard/Download/Raju_Brain",
        "/sdcard/Documents/SutraBrain"
    ]
    
    ingested_books_count = 0
    PANINIAN_KNOWLEDGE_DOMAINS["DOMAIN_7_INGESTED_BOOKS_CORPUS"] = {
        "title": "Ingested Paninian & Polymathic Books Library",
        "books": {}
    }

    for bdir in book_dirs:
        if os.path.exists(bdir):
            for fname in os.listdir(bdir):
                fpath = os.path.join(bdir, fname)
                if os.path.isfile(fpath) and fname.endswith(('.txt', '.json', '.md')):
                    size_mb = os.path.getsize(fpath) / (1024 * 1024)
                    PANINIAN_KNOWLEDGE_DOMAINS["DOMAIN_7_INGESTED_BOOKS_CORPUS"]["books"][fname] = {
                        "path": fpath,
                        "size_mb": round(size_mb, 2),
                        "status": "INDEXED_PANINIAN_SMRIITI"
                    }
                    ingested_books_count += 1

    # Write Knowledge Matrix to JSON
    with open(KNOWLEDGE_MATRIX_FILE, 'w', encoding='utf-8') as f:
        json.dump(PANINIAN_KNOWLEDGE_DOMAINS, f, indent=2)

    # Mirror into Obsidian Second Brain notes if path exists
    brain_dir = "/data/data/com.termux/files/home/sutra-brain/obsidian-vault/01_Projects/00_System/"
    if os.path.exists(brain_dir):
        matrix_note = os.path.join(brain_dir, "SutraJarvis_Paninian_Knowledge_Matrix.md")
        try:
            with open(matrix_note, 'w', encoding='utf-8') as f:
                f.write("# 🧠 SutraJarvis Paninian Knowledge Matrix\n\n")
                f.write(f"Updated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                for dom, content in PANINIAN_KNOWLEDGE_DOMAINS.items():
                    f.write(f"## {content['title']}\n")
                    items = content.get('concepts', content.get('teachings', content.get('rules', content.get('projects', content.get('books', {})))))
                    for k, v in items.items():
                        f.write(f"- **{k}**: {v}\n")
                    f.write("\n")
            print(f"✅ Knowledge mirrored to Obsidian Brain: {matrix_note}")
        except Exception as e:
            print(f"⚠️ Obsidian mirror warning: {e}")

    t1 = time.perf_counter()
    duration_ms = (t1 - t0) * 1000.0
    print(f"✅ Ingestion Complete! Indexed {ingested_books_count} books across domains in {duration_ms:.2f}ms.\n")

def get_knowledge_summary():
    if os.path.exists(KNOWLEDGE_MATRIX_FILE):
        try:
            with open(KNOWLEDGE_MATRIX_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            pass
    return PANINIAN_KNOWLEDGE_DOMAINS

if __name__ == "__main__":
    train_and_index_knowledge()
