# File: custom_model.py
# This model assesses transcript quality and completeness

import pandas as pd
import json

def load_model(input_dir):
    """
    Load any model artifacts or configurations
    """
    return {
        "min_words": 50,
        "required_keywords": ["HCP", "product", "discussion"],
        "max_transcription_confidence": 0.7
    }

def score(data, model, **kwargs):
    """
    Score function that validates transcript quality
    
    Args:
        data: DataFrame with 'transcript' column
        model: Model config loaded by load_model()
        
    Returns:
        DataFrame with quality scores
    """
    results = []
    
    for idx, row in data.iterrows():
        transcript = row.get('transcript', '')
        
        # Initialize quality checks
        quality_checks = {
            "word_count": len(transcript.split()),
            "has_hcp": "HCP" in transcript.upper() or "doctor" in transcript.lower(),
            "has_product": any(prod in transcript.lower() for prod in ["product", "medication", "drug"]),
            "length_ok": len(transcript.split()) >= model["min_words"],
            "has_structure": any(marker in transcript.lower() for marker in ["visit", "call", "meeting"])
        }
        
        # Calculate quality score (0-1)
        passed_checks = sum(quality_checks.values())
        total_checks = len(quality_checks)
        quality_score = passed_checks / total_checks
        
        # Determine routing decision
        if quality_score >= 0.8:
            route = "process"
            confidence = "high"
        elif quality_score >= 0.6:
            route = "process_with_review"
            confidence = "medium"
        else:
            route = "reject"
            confidence = "low"
        
        results.append({
            "quality_score": quality_score,
            "route": route,
            "confidence": confidence,
            "word_count": quality_checks["word_count"],
            "validation_details": json.dumps(quality_checks)
        })
    
    return pd.DataFrame(results)