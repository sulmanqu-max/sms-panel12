import time
import json
import re
import requests
from bs4 import BeautifulSoup

LOGIN_URL = "http://51.75.55.16/ints/login"
DASHBOARD_URL = "http://51.75.55.16/ints/agent/SMSDashboard"
USERNAME = "Sulman555"
PASSWORD = "sulman123##"

def run_bot():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    })
    
    try:
        print("Fetching login page...")
        resp = session.get(LOGIN_URL)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Parse Math Captcha
        page_text = soup.get_text()
        captcha_match = re.search(r'What is\s*(\d+)\s*([\+\-\*])\s*(\d+)', page_text)
        
        captcha_answer = "0"
        if captcha_match:
            n1 = int(captcha_match.group(1))
            op = captcha_match.group(2)
            n2 = int(captcha_match.group(3))
            
            if op == '+': captcha_answer = str(n1 + n2)
            elif op == '-': captcha_answer = str(n1 - n2)
            elif op == '*': captcha_answer = str(n1 * n2)
            print(f"Solved Captcha: {n1} {op} {n2} = {captcha_answer}")
        else:
            print("Captcha pattern not found!")

        # Gather all form inputs
        login_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "captcha": captcha_answer
        }
        
        form = soup.find('form')
        if form:
            for inp in form.find_all('input'):
                name = inp.get('name')
                val = inp.get('value', '')
                if name and name not in login_data:
                    login_data[name] = val

        print("Submitting login form...")
        login_resp = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        print(f"Login Response Final URL: {login_resp.url}")

        # Check if login failed (if URL still contains login or error text exists)
        if "login" in login_resp.url or "Error" in login_resp.text:
            print("Login failed! Check credentials or captcha parsing.")
            # Let's save debug state
            error_data = [{"phone": "Login Failed", "client": USERNAME, "service": "Auth Error", "otp": "Check Captcha/Pass", "time": time.strftime("%I:%M %p")}]
            with open('data.json', 'w', encoding='utf-8') as f:
                json.dump(error_data, f, ensure_ascii=False, indent=4)
            return

        # Fetch SMS / Number Dashboard
        print("Fetching Dashboard data...")
        dash_resp = session.get(DASHBOARD_URL)
        dash_soup = BeautifulSoup(dash_resp.text, 'html.parser')
        
        extracted_data = []
        
        # Find rows in any table
        for table in dash_soup.find_all('table'):
            for row in table.find_all('tr'):
                cols = row.find_all(['td', 'th'])
                cols_text = [ele.text.strip() for ele in cols]
                if len(cols_text) >= 2 and "Phone" not in cols_text[0] and "Date" not in cols_text[0]:
                    extracted_data.append({
                        "phone": cols_text[0],
                        "client": cols_text[1] if len(cols_text) > 1 else USERNAME,
                        "service": cols_text[2] if len(cols_text) > 2 else "WhatsApp Live",
                        "otp": cols_text[3] if len(cols_text) > 3 else "Waiting...",
                        "time": time.strftime("%I:%M %p")
                    })
        
        if not extracted_data:
            print("No table data found, extracting text blocks...")
            # Try to grab whatever numbers are visible on dashboard
            extracted_data = [
                {"phone": "Panel Connected", "client": USERNAME, "service": "Live SMS", "otp": "No Active SMS Found", "time": time.strftime("%I:%M %p")}
            ]

        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
        print("data.json updated successfully!")

    except Exception as e:
        print(f"Error occurred: {e}")
        error_data = [{"phone": "Error", "client": "System", "service": "Exception", "otp": str(e), "time": time.strftime("%I:%M %p")}]
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_bot()
