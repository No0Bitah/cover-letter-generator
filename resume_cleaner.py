import requests
import re


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "llama3.1:8b"
USER_PROMPT = """
organize the resume text into a clean, structured format. The original text had a two-column layout that got jumbled during extraction, reorganized it into proper sections with clear hierarchy:

Header - Name and title
Contact Information - Address, phone, email
Career Overview - Professional summary
Education - Degrees with dates and institutions
Work Experience - Jobs in reverse chronological order with company, position, duration, and responsibilities
Skills - Technical and soft skills

**MAKE SURE TO PUT CORRECT SPELLING AND Information
**DO NOT MAKEUP ADDITIONAL INFO

Important NOTE! ***
					1.ONLY OUTPUT THE TAILORED RESUME DON'T INCLUDE OTHER TEXTS!
				***
"""

def query_ollama(model, prompt):
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    response = requests.post(OLLAMA_URL, json=payload)
    response.raise_for_status()
    data = response.json()
    return data.get("response", "")

def remove_extra_intro(text):
    """
    Removes common introductory phrases or sentences from the AI response.
    """
    # List of common intro phrases to remove (case-insensitive)
    patterns = [
        r"^here is the reorganized resume.*?:\s*",  # e.g., "Here is the reorganized resume in a clean and structured format:"
        r"^organized resume:\s*",
        r"^cleaned resume:\s*",
        r"^below is.*?:\s*",
        r"^the cleaned and structured resume is as follows:\s*",
        r"^resume:\s*",
    ]
    cleaned = text
    for pat in patterns:
        cleaned = re.sub(pat, '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip()

def clean_resume(resume_text):
    """ Clean the resume text using Ollama model
    """
    try:
        result = query_ollama(MODEL, USER_PROMPT + " " + resume_text)

        # Remove any extra introductory text
        result = remove_extra_intro(result)
        # save the result to a file for debugging
        with open("resume-result.txt", "w", encoding="utf-8") as f:
            f.write(result)
        return result
    except requests.RequestException as e:
        return f"Error querying Ollama: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"

