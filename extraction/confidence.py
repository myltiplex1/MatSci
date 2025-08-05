from logger import setup_logger

logger = setup_logger('confidence')

def calculate_confidence(text_snippet):
    """Calculate a confidence score for an extracted parameter."""
    try:
        # Placeholder logic: Confidence based on text length and keyword presence
        confidence = min(0.9, len(text_snippet) / 1000.0)
        if any(keyword in text_snippet.lower() for keyword in ["precursor", "temperature", "ph", "method"]):
            confidence += 0.1
        confidence = min(confidence, 1.0)
        logger.info(f"Calculated confidence score: {confidence}")
        return confidence
    except Exception as e:
        logger.error(f"Error calculating confidence: {str(e)}")
        return 0.5  # Default confidence