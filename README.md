# Cover Letter Generator 📝

A smart, personalized cover letter generator that leverages the power of Ollama's local LLM models to create tailored cover letters based on your resume and job descriptions.

## 🌟 Features

- **Smart Resume Processing**: Automatically extracts and cleans text from PDF, DOCX, and TXT files
- **Multiple Input Methods**: Upload files or paste text directly
- **Local LLM Integration**: Uses Ollama API for privacy-focused, local processing
- **Real-time Personalization**: Interactive chat interface for further customization
- **Professional Formatting**: Generates email-formatted cover letters with proper structure
- **Typing Animation**: Smooth display of generated content
- **Session Management**: Caches processed files to avoid reprocessing

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **LLM**: Ollama API with Gemma:2b model
- **PDF Processing**: PyMuPDF (fitz), custom extraction module
- **Document Processing**: python-docx
- **Backend**: Python 3.7+

## 📋 Prerequisites

1. **Ollama Installation**: Install Ollama on your system
   ```bash
   # Visit https://ollama.ai to download and install
   ```

2. **Model Setup**: Pull the Gemma:2b model
   ```bash
   ollama pull gemma:2b
   ```

3. **Python Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Installation

1. **Clone the repository**
   ```bash
   git clone <your-repository-url>
   cd cover-letter-generator
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit requests PyMuPDF python-docx
   ```

3. **Start Ollama service**
   ```bash
   ollama serve
   ```

4. **Run the application**
   ```bash
   streamlit run letter_creator.py
   ```

## 📁 Project Structure

```
cover-letter-generator/
├── letter_creator.py          # Main Streamlit application
├── extract_resume.py          # PDF text extraction utilities
├── resume_cleaner.py          # Resume text cleaning and processing
├── requirements.txt           # Python dependencies
└── README.md                 # Project documentation
```

## 🎯 Usage

### Step 1: Upload Your Resume
- Upload your resume file (PDF, DOCX, or TXT)
- Or paste your resume text directly in the text area

### Step 2: Add Job Description
- Upload the job description file (PDF, DOCX, or TXT)
- Or paste the job description text directly

### Step 3: Generate Cover Letter
- Click "🚀 Generate Cover Letter"
- Wait for the AI to process and generate your personalized cover letter

### Step 4: Personalize Further (Optional)
- Use the chat interface to request modifications
- Examples: "Make it more formal", "Add emphasis on teamwork", "Make it shorter"

## ⚙️ Configuration

### Ollama Settings
You can modify the Ollama configuration in `letter_creator.py`:

```python
# Default Ollama API endpoint
Ollama_API_URL = "http://localhost:11434/api/generate"

# Model configuration
MODEL_NAME = "gemma:2b"  # Change to your preferred model

# Generation parameters
"temperature": 0.7,  # Creativity level (0.0-1.0)
"top_p": 0.9,       # Diversity control (0.0-1.0)
```

### Supported File Types
- **PDF**: Processed using PyMuPDF with fallback extraction
- **DOCX**: Microsoft Word documents
- **TXT**: Plain text files

## 🔧 Key Functions

### `generate_cover_letter_prompt(resume_text, job_description)`
Creates a comprehensive prompt for the LLM with specific instructions for:
- Professional tone and format
- Technology matching between resume and job description
- Enthusiasm for learning new technologies
- Concise, email-format output

### `read_file(file, file_type)`
Handles multiple file formats with intelligent processing:
- PDF extraction with cleanup
- DOCX paragraph extraction
- TXT direct reading
- Resume cleaning for type 0 (resume files)

### `query_ollama(prompt)`
Communicates with the Ollama API:
- Sends structured requests
- Handles response parsing
- Error handling and reporting

### `display_text(response, typing_speed)`
Creates an engaging user experience:
- Typing animation effect
- Professional styling
- Session state management

## 🎨 UI Features

- **Sidebar Navigation**: Clean file upload and text input areas
- **Real-time Feedback**: Success/error messages and loading spinners
- **Responsive Design**: Professional styling with centered layout
- **Interactive Chat**: Post-generation customization interface

## 🛡️ Privacy & Security

- **Local Processing**: All data processing happens locally using Ollama
- **No Data Storage**: Files are processed in memory, not saved permanently
- **Session-based**: Data exists only during your session

## 🔍 Troubleshooting

### Common Issues

1. **Ollama Connection Error**
   - Ensure Ollama is running: `ollama serve`
   - Check if the model is installed: `ollama list`

2. **File Processing Issues**
   - Ensure files are not corrupted
   - Check file size limitations
   - Verify file format compatibility

3. **Performance Issues**
   - Consider using a more powerful model
   - Adjust temperature and top_p parameters
   - Ensure sufficient system resources

## 📊 Performance Tips

- **Model Selection**: Gemma:2b is efficient; consider larger models for better quality
- **File Size**: Smaller files process faster
- **Prompt Engineering**: The built-in prompt is optimized for best results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit changes: `git commit -m 'Add feature'`
4. Push to branch: `git push origin feature-name`
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for providing local LLM capabilities
- [Streamlit](https://streamlit.io) for the amazing web framework
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing

## 📞 Support

If you encounter any issues or have questions:
1. Check the troubleshooting section
2. Review Ollama documentation
3. Open an issue in the repository

---

**Made with ❤️ for job seekers everywhere**