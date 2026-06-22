"""AI-powered question generation from lesson content"""

import json
import re
import spacy
from typing import List, Dict, Optional
from dataclasses import asdict

from .content_chunker import TextChunk


class QuestionGenerationError(Exception):
    """Raised when question generation fails"""
    pass


class QuestionGenerator:
    """Generates MCQ and short-answer questions from lesson content"""

    def __init__(self):
        """Initialize spaCy NLP model"""
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            raise QuestionGenerationError(
                "spaCy model 'en_core_web_sm' not found. "
                "Install with: python -m spacy download en_core_web_sm"
            )

    def extract_key_concepts(self, text: str) -> List[Dict[str, str]]:
        """Extract key concepts (entities and noun phrases); top 10, de-duped."""
        doc = self.nlp(text)
        concepts = []

        for ent in doc.ents:
            concepts.append({"text": ent.text, "type": ent.label_, "source": "entity"})

        for chunk in doc.noun_chunks:
            concepts.append({"text": chunk.text, "type": "NOUN_PHRASE", "source": "noun_chunk"})

        seen = set()
        unique_concepts = []
        for concept in concepts:
            key = concept["text"].lower()
            if key not in seen:
                seen.add(key)
                unique_concepts.append(concept)

        return unique_concepts[:10]

    def generate_fill_blank_questions(self, text: str, num_questions: int = 3) -> List[Dict]:
        """Generate fill-in-the-blank style questions (entity-based)."""
        doc = self.nlp(text)
        questions = []

        for sent in doc.sents:
            if len(questions) >= num_questions:
                break
            entities = [ent.text for ent in sent.ents]
            if not entities:
                continue
            answer = entities[0]
            blank_sent = sent.text.replace(answer, "______", 1)
            questions.append({
                "question_text": blank_sent,
                "question_type": "FILL_BLANK",
                "correct_answer": answer,
                "difficulty": "MEDIUM",
                "source_sentence": sent.text,
            })

        return questions

    # Linking verbs used to split a statement into subject + predicate, e.g.
    # "Photosynthesis is the process by which..." -> ask "What is photosynthesis?"
    _LINKING_VERBS = (" is ", " are ", " was ", " were ")

    # A subject that begins with one of these is not a real concept to ask about
    # ("It is important", "This was the result") -- skip so we never produce a
    # question like "What is it?".
    _PRONOUN_SUBJECTS = {
        "it", "this", "that", "these", "those", "they", "there",
        "he", "she", "we", "you", "i", "here", "its", "their",
        "his", "her", "such", "one", "some", "many", "most",
    }

    # Clause boundaries used to trim a long predicate to a short spoken phrase.
    _CLAUSE_BREAKS = ("; ", ", ", " which ", " that ", " where ",
                      " because ", " so that ", " in order ", " such as ")

    # Words too generic to make a good fill-in-the-blank answer or distractor.
    _STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "of", "to", "in", "on", "at",
        "for", "with", "as", "by", "from", "is", "are", "was", "were", "be",
        "been", "being", "it", "its", "this", "that", "these", "those", "they",
        "them", "their", "there", "here", "he", "she", "we", "you", "i", "his",
        "her", "our", "your", "which", "who", "what", "when", "where", "why",
        "how", "can", "will", "would", "should", "could", "may", "might", "must",
        "has", "have", "had", "do", "does", "did", "not", "no", "all", "any",
        "more", "most", "some", "such", "than", "then", "also", "into", "over",
        "about", "between", "during", "through", "because", "while", "each",
    }

    @staticmethod
    def _truncate(text: str, max_len: int) -> str:
        text = text.strip()
        return text if len(text) <= max_len else text[:max_len].rstrip() + "..."

    def _short_phrase(self, text: str, max_words: int = 12) -> str:
        """Trim text to one short clause so options stay listenable by ear."""
        text = text.strip().rstrip(".")
        low = text.lower()
        cut = len(text)
        for sep in self._CLAUSE_BREAKS:
            i = low.find(sep)
            # Only cut at a clause break if enough words precede it, so we never
            # reduce "the process by which plants make food" to "the process by".
            if i > 0 and i < cut and len(text[:i].split()) >= 4:
                cut = i
        text = text[:cut].strip()
        words = text.split()
        if len(words) > max_words:
            text = " ".join(words[:max_words])
        return text.strip()

    @staticmethod
    def _dedupe(items: List[str]) -> List[str]:
        seen = set()
        out = []
        for it in items:
            key = it.lower().strip()
            if key and key not in seen:
                seen.add(key)
                out.append(it.strip())
        return out

    @staticmethod
    def _pick_length_matched(correct: str, candidates: List[str], n: int, rng) -> List[str]:
        """Pick n distractors whose length is closest to correct (anti-giveaway)."""
        target = len(correct.split())
        pool = [c for c in candidates if c.lower().strip() != correct.lower().strip()]
        rng.shuffle(pool)
        pool.sort(key=lambda c: abs(len(c.split()) - target))
        return pool[:n]

    def _key_terms(self, doc) -> List[str]:
        """Salient short noun phrases / entities used as cloze answers."""
        terms: List[str] = []
        for ent in doc.ents:
            t = ent.text.strip()
            if 1 <= len(t.split()) <= 3 and len(t) >= 3:
                terms.append(t)
        for nc in doc.noun_chunks:
            t = re.sub(
                r"^(the|a|an|this|that|these|those|its|their|his|her)\s+",
                "", nc.text.strip(), flags=re.I,
            ).strip()
            if (t and 1 <= len(t.split()) <= 3 and len(t) >= 3
                    and t.lower() not in self._STOPWORDS):
                terms.append(t)
        return self._dedupe(terms)

    def generate_mcq_questions(self, text: str, num_questions: int = 5) -> List[Dict]:
        """
        Generate content-bound, audio-friendly multiple-choice questions.

        Two types, built only from the lesson's own words: definitions
        ("What is X?") and fill-in-the-blank. Distractors are length-matched to
        the answer and kept short so a blind student can hold all four in memory
        by ear. The old "which of four long sentences is correct?" pattern is
        gone -- it was unanswerable aloud.
        """
        import random

        doc = self.nlp(text)
        sentences = [
            s.text.strip()
            for s in doc.sents
            if 6 <= len(s.text.split()) <= 40
        ]
        if len(sentences) < 2:
            return []

        key_terms = self._key_terms(doc)
        rng = random.Random(hash(text) & 0xFFFFFFFF)

        questions: List[Dict] = []
        used: set = set()

        for sentence in sentences:
            if len(questions) >= num_questions:
                break
            if sentence in used:
                continue
            mcq = self._definition_mcq(sentence, sentences, rng)
            if mcq is not None:
                used.add(sentence)
                questions.append(mcq)

        for sentence in sentences:
            if len(questions) >= num_questions:
                break
            if sentence in used:
                continue
            mcq = self._cloze_mcq(sentence, key_terms, rng)
            if mcq is not None:
                used.add(sentence)
                questions.append(mcq)

        return questions

    def _definition_mcq(self, sentence: str, all_sentences: List[str], rng) -> Optional[Dict]:
        """'X is/are <predicate>' -> 'What is X?'. None if not a clean definition."""
        verb = next((v for v in self._LINKING_VERBS if v in sentence), None)
        if not verb:
            return None

        idx = sentence.index(verb)
        subject = sentence[:idx].strip()
        predicate = sentence[idx + len(verb):].strip().rstrip(".")

        subj_words = subject.split()
        if not subj_words or len(subj_words) > 6:
            return None
        if subj_words[0].lower() in self._PRONOUN_SUBJECTS:
            return None

        correct = self._short_phrase(predicate)
        if len(correct) < 3:
            return None

        candidates = []
        for other in all_sentences:
            if other == sentence:
                continue
            ov = next((v for v in self._LINKING_VERBS if v in other), None)
            if not ov:
                continue
            other_pred = self._short_phrase(
                other[other.index(ov) + len(ov):].strip().rstrip(".")
            )
            if other_pred and other_pred.lower() != correct.lower():
                candidates.append(other_pred)

        distractors = self._pick_length_matched(correct, self._dedupe(candidates), 3, rng)
        if len(distractors) < 3:
            return None

        return self._assemble_mcq(
            question_text=f"What {verb.strip()} {self._short_phrase(subject, 8)}?",
            correct=correct,
            distractors=distractors,
            explanation=f"From your lesson: {self._truncate(sentence, 200)}",
            rng=rng,
        )

    def _cloze_mcq(self, sentence: str, key_terms: List[str], rng) -> Optional[Dict]:
        """Blank a key term in sentence; answer is the term. None if unusable."""
        present = [
            t for t in key_terms
            if re.search(r"\b" + re.escape(t) + r"\b", sentence, flags=re.I)
        ]
        if not present:
            return None

        present.sort(key=lambda t: len(t), reverse=True)
        answer = present[0]

        blanked = re.sub(
            r"\b" + re.escape(answer) + r"\b", "blank", sentence,
            count=1, flags=re.I,
        )
        if "blank" not in blanked.lower():
            return None

        others = [t for t in key_terms if t.lower() != answer.lower()]
        distractors = self._pick_length_matched(answer, self._dedupe(others), 3, rng)
        if len(distractors) < 3:
            return None

        return self._assemble_mcq(
            question_text=f"Fill in the blank. {self._truncate(blanked, 180)}",
            correct=answer,
            distractors=distractors,
            explanation=f"From your lesson: {self._truncate(sentence, 200)}",
            rng=rng,
        )

    @staticmethod
    def _assemble_mcq(question_text: str, correct: str, distractors: List[str],
                      explanation: str, rng) -> Dict:
        options = [{"text": correct, "is_correct": True}] + [
            {"text": d, "is_correct": False} for d in distractors
        ]
        rng.shuffle(options)
        return {
            "question_text": question_text,
            "question_type": "MCQ",
            "options": options,
            "explanation": explanation,
            "difficulty": "MEDIUM",
        }

    def generate_short_answer_questions(self, text: str, num_questions: int = 3) -> List[Dict]:
        """Generate short-answer discussion questions from key concepts."""
        questions = []
        prompts = [
            "Explain the concept of {concept}",
            "Describe how {concept} relates to the lesson content",
            "Discuss the importance of {concept}",
            "What is the significance of {concept}?",
            "How does {concept} apply in practice?",
        ]
        concepts = self.extract_key_concepts(text)
        for i, concept in enumerate(concepts[:num_questions]):
            prompt = prompts[i % len(prompts)]
            questions.append({
                "question_text": prompt.format(concept=concept["text"]),
                "question_type": "SHORT_ANSWER",
                "expected_keywords": [concept["text"]],
                "difficulty": "MEDIUM",
                "concept": concept["text"],
            })
        return questions

    def generate_all_questions(self, text: str, num_mcq: int = 5,
                               num_short_answer: int = 3) -> Dict[str, List]:
        """Generate all question types from text."""
        return {
            "mcq": self.generate_mcq_questions(text, num_mcq),
            "short_answer": self.generate_short_answer_questions(text, num_short_answer),
            "fill_blank": self.generate_fill_blank_questions(text, num_mcq // 2),
        }


def generate_questions(text: str, question_type: str = "all", **kwargs) -> Dict[str, List]:
    """Generate questions from text using the specified strategy."""
    try:
        generator = QuestionGenerator()
        if question_type == "all":
            return generator.generate_all_questions(
                text,
                num_mcq=kwargs.get('num_mcq', 5),
                num_short_answer=kwargs.get('num_short_answer', 3),
            )
        elif question_type == "mcq":
            return {"mcq": generator.generate_mcq_questions(text, kwargs.get('num_questions', 5))}
        elif question_type == "short_answer":
            return {"short_answer": generator.generate_short_answer_questions(text, kwargs.get('num_questions', 3))}
        elif question_type == "fill_blank":
            return {"fill_blank": generator.generate_fill_blank_questions(text, kwargs.get('num_questions', 3))}
        else:
            raise ValueError(f"Unknown question type: {question_type}")
    except Exception as e:
        raise QuestionGenerationError(f"Question generation failed: {str(e)}")
