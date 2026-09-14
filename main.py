# RetailPulse (Enterprise Sales Data Analyzer) - main.py

"""
Team Members:
1. Aniketh Chavare - 25BTRPW014
2. Aayush Kumar Verma - 25BTRPW003
3. Ardra Rajesh - 25BTRPW016
4. Harshith R Thattihalli - 25BTRPW047
5. Guthi Leela Harsha - 25BTRPW042
6. Akula Nikhil - 25BTRPW012
7. Ekansh Kumar - 25BTRPW037
8. Akshath Maurya - 25BTRPW010
"""

# Imports
import os
import sys
import tkinter as tk
from tkinter import messagebox

from gui_app import RetailPulseGUI
from auth_manager import AuthManager
from analytics_engine import AnalyticsEngine
from email_dispatcher import EmailDispatcher

# Function 1: check_environment
def check_environment(dataset_path: str) -> bool:
    """ Verifies that the required dataset file is accessible before booting. """
    
    if not os.path.exists(dataset_path):
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror(
            "Dataset Missing",
            f"Unable to locate '{dataset_path}'.\n\n"
            "Please ensure 'amazon.csv' is placed in the same directory as 'main.py'."
        )
        root.destroy()
        
        return False

    return True

# Function 2: main
def main() -> None:
    """ Initializes engines and launches the RetailPulse desktop interface. """
    
    dataset_file = "amazon.csv"

    # Pre-Flight System Check
    if not check_environment(dataset_file):
        sys.exit(1)

    # Instantiate Core Engines
    auth_manager = AuthManager()
    email_dispatcher = EmailDispatcher()
    analytics_engine = AnalyticsEngine(csv_filepath=dataset_file)

    # Initialize Tkinter Root and Mount the GUI
    root = tk.Tk()
    
    app = RetailPulseGUI(
        root=root,
        engine=analytics_engine,
        auth=auth_manager,
        email_dispatcher=email_dispatcher
    )

    # Enter GUI Event Loop
    root.mainloop()

# Running the Application
if __name__ == "__main__":
    main()