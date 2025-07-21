# American Express AI Banking Chatbot

This project is an AI-powered banking chatbot built with Streamlit and powered by Google's Gemini model via the OpenRouter API. It simulates a conversational banking experience, allowing users to perform various banking operations through a chat interface.

---

## Features

- **Conversational AI**: Natural language interface for all banking tasks.
- **User Management**: Simple registration and login for new and existing customers.
- **Tool-Based Functions**: The chatbot can use backend tools to:
  - Fetch user profiles, balances, and transaction histories.
  - Calculate loan EMIs.
  - Approve loans and create fixed deposits.
- **Modular and Extendable**: Clean architecture makes it easy to add new features and banking tools.

---

## Setup and Installation

Follow these steps to run the project locally.

### 1. Prerequisites

- Python 3.8+
- A virtual environment tool (e.g., `venv`)

### 2. Installation Steps

1.  **Clone the repository** (or download the source code).

2.  **Create and activate a virtual environment**:
    ```sh
    # Navigate to your project directory
    cd path/to/your/project

    # Create a virtual environment (e.g., named "bot")
    python -m venv bot

    # Activate it
    # On Windows:
    .\bot\Scripts\activate
    # On macOS/Linux:
    source bot/bin/activate
    ```

3.  **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4.  **Create the environment file**:
    - In the project root directory, create a file named `.env.local`.
    - Add your OpenRouter API key to this file:
      ```
      API_KEY=sk-or-v1-your-openrouter-api-key-here
      ```

5.  **Run the application**:
    ```sh
    streamlit run app.py
    ```
    The application will open in your default web browser. For more detailed documentation on the project architecture and available tools, please see `documentation.md`.
