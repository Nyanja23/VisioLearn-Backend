"""AI-powered question generation from lesson content"""

import json
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
        """
        Extract key concepts (named entities and noun phrases) from text
        
        Args:
            text: Input text
            
        Returns:
            List of concepts with their types
        """
        doc = self.nlp(text)
        concepts = []
        
        # Extract named entities
        for ent in doc.ents:
            concepts.append({
                "text": ent.text,
                "type": ent.label_,
                "source": "entity"
            })
        
        # Extract noun phrases (basic heuristic)
        for chunk in doc.noun_chunks:
            concepts.append({
                "text": chunk.text,
                "type": "NOUN_PHRASE",
                "source": "noun_chunk"
            })
        
        # Remove duplicates
        seen = set()
        unique_concepts = []
        for concept in concepts:
            key = concept["text"].lower()
            if key not in seen:
                seen.add(key)
                unique_concepts.append(concept)
        
        return unique_concepts[:10]  # Return top 10
    
    def generate_fill_blank_questions(self, text: str, num_questions: int = 3) -> List[Dict]:
        """
        Generate fill-in-the-blank style questions
        
        Args:
            text: Source text
            num_questions: Number of questions to generate
            
        Returns:
            List of question dictionaries
        """
        doc = self.nlp(text)
        questions = []
        
        # Find sentences with significant entities or noun phrases
        for sent_idx, sent in enumerate(doc.sents):
            if len(questions) >= num_questions:
                break
            
            # Extract entities from sentence
            entities = [ent.text for ent in sent.ents]
            
            if not entities:
                continue
            
            # Create fill-in-the-blank by replacing first entity
            answer = entities[0]
            blank_sent = sent.text.replace(answer, "______", 1)
            
            questions.append({
                "question_text": blank_sent,
                "question_type": "FILL_BLANK",
                "correct_answer": answer,
                "difficulty": "MEDIUM",
                "source_sentence": sent.text
            })
        
        return questions
    
    # Linking verbs used to split a statement into subject + predicate, e.g.
    # "Photosynthesis is the process by which..." -> ask "What is photosynthesis?"
    _LINKING_VERBS = (" is ", " are ", " was ", " were ")

    @staticmethod
    def _truncate(text: str, max_len: int) -> str:
        text = text.strip()
        return text if len(text) <= max_len else text[:max_len].rstrip() + "…"

    def generate_mcq_questions(self, text: str, num_questions: int = 5) -> List[Dict]:
        """
        Generate content-bound multiple-choice questions.

        Each question is built directly from the lesson's own sentences, with
        the correct answer and the three distractors all drawn from the text —
        so questions stay accurate, curriculum-aligned, and never invent facts
        (the constrained, content-bound approach the project requires). Every
        question carries an ``explanation`` (the source sentence) so the app can
        teach on a wrong answer instead of only saying "incorrect".

        Returns a list of dicts shaped exactly as the Flutter client expects:
        ``question_text``, ``options`` (list of ``{text, is_correct}``),
        ``explanation``.
        """
        import random

        doc = self.nlp(text)
        # Usable sentences: long enough to be meaningful, not headings.
        sentences = [
            s.text.strip()
            for s in doc.sents
            if len(s.text.split()) >= 6
        ]
        # Need at least four distinct sentences so every question has one
        # correct answer plus three plausible distractors.
        if len(sentences) < 4:
            return []

        # Deterministic order so the same note always yields the same quiz.
        rng = random.Random(hash(text) & 0xFFFFFFFF)

        questions: List[Dict] = []
        used_sentences = set()

        for sentence in sentences:
            if len(questions) >= num_questions:
                break
            if sentence in used_sentences:
                continue

            mcq = self._mcq_from_sentence(sentence, sentences, rng)
            if mcq is not None:
                used_sentences.add(sentence)
                questions.append(mcq)

        return questions

    def _mcq_from_sentence(
        self, sentence: str, all_sentences: List[str], rng
    ) -> Optional[Dict]:
        """Build one MCQ from [sentence], or None if no good distractors exist."""
        # Pattern A: "X is/are <predicate>" -> "What is X?" with predicate as
        # the answer and other sentences' predicates as distractors.
        verb = next((v for v in self._LINKING_VERBS if v in sentence), None)
        if verb:
            idx = sentence.index(verb)
            subject = sentence[:idx].strip()
            predicate = sentence[idx + len(verb):].strip().rstrip(".")
            if 0 < len(subject) <= 60 and len(predicate) >= 3:
                distractors = []
                for other in all_sentences:
                    if other == sentence:
                        continue
                    ov = next((v for v in self._LINKING_VERBS if v in other), None)
                    if not ov:
                        continue
                    other_pred = other[other.index(ov) + len(ov):].strip().rstrip(".")
                    cand = self._truncate(other_pred, 90)
                    if cand and cand != predicate and cand not in distractors:
                        distractors.append(cand)
                    if len(distractors) >= 3:
                        break
                if len(distractors) >= 3:
                    return self._assemble_mcq(
                        question_text=f"What {verb.strip()} {self._truncate(subject, 70)}?",
                        correct=self._truncate(predicate, 90),
                        distractors=distractors[:3],
                        explanation=f"From your lesson: {self._truncate(sentence, 200)}",
                        rng=rng,
                    )

        # Pattern B (fallback): "which statement is correct?" using whole
        # sentences. The correct option already IS the lesson statement, so no
        # extra explanation is needed.
        others = [self._truncate(s, 120) for s in all_sentences if s != sentence]
        if len(others) < 3:
            return None
        rng.shuffle(others)
        return self._assemble_mcq(
            question_text="According to the lesson, which statement is correct?",
            correct=self._truncate(sentence, 120),
            distractors=others[:3],
            explanation="",
            rng=rng,
        )

    @staticmethod
    def _assemble_mcq(
        question_text: str,
        correct: str,
        distractors: List[str],
        explanation: str,
        rng,
    ) -> Dict:
        options = [{"text": correct, "is_correct": True}] + [
            {"text": d, "is_correct": False} for d in distractors
        ]
        rng.shuffle(options)  # correct answer lands in a random position
        return {
            "question_text": question_text,
            "question_type": "MCQ",
            "options": options,
            "explanation": explanation,
            "difficulty": "MEDIUM",
        }
    
    def generate_short_answer_questions(self, text: str, num_questions: int = 3) -> List[Dict]:
        """
        Generate short-answer discussion questions
        
        Args:
            text: Source text
            num_questions: Number of questions to generate
            
        Returns:
            List of short-answer question dictionaries
        """
        questions = []
        
        # Heuristic: Generate "Explain" and "Discuss" questions
        prompts = [
            "Explain the concept of {concept}",
            "Describe how {concept} relates to the lesson content",
            "Discuss the importance of {concept}",
            "What is the significance of {concept}?",
            "How does {concept} apply in practice?"
        ]
        
        concepts = self.extract_key_concepts(text)
        
        for i, concept in enumerate(concepts[:num_questions]):
            prompt = prompts[i % len(prompts)]
            questions.append({
                "question_text": prompt.format(concept=concept["text"]),
                "question_type": "SHORT_ANSWER",
                "expected_keywords": [concept["text"]],
                "difficulty": "MEDIUM",
                "concept": concept["text"]
            })
        
        return questions
    
    def generate_all_questions(
        self,
        text: str,
        num_mcq: int = 5,
        num_short_answer: int = 3
    ) -> Dict[str, List]:
        """
        Generate all question types from text
        
        Args:
            text: Source text
            num_mcq: Number of MCQs
            num_short_answer: Number of short-answer questions
            
        Returns:
            Dictionary with question types as keys
        """
        return {
            "mcq": self.generate_mcq_questions(text, num_mcq),
            "short_answer": self.generate_short_answer_questions(text, num_short_answer),
            "fill_blank": self.generate_fill_blank_questions(text, num_mcq // 2)
        }


def generate_questions(
    text: str,
    question_type: str = "all",
    **kwargs
) -> Dict[str, List]:
    """
    Generate questions from text using specified strategy
    
    Args:
        text: Source text
        question_type: "mcq", "short_answer", "fill_blank", or "all"
        **kwargs: Additional parameters (num_mcq, num_short_answer, etc.)
        
    Returns:
        Dictionary with generated questions
        
    Raises:
        QuestionGenerationError: If generation fails
    """
    try:
        generator = QuestionGenerator()
        
        if question_type == "all":
            return generator.generate_all_questions(
                text,
                num_mcq=kwargs.get('num_mcq', 5),
                num_short_answer=kwargs.get('num_short_answer', 3)
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
