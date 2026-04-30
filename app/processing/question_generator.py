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
    
    def generate_mcq_questions(self, text: str, num_questions: int = 5) -> List[Dict]:
        """
        Generate multiple-choice questions
        
        Args:
            text: Source text
            num_questions: Number of MCQ to generate
            
        Returns:
            List of MCQ question dictionaries
        """
        concepts = self.extract_key_concepts(text)
        questions = []
        
        for i, concept in enumerate(concepts[:num_questions]):
            if not concept["text"]:
                continue
            
            # Create a question about the concept
            question_text = f"Which of the following best describes {concept['text']}?"
            
            # For now, use the source text as the correct answer explanation
            # In production, use a more sophisticated method
            options = [
                {"text": concept["text"], "is_correct": True},
                {"text": f"Not related to {concept['type']}", "is_correct": False},
                {"text": "An alternative concept", "is_correct": False},
                {"text": "A general term", "is_correct": False}
            ]
            
            questions.append({
                "question_text": question_text,
                "question_type": "MCQ",
                "options": options,
                "difficulty": "MEDIUM",
                "concept": concept["text"],
                "concept_type": concept["type"]
            })
        
        return questions
    
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
