import pandas as pd
import os

class UserDataManager:
    def __init__(self, user_data_path="bank_users.csv"):
        self.user_data_path = user_data_path

    def register_user(self, name, acc_no, credit_score, salary):
        # This implementation is in app.py, keep this file for other data functions if needed
        pass

    def login_user(self, acc_no):
        if os.path.exists(self.user_data_path):
            df = pd.read_csv(self.user_data_path, dtype=str)
            acc_no = acc_no.strip()
            user = df[df["account_number"] == acc_no]
            if not user.empty:
                return True, user.iloc[0].to_dict()
            else:
                return False, "Account not found. Please check the number and try again."
        else:
            return False, "No user data file found."

    def update_user_info_if_missing(self, account_number, **kwargs):
        """Update user info in bank_users.csv if any field is provided."""
        if not os.path.exists(self.user_data_path):
            return
        df = pd.read_csv(self.user_data_path, dtype=str)
        idx = df.index[df["account_number"] == str(account_number)].tolist()
        if not idx:
            return
        idx = idx[0]
        updated = False
        for key, value in kwargs.items():
            if key in df.columns:
                df.at[idx, key] = value
                updated = True
        if updated:
            df.to_csv(self.user_data_path, index=False) 