"""Text summarization and feedback generation for lessons"""

import re
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import numpy as np


class SummarizationError(Exception):
    """Raised when summarization fails"""
    pass


class TextSummarizer:
    """Generates summaries and feedback from lesson content"""
    
    def __init__(self):
        """Initialize transformer model for semantic similarity"""
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
        except Exception as e:
            raise SummarizationError(f"Failed to load summarization model: {str(e)}")
    
    def split_sentences(self, text: str) -> List[str]:
        """Split text into sentences"""
        # Simple sentence splitting
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def score_sentences_by_similarity(
        self,
        sentences: List[str],
        num_summary_sentences: int = 5
    ) -> List[tuple]:
        """
        Score sentences by their importance using semantic similarity
        
        Args:
            sentences: List of sentences
            num_summary_sentences: Number of sentences for summary
            
        Returns:
            List of (sentence, score, index) tuples sorted by score
        """
        if not sentences:
            return []
        
        # Generate embeddings for all sentences
        embeddings = self.model.encode(sentences)
        
        # Calculate sentence importance based on average similarity to other sentences
        scores = []
        for i, embedding in enumerate(embeddings):
            # Cosine similarity to other sentences
            similarities = [
                np.dot(embedding, embeddings[j]) / (
                    np.linalg.norm(embedding) * np.linalg.norm(embeddings[j]) + 1e-8
                )
                for j in range(len(embeddings)) if i != j
            ]
            
            avg_similarity = np.mean(similarities) if similarities else 0
            scores.append((sentences[i], avg_similarity, i))
        
        # Sort by score and return top sentences in original order
        sorted_scores = sorted(scores, key=lambda x: x[1], reverse=True)
        top_sentences = sorted(sorted_scores[:num_summary_sentences], key=lambda x: x[2])
        
        return [(s, score) for s, score, _ in top_sentences]
    
    def generate_summary(
        self,
        text: str,
        summary_ratio: float = 0.3
    ) -> str:
        """
        Generate extractive summary of text
        
        Args:
            text: Text to summarize
            summary_ratio: Ratio of original text (0.3 = 30%)
            
        Returns:
            Summary text
        """
        sentences = self.split_sentences(text)
        
        if not sentences:
            return ""
        
        num_summary_sentences = max(1, int(len(sentences) * summary_ratio))
        summary_sentences = self.score_sentences_by_similarity(sentences, num_summary_sentences)
        
        summary = " ".join([s for s, _ in summary_sentences])
        return summary
    
    def generate_key_points(
        self,
        text: str,
        num_points: int = 5
    ) -> List[str]:
        """
        Generate bullet-point key takeaways
        
        Args:
            text: Text to extract key points from
            num_points: Number of key points
            
        Returns:
            List of key point sentences
        """
        sentences = self.split_sentences(text)
        
        if not sentences:
            return []
        
        top_sentences = self.score_sentences_by_similarity(sentences, num_points)
        return [s for s, _ in top_sentences]
    
    def generate_learning_objectives(
        self,
        text: str,
        num_objectives: int = 3
    ) -> List[str]:
        """
        Generate learning objectives based on text
        
        Heuristic: Extract key concepts and create "Students will understand..." statements
        
        Args:
            text: Lesson text
            num_objectives: Number of objectives
            
        Returns:
            List of learning objective strings
        """
        sentences = self.split_sentences(text)
        top_sentences = self.score_sentences_by_similarity(sentences, num_objectives)
        
        objectives = []
        for sentence, _ in top_sentences:
            # Convert to learning objective format
            objective = f"Students will be able to understand {sentence.lower()}"
            objectives.append(objective)
        
        return objectives


def generate_summary(text: str, summary_ratio: float = 0.3) -> str:
    """
    Generate summary of text
    
    Args:
        text: Text to summarize
        summary_ratio: Ratio of original text (default 30%)
        
    Returns:
        Summary text
        
    Raises:
        SummarizationError: If summarization fails
    """
    try:
        summarizer = TextSummarizer()
        return summarizer.generate_summary(text, summary_ratio)
    except Exception as e:
        raise SummarizationError(f"Summarization failed: {str(e)}")


def generate_key_points(text: str, num_points: int = 5) -> List[str]:
    """
    Generate key points from text
    
    Args:
        text: Text to extract from
        num_points: Number of key points
        
    Returns:
        List of key points
    """
    try:
        summarizer = TextSummarizer()
        return summarizer.generate_key_points(text, num_points)
    except Exception as e:
        raise SummarizationError(f"Key point generation failed: {str(e)}")


def generate_learning_objectives(text: str, num_objectives: int = 3) -> List[str]:
    """
    Generate learning objectives from text
    
    Args:
        text: Lesson text
        num_objectives: Number of objectives
        
    Returns:
        List of learning objectives
    """
    try:
        summarizer = TextSummarizer()
        return summarizer.generate_learning_objectives(text, num_objectives)
    except Exception as e:
        raise SummarizationError(f"Objective generation failed: {str(e)}")


FEEDBACK_TEMPLATES = {
    "general_correct": [
        "Excellent! You've demonstrated a strong understanding.",
        "Great job! Your answer shows you've mastered this concept.",
        "Perfect! That's the correct understanding."
    ],
    "general_incorrect": [
        "Not quite. Let's review the key concepts.",
        "That's not quite right. Consider this perspective...",
        "Close, but let's clarify this concept."
    ],
    "partial_correct": [
        "You're partially correct. Consider the full picture...",
        "Good thinking, but there's more to it.",
        "You're on the right track. Let's expand on that..."
    ]
}


def get_feedback_template(template_type: str = "general_correct") -> str:
    """Get a feedback template"""
    templates = FEEDBACK_TEMPLATES.get(template_type, FEEDBACK_TEMPLATES["general_incorrect"])
    return templates[0] if templates else ""
