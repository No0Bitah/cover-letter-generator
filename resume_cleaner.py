# resume_cleaner.py
"""
Resume cleaning module that uses Ollama API to clean and format resume text.
This module imports configuration from config.py for consistency.
"""

import re
import requests
import json
from config import (
    OLLAMA_API_URL,
    MODEL_NAME,
    MODEL_PARAMETERS,
    RESUME_CLEANING_PROMPT_TEMPLATE,
    ERROR_MESSAGES
)



def extract_between_dashes(response: str) -> str:
    """
    Extracts only the content between the first two lines containing '---' in the response.
    Returns an empty string if the pattern is not found.
    """
    dash_match = re.search(r"---\s*\n(.*?)\n---", response, flags=re.DOTALL)
    if dash_match:
        return dash_match.group(1).strip()

    # Try to extract content after "Here is the" phrase
    here_is_match = re.search(r"(Here (is|’s|s the)[^\n]*:\s*\n+)(.*)", response, flags=re.IGNORECASE | re.DOTALL)
    if here_is_match:
        return here_is_match.group(3).strip()

    # Fallback: Remove any <think>...</think> block and return the rest
    fallback = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL | re.IGNORECASE).strip()
    if fallback:
        # Remove any leading/trailing whitespace and return
        fallback = re.sub(r"^\s+|\s+$", "", fallback)
        if fallback:
            return fallback
    else:
        return fallback if fallback else "No valid content found."  
    # return fallback 
    

def clean_resume(resume_text: str) -> str:
    """
    Clean and format resume text using Ollama API.
    
    Args:
        resume_text (str): Raw resume text to be cleaned
        
    Returns:
        str: Cleaned and formatted resume text
    """
    if not resume_text.strip():
        return ""
    
    # Generate the cleaning prompt using the template from config
    prompt = RESUME_CLEANING_PROMPT_TEMPLATE.format(resume_text=resume_text)
    
    headers = {
        "Content-Type": "application/json"
    }

    # Payload to send to the API
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        **MODEL_PARAMETERS
    }

    try:
        response = requests.post(OLLAMA_API_URL, headers=headers, data=json.dumps(data))
        
        # Check if the response is successful
        if response.status_code == 200:
            result = response.json()
            print("OLLAMA RAW RESPONSE befire cleaming resume:")
            repr(result['response'])  # Or use logging
            cleaned_cover_letter = extract_between_dashes(result['response'])
            with open("generated_resume_cleaned.txt", "w", encoding="utf-8") as f:
                f.write(cleaned_cover_letter)
            return cleaned_cover_letter
        else:
            error_msg = ERROR_MESSAGES["api_error"].format(
                status_code=response.status_code,
                error_text=response.text
            )
            print(f"Resume cleaning error: {error_msg}")
            # Return original text if cleaning fails
            return resume_text
            
    except Exception as e:
        error_msg = ERROR_MESSAGES["general_error"].format(error=str(e))
        print(f"Resume cleaning error: {error_msg}")
        # Return original text if cleaning fails
        return resume_text

def validate_resume_text(resume_text: str) -> bool:
    """
    Validate if the resume text contains essential information.
    
    Args:
        resume_text (str): Resume text to validate
        
    Returns:
        bool: True if resume appears to be valid, False otherwise
    """
    if not resume_text or len(resume_text.strip()) < 50:
        return False
    
    # Check for common resume sections/keywords
    resume_keywords = [
        'experience', 'education', 'skills', 'work', 'employment',
        'university', 'college', 'degree', 'certification', 'project'
    ]
    
    text_lower = resume_text.lower()
    keyword_count = sum(1 for keyword in resume_keywords if keyword in text_lower)
    
    # Resume should contain at least 2 common keywords
    return keyword_count >= 2

def extract_key_sections(resume_text: str) -> dict:
    """
    Extract key sections from resume text for better processing.
    
    Args:
        resume_text (str): Resume text to process
        
    Returns:
        dict: Dictionary containing different sections of the resume
    """
    sections = {
        'full_text': resume_text,
        'has_contact_info': False,
        'has_experience': False,
        'has_education': False,
        'has_skills': False
    }
    
    text_lower = resume_text.lower()
    
    # Check for different sections
    if any(keyword in text_lower for keyword in ['email', 'phone', 'linkedin', '@']):
        sections['has_contact_info'] = True
    
    if any(keyword in text_lower for keyword in ['experience', 'work', 'employment', 'job']):
        sections['has_experience'] = True
    
    if any(keyword in text_lower for keyword in ['education', 'university', 'college', 'degree']):
        sections['has_education'] = True
    
    if any(keyword in text_lower for keyword in ['skills', 'technology', 'programming', 'software']):
        sections['has_skills'] = True
    
    return sections
