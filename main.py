import sys
import os

if getattr(sys, 'frozen', False):
    os.chdir(sys._MEIPASS)

import streamlit.web.cli as stcli

def main():
    sys.argv = [
        "streamlit",
        "run",
        "app.py",
        "--server.port", "8501",
        "--server.headless", "true"
    ]
    stcli.main()

if __name__ == "__main__":
    main()