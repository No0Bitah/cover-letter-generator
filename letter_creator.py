# letter_creator.py
"""This script generates a personalized cover letter based on a resume and job description.
It uses the Ollama API to generate the cover letter text.
It requires the resume and job description to be provided in text files.
It is designed to create a concise, professional cover letter that highlights relevant skills and expresses eagerness to learn new technologies.

It is recommended to run this script in an environment where the Ollama API is accessible."""

import streamlit as st
import requests
import json
from extract_resume import extract
from resume_cleaner import clean_resume
import fitz # PyMuPDF
import time
import tempfile
import os
from docx import Document

# Import configuration
from config import (
    OLLAMA_API_URL,
    MODEL_NAME,
    MODEL_PARAMETERS,
    TYPING_SPEED,
    MAX_WORD_LIMIT,
    COVER_LETTER_PROMPT_TEMPLATE,
    PERSONALIZATION_PROMPT_TEMPLATE,
    UI_MESSAGES,
    COVER_LETTER_STYLE,
    SESSION_KEYS,
    ERROR_MESSAGES,
    FILE_TYPE_MAPPINGS,
    SUPPORTED_FILE_TYPES,
    TEMP_FILE_PREFIX
)

# page configuration
st.set_page_config( 
    page_title=UI_MESSAGES["app_title"],
    page_icon=":memo:",
    layout="wide",
    initial_sidebar_state="expanded"
)

def generate_cover_letter_prompt(resume_text: str, job_description: str) -> str:
    """Generate the prompt for cover letter creation using the template from config."""
    return COVER_LETTER_PROMPT_TEMPLATE.format(
        resume_text=resume_text,
        job_description=job_description,
        word_limit=MAX_WORD_LIMIT
    )

def read_file(file, file_type: int):
    """Read and process uploaded files based on their type."""
    if file is None:
        return ""
    
    if file.type == "application/pdf":
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf', prefix=TEMP_FILE_PREFIX) as tmp_file:
            file.seek(0)  # Reset file pointer to beginning
            tmp_file.write(file.read())
            temp_pdf_path = tmp_file.name
        
        try:
            # Call your existing extract function with the temporary file path
            extracted_text = extract(temp_pdf_path)
            if file_type == 0:
                # Clean the extracted text using the Ollama model
                with st.spinner(UI_MESSAGES["cleaning_resume"]):
                    clean_resume_text = clean_resume(extracted_text)
                return clean_resume_text
            elif file_type == 1:
                # If it's a job description, just return the extracted text
                return extracted_text
             
        except Exception as e:
            st.warning(ERROR_MESSAGES["pdf_extraction"])
            # Fallback to simple PyMuPDF extraction
            file.seek(0)
            file_bytes = file.read()
            reader = fitz.open(stream=file_bytes, filetype="pdf")
            text = ""
            for page in reader:
                text += page.get_text() or ""
            reader.close()
            # If it's a resume, clean the extracted text
            if file_type == 0:
                # Show loading spinner
                with st.spinner(UI_MESSAGES["cleaning_resume"]):
                    clean_resume_text = clean_resume(text)
                return clean_resume_text
            # If it's a job description, just return the extracted text
            else:
                return text
        finally:
            # Always clean up the temporary file
            if os.path.exists(temp_pdf_path):
                os.unlink(temp_pdf_path)
    
    elif file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        doc = Document(file)
        return "\n".join([para.text for para in doc.paragraphs])
    elif file.type == "text/plain":
        return file.read().decode("utf-8")
    else:
        st.error(ERROR_MESSAGES["file_processing"])
        return ""

def query_ollama(prompt):
    """Query the Ollama API with the given prompt."""
    headers = {
        "Content-Type": "application/json"
    }

    # Payload to send to the API (including your prompt)
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
            return result['response']
        else:
            error_msg = ERROR_MESSAGES["api_error"].format(
                status_code=response.status_code,
                error_text=response.text
            )
            st.error(error_msg)
            return error_msg
    except Exception as e:
        error_msg = ERROR_MESSAGES["general_error"].format(error=str(e))
        st.error(error_msg)
        return error_msg
    
