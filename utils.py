import re

def clean_text(text):
    """
    Clean and sanitize text input
    
    :param text: Input text to clean
    :return: Cleaned text or None
    """
    if not text:
        return None
    
    # Remove non-breaking spaces and extra whitespaces
    cleaned = text.replace('\xa0', '').strip()
    return cleaned if cleaned else None

def parse_year(year_text):
    """
    Parse year from text
    
    :param year_text: Year as text
    :return: Integer year or None
    """
    try:
        # Extract only numeric characters
        year = re.findall(r'\d{4}', str(year_text))
        return int(year[0]) if year else None
    except (ValueError, IndexError):
        return None

def parse_duration(duration_text):
    """
    Parse movie duration in minutes
    
    :param duration_text: Duration as text
    :return: Total minutes or None
    """
    if not duration_text:
        return None
    
    # Clean the text
    duration_text = clean_text(duration_text)
    
    # Match hours and minutes
    hours_match = re.search(r'(\d+)h', duration_text)
    minutes_match = re.search(r'(\d+)m', duration_text)
    
    total_minutes = 0
    
    # Calculate hours to minutes
    if hours_match:
        total_minutes += int(hours_match.group(1)) * 60
    
    # Add minutes
    if minutes_match:
        total_minutes += int(minutes_match.group(1))
    
    return total_minutes if total_minutes > 0 else None

def parse_rating(rating_text):
    """
    Parse IMDb rating
    
    :param rating_text: Rating as text
    :return: Float rating or None
    """
    if not rating_text:
        return None
    
    try:
        # Remove non-numeric characters except decimal point
        cleaned_rating = re.sub(r'[^\d.]', '', str(rating_text))
        return float(cleaned_rating) if cleaned_rating else None
    except (ValueError, TypeError):
        return None

def parse_total_ratings(ratings_text):
    """
    Parse total number of ratings
    
    :param ratings_text: Ratings text
    :return: Integer total ratings or None
    """
    if not ratings_text:
        return None
    
    try:
        # Clean the text
        cleaned_text = clean_text(ratings_text)
        
        # Handle millions (M)
        if 'M' in cleaned_text:
            return int(float(cleaned_text.replace('M', '')) * 1_000_000)
        
        # Handle thousands (K)
        if 'K' in cleaned_text:
            return int(float(cleaned_text.replace('K', '')) * 1_000)
        
        # Remove non-numeric characters
        numeric_ratings = re.sub(r'[^\d]', '', cleaned_text)
        return int(numeric_ratings) if numeric_ratings else None
    
    except (ValueError, TypeError):
        return None