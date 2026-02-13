"""
NLP Utilities for Deterministic Signal Extraction

This module provides deterministic NLP functions for keyword extraction,
text normalization, and signal detection. NO semantic reasoning, embeddings,
ML models, or AI judgment.

Ported from the original IdeaLab repository with enhancements.
"""

import re
from typing import List, Dict, Any, Set
from collections import Counter
import string

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import PorterStemmer
    
    # Download required NLTK data
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
        
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    print("WARNING: NLTK not available. Install with: pip install nltk")


class DeterministicNLP:
    """Deterministic NLP processor with no AI/ML components"""
    
    def __init__(self):
        if not NLTK_AVAILABLE:
            raise RuntimeError("NLTK is required. Install with: pip install nltk")
        
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Keep negations and intensifiers (don't remove these)
        self.stop_words_exceptions = {
            'not', 'no', 'nor', 'none', 'never', 'neither',
            'very', 'too', 'really', 'extremely', 'highly'
        }
        
        # Filler phrases to remove
        self.filler_phrases = {
            'i think', 'i believe', 'in my opinion', 'i feel',
            'it seems', 'kind of', 'sort of', 'you know'
        }
    
    def normalize_problem_text(self, text: str) -> str:
        """
        Normalize problem text for consistent matching.
        
        Steps:
        1. Lowercase
        2. Tokenize
        3. Remove stopwords (except negations)
        4. Stem tokens
        5. Remove fillers
        6. Deduplicate
        
        Returns idempotent, clean text.
        """
        # Lowercase
        text = text.lower().strip()
        
        # Remove filler phrases
        for filler in self.filler_phrases:
            text = text.replace(filler, '')
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Filter: remove stopwords but keep negations/intensifiers
        filtered_tokens = [
            t for t in tokens
            if t not in self.stop_words or t in self.stop_words_exceptions
        ]
        
        # Stem
        stemmed_tokens = [self.stemmer.stem(t) for t in filtered_tokens]
        
        # Remove punctuation-only tokens
        stemmed_tokens = [
            t for t in stemmed_tokens
            if not all(c in string.punctuation for c in t)
        ]
        
        # Deduplicate consecutive duplicates
        deduplicated = []
        prev = None
        for token in stemmed_tokens:
            if token != prev:
                deduplicated.append(token)
                prev = token
        
        normalized = ' '.join(deduplicated)
        
        # ASSERTION: No repeated consecutive tokens
        tokens_list = normalized.split()
        for i in range(len(tokens_list) - 1):
            assert tokens_list[i] != tokens_list[i+1], \
                f"Normalized text contains consecutive duplicates: {normalized}"
        
        return normalized
    
    def extract_keywords(
        self, 
        text: str, 
        top_n: int = 10,
        min_length: int = 3
    ) -> List[str]:
        """
        Extract keywords using deterministic frequency-based approach.
        
        Returns top_n most frequent non-stopword tokens.
        """
        # Normalize
        tokens = word_tokenize(text.lower())
        
        # Filter
        filtered = [
            t for t in tokens
            if t not in self.stop_words
            and len(t) >= min_length
            and t.isalnum()
        ]
        
        # Stem
        stemmed = [self.stemmer.stem(t) for t in filtered]
        
        # Count frequencies
        freq = Counter(stemmed)
        
        # Return top N
        return [word for word, count in freq.most_common(top_n)]
    
    def stem_tokens(self, tokens: List[str]) -> List[str]:
        """Stem a list of tokens"""
        return [self.stemmer.stem(t) for t in tokens]
    
    def stem_word(self, word: str) -> str:
        """Stem a single word"""
        return self.stemmer.stem(word.lower())
    
    def preprocess_text(self, text: str) -> Dict[str, Any]:
        """
        Full NLP pipeline returning all artifacts.
        
        Returns:
        - original_text: Original input
        - tokens: Word tokens
        - stems: Stemmed tokens
        - keywords: Top keywords
        - normalized: Normalized text
        """
        original_text = text
        
        # Tokenize
        tokens = word_tokenize(text.lower())
        
        # Stem
        stems = set(self.stem_tokens(tokens))
        
        # Extract keywords
        keywords = self.extract_keywords(text)
        
        # Normalize
        normalized = self.normalize_problem_text(text)
        
        return {
            'original_text': original_text,
            'tokens': tokens,
            'stems': stems,
            'keywords': keywords,
            'normalized': normalized
        }
    
    def match_keyword_with_context(
        self,
        keyword: str,
        preprocessed: Dict[str, Any],
        excluded_phrases: List[str] = None,
        required_context: List[str] = None
    ) -> bool:
        """
        Check if keyword exists in text with context validation.
        
        Example:
        - "automation" should match "automate tasks"
        - "automation" should NOT match "automation bias"
        - "critical" with required_context=["issue"] should NOT match "critical acclaim"
        
        Args:
            keyword: Word to match (will be stemmed)
            preprocessed: Output from preprocess_text()
            excluded_phrases: Phrases that invalidate the match
            required_context: Words that must be present near keyword
        
        Returns:
            True if keyword matches with valid context
        """
        keyword_stem = self.stem_word(keyword)
        
        # Check if stem exists
        if keyword_stem not in preprocessed['stems']:
            return False
        
        # Check excluded phrases
        if excluded_phrases:
            lower_text = preprocessed['original_text'].lower()
            for phrase in excluded_phrases:
                if phrase.lower() in lower_text:
                    return False
        
        # Check required context
        if required_context:
            lower_text = preprocessed['original_text'].lower()
            for req in required_context:
                if req.lower() not in lower_text:
                    return False
        
        return True
    
    def extract_ngrams(
        self,
        text: str,
        n: int = 2,
        min_freq: int = 2
    ) -> List[str]:
        """
        Extract n-grams (phrases) from text.
        
        Returns n-grams that appear at least min_freq times.
        """
        tokens = word_tokenize(text.lower())
        
        # Filter stopwords for cleaner n-grams
        filtered = [
            t for t in tokens
            if t not in self.stop_words and t.isalnum()
        ]
        
        # Generate n-grams
        ngrams = []
        for i in range(len(filtered) - n + 1):
            ngram = ' '.join(filtered[i:i+n])
            ngrams.append(ngram)
        
        # Count frequencies
        freq = Counter(ngrams)
        
        # Return those above threshold
        return [
            ngram for ngram, count in freq.items()
            if count >= min_freq
        ]
    
    def is_question(self, text: str) -> bool:
        """Deterministically check if text is a question"""
        text = text.strip()
        
        # Check for question mark
        if text.endswith('?'):
            return True
        
        # Check for question words at start
        question_words = {
            'who', 'what', 'when', 'where', 'why', 'how',
            'is', 'are', 'do', 'does', 'can', 'could',
            'would', 'should', 'will'
        }
        
        first_word = text.lower().split()[0] if text else ''
        return first_word in question_words
    
    def count_keywords_in_text(
        self,
        text: str,
        keywords: List[str],
        use_stemming: bool = True
    ) -> Dict[str, int]:
        """
        Count occurrences of each keyword in text.
        
        Returns dictionary: {keyword: count}
        """
        preprocessed = self.preprocess_text(text)
        
        counts = {}
        for keyword in keywords:
            if use_stemming:
                keyword_stem = self.stem_word(keyword)
                # Count in stemmed tokens
                count = sum(
                    1 for token in preprocessed['tokens']
                    if self.stem_word(token) == keyword_stem
                )
            else:
                count = preprocessed['tokens'].count(keyword.lower())
            
            counts[keyword] = count
        
        return counts


# Global instance for easy import
nlp = DeterministicNLP() if NLTK_AVAILABLE else None


# Convenience functions
def normalize_text(text: str) -> str:
    """Normalize text (convenience function)"""
    if not nlp:
        raise RuntimeError("NLTK not available")
    return nlp.normalize_problem_text(text)


def extract_keywords(text: str, top_n: int = 10) -> List[str]:
    """Extract keywords (convenience function)"""
    if not nlp:
        raise RuntimeError("NLTK not available")
    return nlp.extract_keywords(text, top_n=top_n)


def stem_word(word: str) -> str:
    """Stem a word (convenience function)"""
    if not nlp:
        raise RuntimeError("NLTK not available")
    return nlp.stem_word(word)