def display_text(response: str, typing_speed: float = TYPING_SPEED):
    """Display the generated text in a Streamlit app, preserving line breaks and formatting."""
    # Get the placeholder from session state
    placeholder = st.session_state[SESSION_KEYS["cover_letter_placeholder"]]

    # Wrap everything in a centered container with nice styling
    styled_container = COVER_LETTER_STYLE["container"]
    closing_container = COVER_LETTER_STYLE["container_end"]
    
    # Simulate typing effect, preserving original line breaks
    text = ""
    for char in response:
        text += char
        placeholder.markdown(styled_container + text + closing_container, unsafe_allow_html=True)
        time.sleep(typing_speed)
    
    # Store the final displayed text in session state to persist it
    st.session_state[SESSION_KEYS["current_displayed_letter"]] = response

def chat(generated_cover_letter: str):
    """Handle the chat interface for cover letter personalization."""
    if SESSION_KEYS["chat_history"] not in st.session_state:
        st.session_state[SESSION_KEYS["chat_history"]] = [
            {"role": "system", "content": "You are a helpful assistant for cover letter personalization."},
            {"role": "assistant", "content": generated_cover_letter}
        ]

    user_input = st.text_input(UI_MESSAGES["personalization_input"])

    if st.button(UI_MESSAGES["personalization_button"]) and user_input.strip():
        # Add user message to chat history
        st.session_state[SESSION_KEYS["chat_history"]].append({"role": "user", "content": user_input})

        # Build a prompt with chat history for context
        chat_prompt = PERSONALIZATION_PROMPT_TEMPLATE.format(
            current_cover_letter=st.session_state[SESSION_KEYS["chat_history"]][-2]['content'],
            user_request=user_input
        )

        # Show loading spinner for personalization
        with st.spinner(UI_MESSAGES["personalizing_letter"]):
            # Get the updated cover letter from Ollama
            updated_letter = query_ollama(chat_prompt)
            st.session_state[SESSION_KEYS["chat_history"]].append({"role": "assistant", "content": updated_letter})

            # Update the cover letter display at the top
            display_text(updated_letter)

    # Always ensure the current letter is displayed
    elif SESSION_KEYS["current_displayed_letter"] in st.session_state:
        styled_container = COVER_LETTER_STYLE["container"]
        closing_container = COVER_LETTER_STYLE["container_end"]
        st.session_state[SESSION_KEYS["cover_letter_placeholder"]].markdown(
            styled_container + st.session_state[SESSION_KEYS["current_displayed_letter"]] + closing_container, 
            unsafe_allow_html=True
        )

def initialize_session_state():
    """Initialize all session state variables."""
    session_defaults = {
        SESSION_KEYS["cover_letter_placeholder"]: st.empty(),
        SESSION_KEYS["processed_resume_text"]: "",
        SESSION_KEYS["processed_job_description"]: "",
        SESSION_KEYS["last_resume_file_name"]: "",
        SESSION_KEYS["last_job_file_name"]: "",
    }
    
    for key, default_value in session_defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value

