import os
import json
import requests
import math
from bank import BankManager
from data import UserDataManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path=".env.local")
API_KEY = os.getenv("API_KEY")
MODEL = "google/gemini-2.0-flash-001"
ENDPOINT = "https://openrouter.ai/api/v1/chat/completions"

# Initialize managers
bank_manager = BankManager()
user_manager = UserDataManager()

# --- Tool Definitions ---
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_user_profile",
            "description": "Get the profile information for the currently logged-in user.",
            "parameters": {
                "type": "object",
                "properties": {},
                "required": []
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_balance",
            "description": "Get the account balance for the currently logged-in user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {"type": "string", "description": "The user's account number."}
                },
                "required": ["account_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_loan_history",
            "description": "Get the loan history for the currently logged-in user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {"type": "string", "description": "The user's account number."}
                },
                "required": ["account_number"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_loan_emi",
            "description": "Calculate the monthly EMI and total interest for a loan.",
            "parameters": {
                "type": "object",
                "properties": {
                    "principal": {"type": "number", "description": "The principal loan amount."},
                    "years": {"type": "number", "description": "The loan duration in years."},
                    "loan_type": {"type": "string", "description": "Type of loan: personal, student, or home."},
                    "monthly_salary": {"type": "number", "description": "Monthly salary (only for personal loans).", "nullable": True}
                },
                "required": ["principal", "years", "loan_type", "monthly_salary"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "approve_loan",
            "description": "Approve a loan for the user based on type of loan, principal, years, and salary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {"type": "string", "description": "The user's account number."},
                    "loan_type": {"type": "string", "description": "Type of loan: personal, student, or home."},
                    "principal": {"type": "number", "description": "The principal loan amount."},
                    "years": {"type": "number", "description": "The loan duration in years."},
                    "monthly_salary": {"type": "number", "description": "Monthly salary (required for personal/home loans).", "nullable": True}
                },
                "required": ["account_number", "loan_type", "principal", "years", "monthly_salary"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "create_fixed_deposit",
            "description": "Create a fixed deposit for the user.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_number": {"type": "string", "description": "The user's account number."},
                    "amount": {"type": "number", "description": "The deposit amount."},
                    "years": {"type": "number", "description": "The duration of the deposit in years."}
                },
                "required": ["account_number", "amount", "years"]
            }
        }
    }
]

# --- Tool Function Implementations ---
def get_user_profile(user_profile):
    acc_no = user_profile.get("account_number", "")
    success, profile = user_manager.login_user(acc_no)
    return profile if success else {}

def get_balance(account_number):
    return {"balance": bank_manager.get_balance(account_number)}

def get_loan_history(account_number):
    return {"loans": bank_manager.get_loan_history(account_number)}

def approve_loan(account_number, loan_type, principal, years, monthly_salary, name=None, credit_score=None, balance=None, account_type=None, branch=None, ifsc=None, phone=None, email=None):
    # Update user info if missing
    user_manager.update_user_info_if_missing(
        account_number,
        name=name,
        credit_score=credit_score,
        balance=balance,
        account_type=account_type,
        branch=branch,
        ifsc=ifsc,
        phone=phone,
        email=email,
        monthly_salary=monthly_salary
    )
    return bank_manager.approve_loan(account_number, loan_type, principal, years, monthly_salary)

def create_fixed_deposit(account_number, amount, years):
    return bank_manager.create_fixed_deposit(account_number, amount, years)

