import pandas as pd
import os

class BankManager:
    def __init__(self, user_data_path="bank_users.csv", loan_record_path="approved_loans.csv", fd_record_path="fixed_deposits.csv"):
        self.user_data_path = user_data_path
        self.loan_record_path = loan_record_path
        self.fd_record_path = fd_record_path

    def load_user_data(self, account_number):
        try:
            df = pd.read_csv(self.user_data_path, dtype={"account_number": str})
            user = df[df["account_number"] == str(account_number)]
            return user.iloc[0].to_dict() if not user.empty else None
        except Exception:
            return None

    def calculate_personal_loan_emi(self, principal, years):
        rate = 0.125 / 12  # 12.5% annual interest, monthly
        months = years * 12
        emi = (principal * rate * (1 + rate) ** months) / ((1 + rate) ** months - 1)
        return emi

    def approve_loan(self, account_number, loan_type, principal, years, monthly_salary):
        if loan_type.lower() == "student":
            return {
                "status": "info",
                "message": "📞 For student loans, please contact our education loan department at 1800-123-456."
            }

        emi = self.calculate_personal_loan_emi(principal, years)  # Assuming same EMI formula applies

        # Check eligibility based on loan type
        if loan_type.lower() == "personal" and emi > 0.6 * monthly_salary:
            return {
                "status": "rejected",
                "message": f"❌ Loan Rejected: EMI ₹{emi:.2f} exceeds 60% of your monthly salary ₹{monthly_salary:.2f}."
            }
        elif loan_type.lower() == "home" and emi > 0.5 * monthly_salary:
            return {
                "status": "rejected",
                "message": f"❌ Loan Rejected: EMI ₹{emi:.2f} exceeds 50% of your monthly salary ₹{monthly_salary:.2f}."
            }

        user = self.load_user_data(account_number)
        if not user:
            return {
                "status": "error",
                "message": f"❌ Error: Account {account_number} not found."
            }

        loan_entry = {
            "account_number": user["account_number"],
            "name": user["name"],
            "loan_type": loan_type.capitalize(),
            "loan_amount": principal,
            "duration_years": years,
            "monthly_salary": monthly_salary,
            "approved_emi": round(emi, 2)
        }

        print(f"DEBUG: Writing loan entry for account {user['account_number']}: {loan_entry}")
        print("DEBUG: Writing to", os.path.abspath(self.loan_record_path))
        try:
            if os.path.exists(self.loan_record_path):
                loan_df = pd.read_csv(self.loan_record_path)
                loan_df = pd.concat([loan_df, pd.DataFrame([loan_entry])], ignore_index=True)
            else:
                loan_df = pd.DataFrame([loan_entry])
            loan_df.to_csv(self.loan_record_path, index=False)
            print("DEBUG: Write successful")
        except Exception as e:
            print("ERROR writing to CSV:", e)

        return {
            "status": "approved",
            "message": f"✅ {loan_type.capitalize()} Loan Approved! EMI: ₹{emi:.2f}/month for {years} years. Loan details saved."
        }

    def create_fixed_deposit(self, account_number, amount, years):
        try:
            amount = float(amount)
            years = float(years)
        except Exception as e:
            print("ERROR: Invalid FD input:", amount, years)
            return {"status": "error", "message": "Invalid amount or years for fixed deposit."}
        rate = 0.068  # 6.8% simple interest
        maturity = amount + (amount * rate * years)
        fd_entry = {
            "account_number": account_number,
            "amount": amount,
            "years": years,
            "maturity_amount": round(maturity, 2)
        }
        print(f"DEBUG: Writing fixed deposit entry for account {account_number}: {fd_entry}")
        print("DEBUG: Writing to", os.path.abspath(self.fd_record_path))
        try:
            if os.path.exists(self.fd_record_path):
                fd_df = pd.read_csv(self.fd_record_path)
                fd_df = pd.concat([fd_df, pd.DataFrame([fd_entry])], ignore_index=True)
            else:
                fd_df = pd.DataFrame([fd_entry])
            fd_df.to_csv(self.fd_record_path, index=False)
            print("DEBUG: Write successful")
        except Exception as e:
            print("ERROR writing to CSV:", e)
        return fd_entry

    def get_fixed_deposits(self, account_number):
        if not os.path.exists(self.fd_record_path):
            return []
        df = pd.read_csv(self.fd_record_path, dtype={"account_number": str})
        return df[df["account_number"] == str(account_number)].copy().to_dict('records')  # type: ignore

    def update_user_info_if_missing(self, account_number, **kwargs):
        """DEPRECATED: This logic has been moved to UserDataManager in data.py"""
        pass

    def get_loan_history(self, account_number):
        if not os.path.exists(self.loan_record_path):
            return []
        df = pd.read_csv(self.loan_record_path, dtype={"account_number": str})
        acc_no = str(account_number).strip()
        return df[df["account_number"].str.strip() == acc_no].copy().to_dict('records')  # type: ignore 

    def get_balance(self, account_number):
        user = self.load_user_data(account_number)
        if user and "balance" in user:
            balance = user["balance"]
            if balance and str(balance).strip() and str(balance).strip().lower() != "data not available":
                return balance
            else:
                return "Balance not available. Please update your account information."
        return "Account not found." 