def main():
    """Main application function."""
    st.markdown(
        f"""
        <h1 style='text-align: center;'>{UI_MESSAGES["app_title"]}</h1>
        <p style='text-align: center;'>{UI_MESSAGES["app_description"]}</p>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar for file uploads
    st.sidebar.header("Upload Your Resume")
    resume_file = st.sidebar.file_uploader(
        UI_MESSAGES["resume_upload_label"], 
        type=SUPPORTED_FILE_TYPES
    )
    st.sidebar.markdown("---")
    st.sidebar.header("Or Paste Resume Text")
    resume_text_input = st.sidebar.text_area(
        UI_MESSAGES["resume_text_label"],
        height=200,
        key=SESSION_KEYS["resume_text_input"]
    )

    st.sidebar.header("Upload Job Description")
    job_file = st.sidebar.file_uploader(
        UI_MESSAGES["job_upload_label"], 
        type=SUPPORTED_FILE_TYPES
    )
    st.sidebar.markdown("---")
    st.sidebar.header("Or Paste Job Description Text")
    job_description_input = st.sidebar.text_area(
        UI_MESSAGES["job_text_label"],
        height=200,
        key=SESSION_KEYS["job_description_input"]
    )

    # Use the pasted text if available, otherwise use cached or process files
    resume_text = resume_text_input.strip() if resume_text_input else ""    
    job_description = job_description_input.strip() if job_description_input else ""

    # Process resume file only if no text is pasted and file has changed
    if resume_file and not resume_text:
        current_resume_file_name = resume_file.name
        # Only process if it's a new file or not processed before
        if (current_resume_file_name != st.session_state[SESSION_KEYS["last_resume_file_name"]] or 
            not st.session_state[SESSION_KEYS["processed_resume_text"]]):
            resume_text = read_file(resume_file, 0)
            st.session_state[SESSION_KEYS["processed_resume_text"]] = resume_text
            st.session_state[SESSION_KEYS["last_resume_file_name"]] = current_resume_file_name
        else:
            # Use cached processed text
            resume_text = st.session_state[SESSION_KEYS["processed_resume_text"]]
    
    # Process job description file only if no text is pasted and file has changed
    if job_file and not job_description:
        current_job_file_name = job_file.name
        # Only process if it's a new file or not processed before
        if (current_job_file_name != st.session_state[SESSION_KEYS["last_job_file_name"]] or 
            not st.session_state[SESSION_KEYS["processed_job_description"]]):
            job_description = read_file(job_file, 1)
            st.session_state[SESSION_KEYS["processed_job_description"]] = job_description
            st.session_state[SESSION_KEYS["last_job_file_name"]] = current_job_file_name
        else:
            # Use cached processed text
            job_description = st.session_state[SESSION_KEYS["processed_job_description"]]

    # Clear cached data when text is pasted (overrides file upload)
    if resume_text_input.strip():
        st.session_state[SESSION_KEYS["processed_resume_text"]] = ""
        st.session_state[SESSION_KEYS["last_resume_file_name"]] = ""
    if job_description_input.strip():
        st.session_state[SESSION_KEYS["processed_job_description"]] = ""
        st.session_state[SESSION_KEYS["last_job_file_name"]] = ""
    
    # Check if both files are uploaded
    if not resume_text:
        st.sidebar.error(UI_MESSAGES["resume_missing"])
    elif not job_description:
        st.sidebar.error(UI_MESSAGES["job_missing"])
    else:
        # Show success messages
        if resume_text:
            st.sidebar.success(UI_MESSAGES["resume_ready"])
        if job_description:
            st.sidebar.success(UI_MESSAGES["job_ready"])

    # Show appropriate info messages
    if not resume_text and not job_description:
        st.info(UI_MESSAGES["upload_both"])
    elif not resume_text:
        st.info(UI_MESSAGES["upload_resume"])
    elif not job_description:
        st.info(UI_MESSAGES["upload_job"])

    if resume_text and job_description:
        # Add Create Button in sidebar
        st.sidebar.markdown("---")
        create_button = st.sidebar.button(UI_MESSAGES["generate_button"], type="primary", use_container_width=True)

        # Generate cover letter only when button is clicked and both files are available
        if create_button and resume_text and job_description:
            # Show loading spinner
            with st.spinner(UI_MESSAGES["generating_letter"]):
                prompt = generate_cover_letter_prompt(resume_text, job_description)
                print(f"Generated prompt: {prompt}")  # Debugging line
                generated_cover_letter = query_ollama(prompt)
                
                # Store the generated cover letter in session state
                st.session_state[SESSION_KEYS["generated_cover_letter"]] = generated_cover_letter
                st.session_state[SESSION_KEYS["cover_letter_generated"]] = True
                
                # Initialize chat history
                st.session_state[SESSION_KEYS["chat_history"]] = [
                    {"role": "system", "content": "You are a helpful assistant for cover letter personalization."},
                    {"role": "assistant", "content": generated_cover_letter}
                ]
                
                # Display the letter
                display_text(generated_cover_letter)

        # Display existing cover letter if already generated
        elif SESSION_KEYS["cover_letter_generated"] in st.session_state and st.session_state[SESSION_KEYS["cover_letter_generated"]]:
            # Always display the most current letter
            if SESSION_KEYS["current_displayed_letter"] in st.session_state:
                current_letter = st.session_state[SESSION_KEYS["current_displayed_letter"]]
            else:
                current_letter = st.session_state[SESSION_KEYS["chat_history"]][-1]["content"]
                st.session_state[SESSION_KEYS["current_displayed_letter"]] = current_letter
                
            styled_container = COVER_LETTER_STYLE["container"]
            closing_container = COVER_LETTER_STYLE["container_end"]
            st.session_state[SESSION_KEYS["cover_letter_placeholder"]].markdown(
                styled_container + current_letter + closing_container, 
                unsafe_allow_html=True
            )

        # Show personalization chat only after cover letter is generated
        if SESSION_KEYS["cover_letter_generated"] in st.session_state and st.session_state[SESSION_KEYS["cover_letter_generated"]]:
            # Add a chat interface for further personalization
            st.markdown("---")
            st.header(UI_MESSAGES["personalization_header"])
            chat(st.session_state[SESSION_KEYS["generated_cover_letter"]])

if __name__ == "__main__":
    main()