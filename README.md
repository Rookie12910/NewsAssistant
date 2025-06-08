# Bangladesh News Assistant

This project is a web-based news assistant that uses Retrieval-Augmented Generation (RAG) to answer questions about recent news from major Bangladeshi English-language newspapers. The application is built with Streamlit and uses Google's Gemini AI for language understanding and generation.

## Features

-   **Q&A Interface**: Ask questions in natural language about recent news.
-   **Dynamic Data Updates**: Scrape the latest news articles directly from the sources with the click of a button.
-   **Source Citing**: The AI assistant cites the source of the information in its answers.
-   **Conversation History**: View the history of your conversation with the assistant.

## How It Works

The application follows a RAG architecture:

1.  **Scraping (`scrape.py`)**: A Selenium-based scraper fetches the latest news articles from "The Daily Star" and "Prothom Alo (English)". The scraped articles are saved as a JSON file in the `data/` directory.
2.  **Indexing (`rag.py`)**:
    * The news articles are loaded from the JSON file.
    * The text is split into smaller, manageable chunks.
    * Google's `embedding-001` model is used to create vector embeddings for each chunk.
    * These embeddings are stored in a ChromaDB vector store for efficient similarity searching.
3.  **Retrieval & Generation (`rag.py` & `app.py`)**:
    * When a user asks a question, the application creates an embedding of the question.
    * The vector store is searched to find the most relevant news chunks (the context).
    * The user's question and the retrieved context are passed to a Google Gemini model via a prompt.
    * The model generates a comprehensive answer based on the provided news articles.
    * The Streamlit app displays the question and the generated answer in a chat-like interface.

## Setup and Installation

Follow these steps to set up and run the project locally.

### 1. Prerequisites

-   Python 3.8+
-   Google Chrome browser installed.
-   ChromeDriver matching your Google Chrome version.

### 2. Clone the Repository

```bash
git clone <repository_url>
cd <repository_name>
### 3. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

# For Windows

```bash
python -m venv venv
venv\Scripts\activate
```

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

### 4. Install Dependencies

Install all the required Python packages using the `requirements.txt` file.

```bash
pip install -r requirements.txt
```

### 5. Set up ChromeDriver

The web scraper (`scrape.py`) uses Selenium to control a Chrome browser.

1.  Download the **ChromeDriver** that matches your installed Google Chrome version from the [official site](https://googlechromelabs.github.io/chrome-for-testing/).
2.  Create a folder named `chromedriver` in the project's root directory.
3.  Extract and place the `chromedriver.exe` (or `chromedriver` for macOS/Linux) file inside the `chromedriver` folder. The final path should be `./chromedriver/chromedriver.exe`.

### 6. Configure Google API Key

The application uses the Google Gemini API. You need to provide an API key.

1.  Create a file named `.env` in the root of the project directory.
2.  Add your Google AI API key to the `.env` file as follows:

    ```
    GOOGLE_API_KEY="YOUR_API_KEY_HERE"
    ```

## Usage

There are two primary ways to run the application.

### Method 1: Run the Streamlit App Directly

The Streamlit app can handle the initial data scraping itself.

1.  Run the Streamlit app from your terminal:

    ```bash
    streamlit run app.py
    ```

2.  Your browser should open with the application running.
3.  On the sidebar, click the **"🔄 Update News Data"** button to scrape the latest news. This may take a few minutes.
4.  Once the data is updated, you can start asking questions in the main chat interface.

### Method 2: Scrape First, Then Run App

You can also run the scraper script manually before starting the app.

1.  **Run the scraper script:** This will fetch news articles and save them to a file in the `data/` directory.

    ```bash
    python scrape.py
    ```

2.  **Run the Streamlit app:** The app will automatically load the most recent news file from the `data/` directory on startup.
    ```bash
    streamlit run app.py
    ```
