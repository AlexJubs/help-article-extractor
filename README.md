# Scraping and Chunking: Mini Project

## Overview

This project is designed to scrape a public knowledge base (e.g., the Notion Help Center), extract core text content, and chunk it into smaller, logically grouped sections for better readability and processing. The program ensures content is clean, well-organized, and adheres to specified chunking guidelines.

---

## Features

1. **Scrape Help Center Articles**:
   - Extracts sub-pages, help articles, and their content from the Notion Help Center.

2. **Content Processing**:
   - Extracts and organizes text, preserving headers, paragraphs, and lists.
   - Avoids splitting related content mid-list or mid-section.

3. **Content Chunking**:
   - Splits articles into coherent chunks (~750 characters), ensuring context is preserved.

4. **Optional Prettification**:
   - Utilizes OpenAI's GPT-3.5-turbo model to clean and structure text for professional output.

5. **Interactive Mode**:
   - Allows for reviewing and prettifying content on a per-article basis.

---

## Setup

1. **Set OpenAI API Key**:
   - Export your OpenAI API key as an environment variable:
     ```bash
     export OPENAI_API_KEY="your_openai_api_key"
     ```

2. **Install Poetry**:
   ```bash
   pipx install poetry
   ```

3. **Install Dependencies**:
   ```bash
   poetry install
   ```

4. **Run the Program**:
   ```bash
   python script_name.py
   ```

---

## Usage

1. **Run the Program**:
   - Start by scraping the main Notion Help Center:
     ```bash
     poetry run python main.py
     ```

2. **Interactive Options**:
   - Decide whether to review and prettify articles individually.

3. **Output**:
   - The program returns an array of prettified chunks, ready for downstream use in RAG systems or other applications.

---

