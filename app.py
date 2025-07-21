import streamlit as st
import requests
import os
import pandas as pd
from dotenv import load_dotenv
from bank import BankManager
from data import UserDataManager
from chatbot import get_chatbot_response_with_tools

class AmericanExpressChatBot:
    def __init__(self):
        self.api_key = None
        self.user_data_path = "bank_users.csv"
        self.bank_manager = BankManager()
        self.user_manager = UserDataManager()
        self.load_environment()
        self.setup_ui()
        self.setup_session()

    def load_environment(self):
        load_dotenv(dotenv_path=".env.local")
        self.api_key = os.getenv("API_KEY")

    def setup_ui(self):
        st.set_page_config(page_title="American Express Chatbot", layout="wide")
        st.markdown("""
            <style>
                body {
                    background-color: #0d1117;
                    color: #c9d1d9;
                }
                .fixed-header {
                    position: fixed;
                    top: 10px;
                    left: 20px;
                    font-weight: bold;
                    color: #58a6ff;
                    font-size: 20px;
                    z-index: 999;
                }
                .chat-container {
                    background-color: #161b22;
                    border-radius: 10px;
                    padding: 20px;
                    margin-top: 60px;
                    max-height: 70vh;
                    overflow-y: auto;
                }
                .chat-message {
                    margin-bottom: 15px;
                }
                .user {
                    color: #58a6ff;
                    font-weight: bold;
                }
                .bot {
                    color: #8b949e;
                }
                .stTextInput>div>div>input {
                    background-color: #21262d;
                    color: white;
                }
                .stButton>button {
                    background-color: #238636;
                    color: white;
                    border-radius: 5px;
                    border: none;
                    padding: 10px;
                }
            </style>
        """, unsafe_allow_html=True)
        st.markdown('<div class="fixed-header">AmericanExpressAI</div>', unsafe_allow_html=True)
        st.title("🤖 American Express Bank - Banking Chatbot")

    def setup_session(self):
        if "messages" not in st.session_state:
            st.session_state.messages = []
        if "user_profile_set" not in st.session_state:
            st.session_state.user_profile_set = False
        if "user_profile" not in st.session_state:
            st.session_state.user_profile = {}
        if "nav_page" not in st.session_state:
            st.session_state.nav_page = "Chat"

    def sidebar(self):
        with st.sidebar:
            st.header("User Menu")
            if st.session_state.user_profile_set:
                user = st.session_state.user_profile
                st.markdown(f"**Name:** {user.get('name', '-')}")
                st.markdown(f"**Account #:** {user.get('account_number', '-')}")
                st.markdown(f"**Credit Score:** {user.get('credit_score', '-')}")
                st.markdown(f"**Monthly Salary:** ₹{user.get('monthly_salary', '-')}")
                st.markdown("---")
                nav = st.radio("Go to:", ["Chat", "Profile", "Loans", "Deposits"], index=["Chat", "Profile", "Loans", "Deposits"].index(st.session_state.nav_page))
                st.session_state.nav_page = nav
                if st.button("Logout"):
                    st.session_state.user_profile_set = False
                    st.session_state.user_profile = {}
                    st.session_state.messages = []
                    st.session_state.nav_page = "Chat"
                    st.rerun()
            else:
                st.info("Please login or register to access features.")

    def prompt_user_identity(self):
        st.subheader("Welcome to American Express Bank 👋")
        choice = st.radio("Are you a new or existing customer?", ("New", "Existing"))

        if choice == "New":
            self.register_new_user()
        else:
            self.login_existing_user()

    def register_new_user(self):
        st.subheader("📝 New Customer Registration")
        name = st.text_input("Full Name", help="Enter your full legal name.")
        acc_no = st.text_input("Account Number", help="10-digit unique account number.")
        credit_score = st.number_input("Credit Score", min_value=300, max_value=900, value=700, help="Between 300 and 900.")
        balance = st.text_input("Initial Balance", help="Enter initial account balance.")
        account_type = st.text_input("Account Type", help="e.g., Savings, Current, Salary")
        branch = st.text_input("Branch", help="Branch name or code.")
        ifsc = st.text_input("IFSC Code", help="Bank IFSC code.")
        phone = st.text_input("Phone Number", help="Contact phone number.")
        email = st.text_input("Email", help="Contact email address.")
        salary = st.text_input("Monthly Salary (₹)", help="Your monthly income in INR.")

        if st.button("Register"):
            # Validate account number
            if not name or not acc_no or len(acc_no) != 10 or not acc_no.isdigit():
                st.error("Please provide a valid name and a 10-digit account number.")
                return
            # Fill missing fields with 'Data not available'
            def safe_val(val):
                return val if val and str(val).strip() else "Data not available"
            new_data = pd.DataFrame([{
                "account_number": acc_no,
                "name": safe_val(name),
                "credit_score": credit_score if credit_score else "Data not available",
                "balance": safe_val(balance),
                "account_type": safe_val(account_type),
                "branch": safe_val(branch),
                "ifsc": safe_val(ifsc),
                "phone": safe_val(phone),
                "email": safe_val(email),
                "monthly_salary": safe_val(salary)
            }])
            # Check for duplicate account number
            if os.path.exists(self.user_data_path):
                df = pd.read_csv(self.user_data_path, dtype={"account_number": str})
                if acc_no in df["account_number"].astype(str).values:
                    st.error("Account number already exists. Please log in or use a different number.")
                    return
                df = pd.concat([df, new_data], ignore_index=True)
            else:
                df = new_data
            df.to_csv(self.user_data_path, index=False)
            st.session_state.user_profile = new_data.iloc[0].to_dict()
            st.session_state.user_profile_set = True
            st.success("✅ Registration complete! You may now chat.")

    def login_existing_user(self):
        st.subheader("🔐 Existing Customer Login")
        acc_no = st.text_input("Enter Account Number", help="Your 10-digit account number.")

        if st.button("Login"):
            if not acc_no or len(acc_no) != 10 or not acc_no.isdigit():
                st.error("Please enter a valid 10-digit account number.")
                return
            success, result = self.user_manager.login_user(acc_no)
            if success:
                st.session_state.user_profile = result
                st.session_state.user_profile_set = True
                if isinstance(result, dict):
                    st.success(f"✅ Welcome back, {result.get('name', '-') }!")
                else:
                    st.error(result)
            else:
                st.error(result)

    def display_chat(self):
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            role = msg["role"]
            style = "user" if role == "user" else "bot"
            label = "You:" if role == "user" else "AmExBot:"
            st.markdown(f"<div class='chat-message'><span class='{style}'>{label}</span> {msg['content']}</div>",
                        unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    def display_profile(self):
        user = st.session_state.user_profile
        st.subheader("👤 Profile Information")
        st.write(f"**Name:** {user.get('name', '-')}")
        st.write(f"**Account #:** {user.get('account_number', '-')}")
        st.write(f"**Credit Score:** {user.get('credit_score', '-')}")
        st.write(f"**Monthly Salary:** ₹{user.get('monthly_salary', '-')}")

    def display_loans(self):
        user = st.session_state.user_profile
        st.subheader("💳 Loan History")
        loans = self.bank_manager.get_loan_history(user.get('account_number', ''))
        if loans:
            st.dataframe(pd.DataFrame(loans))
        else:
            st.info("No loan records found.")

    def display_deposits(self):
        user = st.session_state.user_profile
        st.subheader("🏦 Fixed Deposits")
        fds = self.bank_manager.get_fixed_deposits(user.get('account_number', ''))
        if fds:
            st.dataframe(pd.DataFrame(fds))
        else:
            st.info("No fixed deposit records found.")

    def run(self):
        self.sidebar()
        if not st.session_state.user_profile_set:
            self.prompt_user_identity()
        else:
            nav = st.session_state.nav_page
            if nav == "Chat":
                self.display_chat()
                with st.form("chat_form", clear_on_submit=True):
                    user_input = st.text_input("Type your message...",
                                               placeholder="Ask about loans, EMI, deposits...")
                    submitted = st.form_submit_button("Send")
                    if submitted and user_input.strip():
                        st.session_state.messages.append({"role": "user", "content": user_input})
                        with st.spinner("AmExBot is typing..."):
                            response = get_chatbot_response_with_tools(user_input, st.session_state.messages[:-1], st.session_state.user_profile)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                        st.rerun()
            elif nav == "Profile":
                self.display_profile()
            elif nav == "Loans":
                self.display_loans()
            elif nav == "Deposits":
                self.display_deposits()

# Run the app
if __name__ == "__main__":
    AmericanExpressChatBot().run()
