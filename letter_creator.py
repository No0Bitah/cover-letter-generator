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

# Define the Ollama API endpoint and the model name
Ollama_API_URL = "http://localhost:11434/api/generate"  # Default endpoint for Ollama
MODEL_NAME = "gemma:2b"  # Replace with your model name if different    

# page configuration
st.set_page_config( 
    page_title="Cover Letter Generator",
    page_icon=":memo:",
    layout="wide",
    initial_sidebar_state="expanded"
)


def generate_cover_letter_prompt(resume_text: str, job_description: str) -> str:
    prompt = f"""
You are a professional cover letter writer. Write a compelling, personalized cover letter based on the resume and job description provided.

⚠️ Important instructions:
The goal is to create a professional, eager-to-learn, and concise cover letter.
    The cover letter must:

    1. Only include the technologies and experiences mentioned in the resume.
    2. Connect the technologies in the resume with those mentioned in the job description.
    3. If there are any technologies in the job description not mentioned in the resume, politely mention that the applicant is willing and eager to learn them.
    4. Make the tone of the cover letter enthusiastic and focused on giving their best to the work.
    5. Format the cover letter to be brief, as most hiring teams prefer short and to-the-point emails.
    6. Use a professional tone, avoiding any casual language and use words not more than 200.
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
    return prompt

def read_file(file, file_type: int):
    if file is None:
        return ""
    
    if file.type == "application/pdf":
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            file.seek(0)  # Reset file pointer to beginning
            tmp_file.write(file.read())
            temp_pdf_path = tmp_file.name
        
        try:
            # Call your existing extract function with the temporary file path
            extracted_text = extract(temp_pdf_path)
            if file_type == 0:
                # Clean the extracted text using the Ollama model
                with st.spinner("Cleaning and processing your resume..."):
                    clean_resume_text = clean_resume(extracted_text)
                return clean_resume_text
            elif file_type == 1:
                # If it's a job description, just return the extracted text
                return extracted_text
             
        except Exception as e:
            print(f"Error extracting PDF: {e}")
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
                with st.spinner("Cleaning and processing your resume..."):
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
        return ""

# Function to call the Ollama API
def query_ollama(prompt):
    headers = {
        "Content-Type": "application/json"
    }

    # Payload to send to the API (including your prompt)
    data = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.7,  # Adjust temperature for creativity
        "top_p": 0.9,  # Adjust top_p for diversity
        }

    try:
        response = requests.post(Ollama_API_URL, headers=headers, data=json.dumps(data))
        
        
        # Check if the response is successful
        if response.status_code == 200:
            result = response.json()
            return result['response']
        else:
            return f"Error: {response.status_code}, {response.text}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
    
def display_text(response: str, typing_speed: float = 0.03):
    """Display the generated text in a Streamlit app, preserving line breaks and formatting."""
    # Get the placeholder from session state
    placeholder = st.session_state.cover_letter_placeholder

    # Wrap everything in a centered container with nice styling
    styled_container = """
    <div style='display: flex; justify-content: center; margin-top: 20px;'>
        <div style='max-width: 800px; background-color: #f8f9fa; padding: 20px;
                    border-radius: 10px; font-family: Arial, sans-serif;
                    white-space: pre-wrap; line-height: 1.6; font-size: 16px; color: #333;'>
    """
    closing_container = "</div></div>"
    
    # Simulate typing effect, preserving original line breaks
    text = ""
    for char in response:
        text += char
        placeholder.markdown(styled_container + text + closing_container, unsafe_allow_html=True)
        time.sleep(typing_speed)
    
    # Store the final displayed text in session state to persist it
    st.session_state.current_displayed_letter = response


def chat(generated_cover_letter: str):
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            {"role": "system", "content": "You are a helpful assistant for cover letter personalization."},
            {"role": "assistant", "content": generated_cover_letter}
        ]

    user_input = st.text_input("Ask to personalize or modify your cover letter (e.g., 'Make it more formal', 'Add a sentence about teamwork'):")

    if st.button("Submit Personalization") and user_input.strip():
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})

        # Build a prompt with chat history for context
        chat_prompt = (     
            "You are a professional cover letter writer. Here is the current cover letter:\n\n"
            f"{st.session_state.chat_history[-2]['content']}\n\n"
            
            "The user has requested the following personalization:\n"
            f"{user_input}\n\n"
            "Please update the cover letter accordingly, keeping it concise, short and professional.\n\n"
        )

        # Show loading spinner for personalization
        with st.spinner("Personalizing your cover letter..."):
            # Get the updated cover letter from Ollama
            updated_letter = query_ollama(chat_prompt)
            st.session_state.chat_history.append({"role": "assistant", "content": updated_letter})

            # Update the cover letter display at the top
            display_text(updated_letter)
            
            # Save the updated letter
            with open("generated_cover_letter.txt", "w", encoding="utf-8") as f:
                f.write(updated_letter)

    # Always ensure the current letter is displayed
    elif "current_displayed_letter" in st.session_state:
        styled_container = """
        <div style='display: flex; justify-content: center; margin-top: 20px;'>
            <div style='max-width: 800px; background-color: #f8f9fa; padding: 20px;
                        border-radius: 10px; font-family: Arial, sans-serif;
                        white-space: pre-wrap; line-height: 1.6; font-size: 16px; color: #333;'>
        """
        closing_container = "</div></div>"
        st.session_state.cover_letter_placeholder.markdown(
            styled_container + st.session_state.current_displayed_letter + closing_container, 
            unsafe_allow_html=True
        )


# Example usage of the function
if __name__ == "__main__":
    st.markdown(
        """
        <h1 style='text-align: center;'>Cover Letter Generator</h1>
        <p style='text-align: center;'>This tool generates a personalized cover letter based on your resume and job description.</p>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown("---")
    
    # Initialize the cover_letter_placeholder at the top
    if "cover_letter_placeholder" not in st.session_state:
        st.session_state.cover_letter_placeholder = st.empty()
    
    # Initialize session state for caching processed files
    if "processed_resume_text" not in st.session_state:
        st.session_state.processed_resume_text = ""
    if "processed_job_description" not in st.session_state:
        st.session_state.processed_job_description = ""
    if "last_resume_file_name" not in st.session_state:
        st.session_state.last_resume_file_name = ""
    if "last_job_file_name" not in st.session_state:
        st.session_state.last_job_file_name = ""
    
    # Sidebar for file uploads
    st.sidebar.header("Upload Your Resume")
    resume_file = st.sidebar.file_uploader(
        "Choose your resume file (PDF, DOCX, or TXT)", 
        type=["pdf", "docx", "txt"]
    )
    st.sidebar.markdown("---")
    st.sidebar.header("Or Paste Resume Text")
    resume_text_input = st.sidebar.text_area(
        "Paste your resume text here (optional, overrides uploaded file)",
        height=200,
        key="resume_text_input"
    )

    st.sidebar.header("Upload Job Description")
    job_file = st.sidebar.file_uploader(
        "Choose the job description file (PDF, DOCX, or TXT)", 
        type=["pdf", "docx", "txt"]
    )
    st.sidebar.markdown("---")
    st.sidebar.header("Or Paste Job Description Text")
    job_description_input = st.sidebar.text_area(
        "Paste the job description here (optional, overrides uploaded file)",
        height=200,
        key="job_description_input"
    )

    # Use the pasted text if available, otherwise use cached or process files
    resume_text = resume_text_input.strip() if resume_text_input else ""    
    job_description = job_description_input.strip() if job_description_input else ""

    # Process resume file only if no text is pasted and file has changed
    if resume_file and not resume_text:
        current_resume_file_name = resume_file.name
        # Only process if it's a new file or not processed before
        if (current_resume_file_name != st.session_state.last_resume_file_name or 
            not st.session_state.processed_resume_text):
            resume_text = read_file(resume_file, 0)
            st.session_state.processed_resume_text = resume_text
            st.session_state.last_resume_file_name = current_resume_file_name
        else:
            # Use cached processed text
            resume_text = st.session_state.processed_resume_text
    
    # Process job description file only if no text is pasted and file has changed
    if job_file and not job_description:
        current_job_file_name = job_file.name
        # Only process if it's a new file or not processed before
        if (current_job_file_name != st.session_state.last_job_file_name or 
            not st.session_state.processed_job_description):
            job_description = read_file(job_file, 1)
            st.session_state.processed_job_description = job_description
            st.session_state.last_job_file_name = current_job_file_name
        else:
            # Use cached processed text
            job_description = st.session_state.processed_job_description

    # Clear cached data when text is pasted (overrides file upload)
    if resume_text_input.strip():
        st.session_state.processed_resume_text = ""
        st.session_state.last_resume_file_name = ""
    if job_description_input.strip():
        st.session_state.processed_job_description = ""
        st.session_state.last_job_file_name = ""
    
    # Check if both files are uploaded
    if not resume_text:
        st.sidebar.error("Please upload your resume file or paste resume text.")
    elif not job_description:
        st.sidebar.error("Please upload the job description file or paste job description text.")
    else:
        # Show success messages
        if resume_text:
            st.sidebar.success("✅ Resume ready!")
        if job_description:
            st.sidebar.success("✅ Job description ready!")

    # Show appropriate info messages
    if not resume_text and not job_description:
        st.info("👆 Please upload both your resume and job description files from the sidebar, or paste the text directly, then click 'Generate Cover Letter'.")
    elif not resume_text:
        st.info("👆 Please upload your resume file or paste resume text from the sidebar, then click 'Generate Cover Letter'.")
    elif not job_description:
        st.info("👆 Please upload the job description file or paste job description text from the sidebar, then click 'Generate Cover Letter'.")

    if resume_text and job_description:
        # Add Create Button in sidebar
        st.sidebar.markdown("---")
        create_button = st.sidebar.button("🚀 Generate Cover Letter", type="primary", use_container_width=True)

        # Generate cover letter only when button is clicked and both files are available
        if create_button and resume_text and job_description:
            # Show loading spinner
            with st.spinner("Generating your personalized cover letter..."):
                prompt = generate_cover_letter_prompt(resume_text, job_description)
                generated_cover_letter = query_ollama(prompt)
                
                # Store the generated cover letter in session state
                st.session_state.generated_cover_letter = generated_cover_letter
                st.session_state.cover_letter_generated = True
                
                # Initialize chat history
                st.session_state.chat_history = [
                    {"role": "system", "content": "You are a helpful assistant for cover letter personalization."},
                    {"role": "assistant", "content": generated_cover_letter}
                ]
                
                # Display the letter
                display_text(generated_cover_letter)

        # Display existing cover letter if already generated
        elif "cover_letter_generated" in st.session_state and st.session_state.cover_letter_generated:
            # Always display the most current letter
            if "current_displayed_letter" in st.session_state:
                current_letter = st.session_state.current_displayed_letter
            else:
                current_letter = st.session_state.chat_history[-1]["content"]
                st.session_state.current_displayed_letter = current_letter
                
            styled_container = """
            <div style='display: flex; justify-content: center; margin-top: 20px;'>
                <div style='max-width: 800px; background-color: #f8f9fa; padding: 20px;
                            border-radius: 10px; font-family: Arial, sans-serif;
                            white-space: pre-wrap; line-height: 1.6; font-size: 16px; color: #333;'>
            """
            closing_container = "</div></div>"
            st.session_state.cover_letter_placeholder.markdown(
                styled_container + current_letter + closing_container, 
                unsafe_allow_html=True
            )

        # Show personalization chat only after cover letter is generated
        if "cover_letter_generated" in st.session_state and st.session_state.cover_letter_generated:
            # Add a chat interface for further personalization
            st.markdown("---")
            st.header("Personalize Your Cover Letter Further")
            chat(st.session_state.generated_cover_letter)