# EMI calculation for different loan types, with debug option
def calculate_loan_emi(principal, years, loan_type, monthly_salary=None, debug=False):
    principal = float(principal)
    years = float(years)
    n = years * 12  # total number of monthly payments
    if loan_type.lower() == "personal":
        r = 0.125 / 12  # monthly rate for personal loan
        emi = bank_manager.calculate_personal_loan_emi(principal, years)
        total_payment = emi * n
        total_interest = total_payment - principal
        if debug:
            print("----- DEBUG: EMI Calculation -----")
            print(f"Loan Type: {loan_type}")
            print(f"Principal: {principal}")
            print(f"Years: {years}")
            print(f"Monthly Rate (r): {r}")
            print(f"Months (n): {n}")
            print(f"Calculated EMI: {emi}")
            print(f"Total Payment: {total_payment}")
            print(f"Total Interest: {total_interest}")
            print("----------------------------------")
        return {"emi": round(emi, 2), "total_interest": round(total_interest, 2)}
    elif loan_type.lower() == "student":
        rate_annual = 8.5 / 100
        r = rate_annual / 12  # monthly rate
        emi = ((principal * r) * ((1 + r) ** n)) / (((1 + r) ** n) - 1)
        total_payment = emi * n
        total_interest = total_payment - principal
        if debug:
            print("----- DEBUG: EMI Calculation -----")
            print(f"Loan Type: {loan_type}")
            print(f"Principal: {principal}")
            print(f"Years: {years}")
            print(f"Monthly Rate (r): {r}")
            print(f"Months (n): {n}")
            print(f"Calculated EMI: {emi}")
            print(f"Total Payment: {total_payment}")
            print(f"Total Interest: {total_interest}")
            print("----------------------------------")
        return {"emi": round(emi, 2), "total_interest": round(total_interest, 2)}
    elif loan_type.lower() == "home":
        rate_annual = 7.2 / 100
        r = rate_annual / 12  # monthly rate
        emi = (principal * r * (1 + r) ** n) / ((1 + r) ** n - 1)
        total_payment = emi * n
        total_interest = total_payment - principal
        if debug:
            print("----- DEBUG: EMI Calculation -----")
            print(f"Loan Type: {loan_type}")
            print(f"Principal: {principal}")
            print(f"Years: {years}")
            print(f"Monthly Rate (r): {r}")
            print(f"Months (n): {n}")
            print(f"Calculated EMI: {emi}")
            print(f"Total Payment: {total_payment}")
            print(f"Total Interest: {total_interest}")
            print("----------------------------------")
        return {"emi": round(emi, 2), "total_interest": round(total_interest, 2)}
    else:
        return {"error": "Unknown loan type. Supported types: personal, student, home."}

# --- Tool Mapping ---
TOOL_MAPPING = {
    "get_user_profile": lambda user_profile: get_user_profile(user_profile),
    "get_balance": lambda account_number: get_balance(account_number),
    "get_loan_history": lambda account_number: get_loan_history(account_number),
    "calculate_loan_emi": lambda principal, years, loan_type, monthly_salary: calculate_loan_emi(principal, years, loan_type, monthly_salary),
    "approve_loan": lambda account_number, loan_type, principal, years, monthly_salary, name=None, credit_score=None, balance=None, account_type=None, branch=None, ifsc=None, phone=None, email=None: approve_loan(account_number, loan_type, principal, years, monthly_salary, name, credit_score, balance, account_type, branch, ifsc, phone, email),
    "create_fixed_deposit": lambda account_number, amount, years: create_fixed_deposit(account_number, amount, years)
}

# --- Main Chatbot Agentic Loop ---
def get_chatbot_response_with_tools(user_input, messages, user_profile):
    system_prompt = """You are a helpful banking assistant. Use tools to answer questions about the user's profile, balance, and loan history.\n\
        You support these services:
1. Student Loans
   - Interest rate: 8.5% per annum (compounded annually)
   - Inputs: principal, repayment years
2. Personal Loans
   - Interest rate: 12.5% per annum (compounded monthly)
   - Inputs: principal, repayment years, salary
   - Rule: Reject if monthly EMI exceeds 60 percent of the user's monthly salary.
3. Home Loans
   - Interest rate: 7.2% per annum (compounded annually)
   - Inputs: loan amount, duration
4. Fixed Deposits
   - Interest rate: 6.8% per annum (simple interest)
   - Inputs: deposit amount, years

Interaction Guidelines:
- Always respond politely and in a conversational tone.
- Do not show calculations, formulas, or code unless explicitly requested.
- Never use LaTeX or technical formatting.
- Give final results directly and encourage follow-ups (e.g., \"Would you like to proceed?\").
- If any required input is missing, ask for it clearly and respectfully.
- Do not assume intent. Always confirm the user's goal before processing.
- If EMI-based rules are violated (e.g. over salary threshold), reject politely with reason.

The goal is to simulate a real banking agent’s tone and behavior."""
    chat_msgs = [
        {"role": "system", "content": system_prompt},
        *messages,
        {"role": "user", "content": user_input}
    ]
    while True:
        payload = {
            "model": MODEL,
            "tools": tools,
            "messages": chat_msgs
        }
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "HTTP-Referer": "http://localhost",
            "X-Title": "Banking Chatbot"
        }
        response = requests.post(ENDPOINT, json=payload, headers=headers)
        data = response.json()
        msg = data["choices"][0]["message"]
        chat_msgs.append(msg)
        if "tool_calls" in msg and msg["tool_calls"]:
            for tool_call in msg["tool_calls"]:
                tool_name = tool_call["function"]["name"]
                tool_args = json.loads(tool_call["function"]["arguments"])
                if tool_name == "get_user_profile":
                    tool_result = TOOL_MAPPING[tool_name](user_profile)
                else:
                    tool_result = TOOL_MAPPING[tool_name](**tool_args)
                chat_msgs.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "name": tool_name,
                    "content": json.dumps(tool_result),
                })
        else:
            break
    return chat_msgs[-1]["content"] 