# config.py
"""
Configuration file for Cover Letter Generator
Contains all configurable parameters including Ollama settings,
model parameters, and prompt templates.
"""

# Ollama API Configuration
OLLAMA_API_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "gemma:2b"

# Model Generation Parameters
MODEL_PARAMETERS = {
    "temperature": 0.7,  # Creativity level (0.0-1.0)
    "top_p": 0.9,       # Diversity control (0.0-1.0)
    "stream": False,    # Whether to stream responses
}

# UI Configuration
TYPING_SPEED = 0.03  # Speed for typing animation effect
MAX_WORD_LIMIT = 200  # Maximum words for cover letter

# File Processing Configuration
SUPPORTED_FILE_TYPES = ["pdf", "docx", "txt"]
TEMP_FILE_PREFIX = "cover_letter_temp_"

# Prompt Templates
COVER_LETTER_PROMPT_TEMPLATE = """
You are a professional cover letter writer. Write a compelling, personalized cover letter based on the resume and job description provided.

⚠️ Important instructions:
The goal is to create a professional, eager-to-learn, and concise cover letter.
    The cover letter must:

    1. Only include the technologies and experiences mentioned in the resume.
    2. Connect the technologies in the resume with those mentioned in the job description.
    3. If there are any technologies in the job description not mentioned in the resume, politely mention that the applicant is willing and eager to learn them.
    4. Make the tone of the cover letter enthusiastic and focused on giving their best to the work.
    5. Format the cover letter to be brief, as most hiring teams prefer short and to-the-point emails.
    6. Use a professional tone, avoiding any casual language and use words not more than {word_limit}.
    7. Use Email format, including a subject line and a greeting.

    
    Include the resume and job description below and generate the cover letter formatted as an email.

📄 Resume:
\"\"\"
{resume_text}
\"\"\"

🧾 Job Description:
\"\"\"
{job_description}
\"\"\"

✍️ Now, write the best possible cover letter based on these.
"""

PERSONALIZATION_PROMPT_TEMPLATE = """
You are a professional cover letter writer. Here is the current cover letter:

{current_cover_letter}

The user has requested the following personalization:
{user_request}

Please update the cover letter accordingly, keeping it concise, short and professional.
"""

RESUME_CLEANING_PROMPT_TEMPLATE = """
You are a professional resume formatter. Clean and format the following resume text:

{resume_text}

Please:
1. Remove any unnecessary formatting artifacts
2. Organize the content properly
3. Ensure consistency in formatting
4. Keep all important information intact
5. Make it professional and readable

Return only the cleaned resume text.
"""

# UI Messages and Labels
UI_MESSAGES = {
    "app_title": "Cover Letter Generator",
    "app_description": "This tool generates a personalized cover letter based on your resume and job description.",
    "resume_upload_label": "Choose your resume file (PDF, DOCX, or TXT)",
    "job_upload_label": "Choose the job description file (PDF, DOCX, or TXT)",
    "resume_text_label": "Paste your resume text here (optional, overrides uploaded file)",
    "job_text_label": "Paste the job description here (optional, overrides uploaded file)",
    "generate_button": "🚀 Generate Cover Letter",
    "personalization_input": "Ask to personalize or modify your cover letter (e.g., 'Make it more formal', 'Add a sentence about teamwork'):",
    "personalization_button": "Submit Personalization",
    "personalization_header": "Personalize Your Cover Letter Further",
    
    # Status messages
    "resume_ready": "✅ Resume ready!",
    "job_ready": "✅ Job description ready!",
    "resume_missing": "Please upload your resume file or paste resume text.",
    "job_missing": "Please upload the job description file or paste job description text.",
    
    # Info messages
    "upload_both": "👆 Please upload both your resume and job description files from the sidebar, or paste the text directly, then click 'Generate Cover Letter'.",
    "upload_resume": "👆 Please upload your resume file or paste resume text from the sidebar, then click 'Generate Cover Letter'.",
    "upload_job": "👆 Please upload the job description file or paste job description text from the sidebar, then click 'Generate Cover Letter'.",
    
    # Loading messages
    "generating_letter": "Generating your personalized cover letter...",
    "cleaning_resume": "Cleaning and processing your resume...",
    "personalizing_letter": "Personalizing your cover letter...",
    "Note": "Please review the generated cover letter before using or sending it. "
        "While AI helps create a solid draft, it may include inaccuracies or overlook specific details. "
        "Always double-check for correctness, tone, and personal relevance.",
}

# Styling Configuration
COVER_LETTER_STYLE = {
    "container": """
    <div style='display: flex; justify-content: center; margin-top: 20px;'>
        <div style='max-width: 800px; background-color: #f8f9fa; padding: 20px;
                    border-radius: 10px; font-family: Arial, sans-serif;
                    white-space: pre-wrap; line-height: 1.6; font-size: 16px; color: #333;'>
    """,
    "container_end": "</div></div>"
}

# Session State Keys
SESSION_KEYS = {
    "cover_letter_placeholder": "cover_letter_placeholder",
    "processed_resume_text": "processed_resume_text",
    "processed_job_description": "processed_job_description",
    "last_resume_file_name": "last_resume_file_name",
    "last_job_file_name": "last_job_file_name",
    "generated_cover_letter": "generated_cover_letter",
    "cover_letter_generated": "cover_letter_generated",
    "chat_history": "chat_history",
    "current_displayed_letter": "current_displayed_letter",
    "resume_text_input": "resume_text_input",
    "job_description_input": "job_description_input",
}

# Error Messages
ERROR_MESSAGES = {
    "ollama_connection": "Error connecting to Ollama. Please ensure Ollama is running and the model is available.",
    "file_processing": "Error processing file. Please check the file format and try again.",
    "pdf_extraction": "Error extracting PDF. Using fallback extraction method.",
    "api_error": "API Error: {status_code}, {error_text}",
    "general_error": "An error occurred: {error}",
}

# File type mappings
FILE_TYPE_MAPPINGS = {
    "application/pdf": "pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": "docx",
    "text/plain": "txt",
}