"""
Learner Module for AI Agent Learning System.
"""

import asyncio
import logging
import json
import pickle
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from pathlib import Path
import os
import time


@dataclass
class LearningExample:
    """A single learning example."""
    input_text: str
    output_text: str
    feedback: Optional[str] = None
    score: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class Learner:
    """
    Learning system for AI Agent.
    
    Features:
    - Learn from user feedback
    - Adapt responses based on preferences
    - Improve over time
    - Track learning progress
    """
    
    def __init__(self, storage_dir: str = "~/ai-agent/learning"):
        """Initialize the Learner."""
        self.logger = logging.getLogger("Learner")
        self._storage_dir = Path(os.path.expanduser(storage_dir))
        self._storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Learning data
        self._examples: List[LearningExample] = []
        self._patterns: Dict[str, Any] = {}
        self._preferences: Dict[str, Any] = {}
        
        # Load existing learning data
        self._load_learning_data()
        
    def _load_learning_data(self) -> None:
        """Load learning data from disk."""
        try:
            # Load examples
            examples_file = self._storage_dir / "examples.pkl"
            if examples_file.exists():
                with open(examples_file, "rb") as f:
                    self._examples = pickle.load(f)
                    
            # Load patterns
            patterns_file = self._storage_dir / "patterns.json"
            if patterns_file.exists():
                with open(patterns_file, "r") as f:
                    self._patterns = json.load(f)
                    
            # Load preferences
            preferences_file = self._storage_dir / "preferences.json"
            if preferences_file.exists():
                with open(preferences_file, "r") as f:
                    self._preferences = json.load(f)
                    
            self.logger.info(f"Loaded {len(self._examples)} learning examples")
            
        except Exception as e:
            self.logger.error(f"Failed to load learning data: {e}")
            
    def _save_learning_data(self) -> None:
        """Save learning data to disk."""
        try:
            # Save examples
            with open(self._storage_dir / "examples.pkl", "wb") as f:
                pickle.dump(self._examples, f)
                
            # Save patterns
            with open(self._storage_dir / "patterns.json", "w") as f:
                json.dump(self._patterns, f, indent=2)
                
            # Save preferences
            with open(self._storage_dir / "preferences.json", "w") as f:
                json.dump(self._preferences, f, indent=2)
                
        except Exception as e:
            self.logger.error(f"Failed to save learning data: {e}")
            
    def add_example(
        self,
        input_text: str,
        output_text: str,
        feedback: Optional[str] = None,
        score: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Add a learning example."""
        example = LearningExample(
            input_text=input_text,
            output_text=output_text,
            feedback=feedback,
            score=score,
            metadata=metadata or {}
        )
        
        self._examples.append(example)
        self._save_learning_data()
        
        self.logger.info(f"Added learning example: {input_text[:50]}...")
        
    def learn_from_feedback(
        self,
        input_text: str,
        output_text: str,
        feedback: str,
        score: float
    ) -> None:
        """Learn from user feedback."""
        # Add as learning example
        self.add_example(
            input_text=input_text,
            output_text=output_text,
            feedback=feedback,
            score=score
        )
        
        # Extract patterns from feedback
        self._extract_patterns(input_text, output_text, feedback, score)
        
        # Update preferences
        self._update_preferences(input_text, output_text, feedback, score)
        
    def _extract_patterns(
        self,
        input_text: str,
        output_text: str,
        feedback: str,
        score: float
    ) -> None:
        """Extract patterns from feedback."""
        # Simple pattern extraction
        feedback_lower = feedback.lower()
        
        # Positive patterns
        if score > 0.7:
            if "good" in feedback_lower or "great" in feedback_lower:
                self._patterns["positive_response"] = self._patterns.get("positive_response", 0) + 1
                
        # Negative patterns
        if score < 0.3:
            if "bad" in feedback_lower or "wrong" in feedback_lower:
                self._patterns["negative_response"] = self._patterns.get("negative_response", 0) + 1
                
        # Save patterns
        self._save_learning_data()
        
    def _update_preferences(
        self,
        input_text: str,
        output_text: str,
        feedback: str,
        score: float
    ) -> None:
        """Update user preferences based on feedback."""
        # Extract preference keywords
        feedback_lower = feedback.lower()
        
        preference_keywords = [
            "prefer", "like", "want", "need",
            "don't like", "don't want", "avoid"
        ]
        
        for keyword in preference_keywords:
            if keyword in feedback_lower:
                # Store preference
                pref_key = f"preference_{len(self._preferences)}"
                self._preferences[pref_key] = {
                    "input": input_text,
                    "feedback": feedback,
                    "score": score,
                    "timestamp": time.time()
                }
                break
                
        # Save preferences
        self._save_learning_data()
        
    def get_similar_examples(
        self,
        input_text: str,
        limit: int = 5
    ) -> List[LearningExample]:
        """Get similar learning examples."""
        if not self._examples:
            return []
            
        # Simple similarity based on word overlap
        input_words = set(input_text.lower().split())
        
        scored_examples = []
        for example in self._examples:
            example_words = set(example.input_text.lower().split())
            
            # Calculate similarity
            if input_words and example_words:
                similarity = len(input_words & example_words) / len(input_words | example_words)
                scored_examples.append((similarity, example))
                
        # Sort by similarity
        scored_examples.sort(key=lambda x: x[0], reverse=True)
        
        return [example for _, example in scored_examples[:limit]]
        
    def get_best_response(
        self,
        input_text: str
    ) -> Optional[str]:
        """Get the best response based on learning."""
        similar_examples = self.get_similar_examples(input_text, limit=3)
        
        if not similar_examples:
            return None
            
        # Find example with highest score
        best_example = max(similar_examples, key=lambda e: e.score)
        
        if best_example.score > 0.5:
            return best_example.output_text
            
        return None
        
    def get_learning_stats(self) -> Dict[str, Any]:
        """Get learning statistics."""
        if not self._examples:
            return {
                "total_examples": 0,
                "average_score": 0.0,
                "positive_examples": 0,
                "negative_examples": 0
            }
            
        scores = [e.score for e in self._examples]
        
        return {
            "total_examples": len(self._examples),
            "average_score": sum(scores) / len(scores),
            "positive_examples": len([s for s in scores if s > 0.7]),
            "negative_examples": len([s for s in scores if s < 0.3]),
            "patterns_learned": len(self._patterns),
            "preferences_learned": len(self._preferences)
        }
        
    def clear_learning_data(self) -> None:
        """Clear all learning data."""
        self._examples.clear()
        self._patterns.clear()
        self._preferences.clear()
        
        # Delete files
        for file in self._storage_dir.glob("*"):
            file.unlink()
            
        self.logger.warning("All learning data cleared")