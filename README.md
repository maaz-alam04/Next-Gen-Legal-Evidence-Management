
# Next Gen Legal Evidence Management System

An AI-powered system for analyzing video evidence, generating structured investigation reports, and enabling intelligent querying through a Retrieval-Augmented Generation (RAG) pipeline.

## Overview

The Next Gen Legal Evidence Management System is designed to support digital forensic workflows by automating the analysis of video evidence and improving information retrieval. The system processes uploaded video files, extracts relevant information, generates structured reports, and allows users to interact with the generated content through a conversational chatbot.

## Features

- Video evidence upload and processing
- AI-based generation of structured investigation reports
- Semantic search using vector embeddings
- Conversational querying through a RAG-based chatbot
- PDF report generation and download
- Context-aware responses using conversation memory

## Tech Stack

- Frontend: Streamlit
- AI Model: Google Gemini API
- Framework: LangChain
- Vector Database: FAISS
- Embeddings: Google Generative AI Embeddings
- PDF Generation: ReportLab
- Environment Management: python-dotenv

## Project Workflow

1. The user uploads a video file through the Streamlit interface.
2. The video is sent to the Gemini API for analysis.
3. A structured report is generated from the uploaded video.
4. The report is converted into embeddings and stored in FAISS.
5. The user can ask questions about the report using the chatbot.
6. The system retrieves relevant information from the vector store and generates a response.
7. The final report can be downloaded as a PDF file.

## Project Structure

```bash
.
├── app.py
├── pages/
│   ├── report_generation.py
│   └── chat.py
├── vectorstore.index/
├── requirements.txt
├── .env
└── README.md
```

## Installation

### Prerequisites

* Python 3.8 or higher
* A valid Gemini API key

### Clone the Repository

```bash
git clone https://github.com/your-username/next-gen-legal-evidence-management-system.git
cd next-gen-legal-evidence-management-system
```

### Create and Activate a Virtual Environment

Windows:

```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv venv
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

## Running the Application

```bash
streamlit run app.py
```

## Usage

1. Open the application in your browser.
2. Go to the Report Generation page.
3. Upload a supported video file.
4. Click Generate Report.
5. View the generated report.
6. Download the report as a PDF.
7. Go to the Chat page and ask questions related to the report.

## Testing

The system was tested for the following functionalities:

* Successful application launch
* Video upload and processing
* Report generation
* PDF export
* Vector store creation and loading
* Chat-based querying
* Context retention in multi-turn conversations
* Error handling for invalid or missing input

## Limitations

* Accuracy depends on the quality of the uploaded video
* Processing time may vary based on file size and API response time
* Internet connectivity is required for API-based processing
* The system is currently optimized for a single-report workflow

## Future Scope

* Real-time video analysis
* Face recognition and license plate detection
* Blockchain-based chain of custody
* Role-based access control
* Cloud deployment
* Mobile application support
* Multimodal RAG for image, audio, and video evidence

## License

This project is intended for academic and research purposes.

## Author

- Mohammed Maaz Alam
- Mohammed Abdul Kalam Khan
- Mahammed Saadullah

