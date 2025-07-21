# American Express AI Banking Chatbot Documentation

## 1. Overview

This project is an AI-powered banking chatbot built with Streamlit and powered by Google's Gemini model via the OpenRouter API. It simulates a conversational banking experience, allowing users to register, log in, and perform various banking operations through a chat interface. The chatbot leverages a tool-based architecture, where the Large Language Model (LLM) can call backend Python functions to fetch data, perform calculations, and execute transactions.

---

## 2. Features

- **User Management**: New user registration and login for existing customers.
- **Conversational AI**: Natural language interface for all banking tasks.
- **Session Management**: Persistent user sessions and chat history.
- **Tool-Based Functions**: The chatbot can use backend tools to:
  - Fetch user profiles, account balances, loan histories, and fixed deposit details.
  - Calculate loan EMIs for various loan types (Personal, Home, Student).
  - Approve loans based on backend business logic.
  - Create new fixed deposits.
- **Data Persistence**: All user data, loan records, and fixed deposit information are stored in CSV files.
- **Modular Architecture**: The codebase is separated into modules for UI, chatbot logic, banking rules, and data management.

---

## 3. Project Structure

```
v2/
├── app.py                  # Main Streamlit application, handles UI and session state.
├── chatbot.py              # Manages all interaction with the LLM, defines tools, and contains the agentic loop.
├── bank.py                 # Core banking business logic (loan calculations, approvals, etc.).
├── data.py                 # Handles all data persistence (read/write to CSV files).
├── bank_users.csv          # Stores user profile data.
├── approved_loans.csv      # Stores records of all approved loans.
├── fixed_deposits.csv      # Stores records of all created fixed deposits.
├── requirements.txt        # Lists all Python package dependencies.
└── .env.local              # Stores the API key for OpenRouter (must be created manually).
```

---

## 4. Setup and Installation

Follow these steps to run the project locally.

### Prerequisites

- Python 3.8+
- A virtual environment tool (e.g., `venv`)

### Installation Steps

1.  **Set up the project folder**: Ensure all the project files are in a single directory (e.g., `v2/`).

2.  **Create and activate a virtual environment**:
    ```sh
    # Navigate to your project directory
    cd path/to/your/project

    # Create a virtual environment
    python -m venv bot

    # Activate it
    # On Windows
    .\bot\Scripts\activate
    # On macOS/Linux
    source bot/bin/activate
    ```

3.  **Install dependencies**:
    ```sh
    pip install -r requirements.txt
    ```

4.  **Create the environment file**:
    - In the `v2/` directory, create a file named `.env.local`.
    - Add your OpenRouter API key to this file:
      ```
      API_KEY=sk-or-v1-your-openrouter-api-key-here
      ```

5.  **Run the application**:
    ```sh
    streamlit run app.py
    ```
    The application will open in your default web browser.

---

## 5. How It Works

The application follows a modular, tool-based architecture.

1.  **Frontend (`app.py`)**:
    - Built with Streamlit, providing the user interface, sidebar navigation, and session management (`st.session_state`).
    - It captures user input and displays the chat history.
    - When a user sends a message, it calls the `get_chatbot_response_with_tools` function from `chatbot.py`.

2.  **Chatbot Logic (`chatbot.py`)**:
    - This is the core of the AI interaction. It defines a set of `tools` (Python functions) that the LLM can use.
    - When a user query is received, it's sent to the Gemini model on OpenRouter along with the list of available tools.
    - The LLM decides if it needs to use a tool to answer the query. If so, it returns a `tool_calls` request.
    - An **agentic loop** processes this request, calls the appropriate Python function (e.g., `approve_loan`), and sends the result back to the LLM.
    - The LLM then uses the tool's result to formulate a final, natural language response for the user.

3.  **Backend Logic (`bank.py` & `data.py`)**:
    - `bank.py`: Implements the actual business logic for each tool, such as calculating EMI or checking loan eligibility against salary.
    - `data.py`: Handles all direct interactions with the CSV files, ensuring data is read and written correctly. This centralizes data persistence.

---

## 6. Available Chatbot Tools

The chatbot has access to the following backend functions:

| Function Name              | Description                                                              | Parameters                                                                |
| -------------------------- | ------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| `get_user_profile`         | Fetches the complete profile of the logged-in user.                      | None                                                                      |
| `get_balance`              | Retrieves the current account balance for the user.                      | `account_number`                                                          |
| `get_loan_history`         | Gets a list of all approved loans for the user.                          | `account_number`                                                          |
| `calculate_loan_emi`       | Calculates the monthly EMI and total interest for a specified loan.      | `principal`, `years`, `loan_type`, `monthly_salary`                       |
| `approve_loan`             | Processes a loan application and approves or rejects it.                 | `account_number`, `loan_type`, `principal`, `years`, `monthly_salary`     |
| `create_fixed_deposit`     | Creates a new fixed deposit record for the user.                         | `account_number`, `amount`, `years`                                       |

---

## 7. Future Improvements

- **Database Migration**: Move from CSV files to a more robust database system like SQLite or PostgreSQL for better scalability and data integrity.
- **User Authentication**: Implement password-based authentication instead of just using an account number.
- **Enhanced Tools**: Add more banking tools like money transfers, bill payments, or credit card management.
- **Unit Testing**: Develop a suite of unit tests for the backend logic in `bank.py` and `data.py` to ensure reliability.
- **Admin Dashboard**: Create a separate interface for bank administrators to view user data, manage loans, and oversee operations. 