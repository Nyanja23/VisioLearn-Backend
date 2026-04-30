"""Content chunking strategies for RAG and learning unit generation"""

import re
from typing import List
from dataclasses import dataclass


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata"""
    text: str
    sequence_number: int
    start_char: int
    end_char: int
    chunk_type: str  # "sentence", "paragraph", "sliding_window"


def split_into_sentences(text: str) -> List[str]:
    """
    Split text into sentences using regex
    
    Args:
        text: Raw text to split
        
    Returns:
        List of sentences
    """
    # Handle common abbreviations
    text = re.sub(r'(\w\.)(\s+)', r'\1___', text)
    
    # Split on sentence boundaries
    sentences = re.split(r'[.!?]+', text)
    
    # Restore spaces and clean
    sentences = [s.replace('___', ' ').strip() for s in sentences if s.strip()]
    
    return sentences


def split_into_paragraphs(text: str) -> List[str]:
    """
    Split text into paragraphs using line breaks
    
    Args:
        text: Raw text to split
        
    Returns:
        List of paragraphs (non-empty)
    """
    paragraphs = text.split('\n')
    paragraphs = [p.strip() for p in paragraphs if p.strip()]
    return paragraphs


def chunk_by_sentences(text: str, min_words_per_chunk: int = 50) -> List[TextChunk]:
    """
    Chunk text by combining sentences into learning units
    
    Args:
        text: Text to chunk
        min_words_per_chunk: Minimum words per chunk (default 50)
        
    Returns:
        List of TextChunk objects
    """
    sentences = split_into_sentences(text)
    chunks = []
    current_chunk = ""
    start_char = 0
    sequence = 0
    
    for sentence in sentences:
        test_chunk = current_chunk + " " + sentence if current_chunk else sentence
        word_count = len(test_chunk.split())
        
        if word_count >= min_words_per_chunk:
            if current_chunk:
                end_char = start_char + len(current_chunk)
                chunks.append(TextChunk(
                    text=current_chunk.strip(),
                    sequence_number=sequence,
                    start_char=start_char,
                    end_char=end_char,
                    chunk_type="sentence"
                ))
                sequence += 1
                start_char = end_char + 1
            current_chunk = sentence
        else:
            current_chunk = test_chunk
    
    # Add remaining chunk
    if current_chunk:
        end_char = start_char + len(current_chunk)
        chunks.append(TextChunk(
            text=current_chunk.strip(),
            sequence_number=sequence,
            start_char=start_char,
            end_char=end_char,
            chunk_type="sentence"
        ))
    
    return chunks


def chunk_by_paragraphs(text: str) -> List[TextChunk]:
    """
    Chunk text by paragraphs
    
    Args:
        text: Text to chunk
        
    Returns:
        List of TextChunk objects (one per paragraph)
    """
    paragraphs = split_into_paragraphs(text)
    chunks = []
    start_char = 0
    
    for seq, para in enumerate(paragraphs):
        end_char = start_char + len(para)
        chunks.append(TextChunk(
            text=para,
            sequence_number=seq,
            start_char=start_char,
            end_char=end_char,
            chunk_type="paragraph"
        ))
        start_char = end_char + 1
    
    return chunks


def create_sliding_windows(
    text: str,
    window_size: int = 3,
    stride: int = 1
) -> List[TextChunk]:
    """
    Create overlapping sliding windows of sentences for context preservation
    
    Useful for RAG to ensure full context around retrieved content.
    
    Args:
        text: Text to chunk
        window_size: Number of sentences per window
        stride: Number of sentences to skip between windows
        
    Returns:
        List of TextChunk objects with overlapping context
    """
    sentences = split_into_sentences(text)
    chunks = []
    start_char = 0
    sequence = 0
    
    for i in range(0, len(sentences), stride):
        window = sentences[i:i + window_size]
        if not window:
            break
        
        window_text = " ".join(window)
        end_char = start_char + len(window_text)
        
        chunks.append(TextChunk(
            text=window_text,
            sequence_number=sequence,
            start_char=start_char,
            end_char=end_char,
            chunk_type="sliding_window"
        ))
        sequence += 1
        start_char = end_char + 1
    
    return chunks


def chunk_text(
    text: str,
    strategy: str = "sentences",
    **kwargs
) -> List[TextChunk]:
    """
    Chunk text using specified strategy
    
    Args:
        text: Text to chunk
        strategy: "sentences", "paragraphs", or "sliding_windows"
        **kwargs: Strategy-specific parameters
        
    Returns:
        List of TextChunk objects
    """
    if strategy == "sentences":
        return chunk_by_sentences(text, kwargs.get('min_words_per_chunk', 50))
    elif strategy == "paragraphs":
        return chunk_by_paragraphs(text)
    elif strategy == "sliding_windows":
        return create_sliding_windows(
            text,
            window_size=kwargs.get('window_size', 3),
            stride=kwargs.get('stride', 1)
        )
    else:
        raise ValueError(f"Unknown chunking strategy: {strategy}")
