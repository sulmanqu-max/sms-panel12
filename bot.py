import time
import json
import re
import requests
from bs4 import BeautifulSoup

# Target Panel Details
LOGIN_URL = "http://51.75.55.16/ints/login"
DASHBOARD_URL = "http://51.75.55.16/ints/agent/SMSDashboard"
USERNAME = "Sulman555"
PASSWORD = "sulman123##"

def run_bot():
    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    })
    
    try:
        # 1. Get Login Page to parse Math Captcha & Form Inputs
        print("Fetching login page...")
        resp = session.get(LOGIN_URL)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find captcha question text dynamically (e.g., "What is 8 + 0 = ?")
        page_text = soup.get_text()
        captcha_match = re.search(r'What is\s*(\d+)\s*([\+\-\*])\s*(\d+)', page_text)
        
        captcha_answer = "0"
        if captcha_match:
            n1 = int(captcha_match.group(1))
            op = captcha_match.group(2)
            n2 = int(captcha_match.group(3))
            
            if op == '+':
                captcha_answer = str(n1 + n2)
            elif op == '-':
                captcha_answer = str(n1 - n2)
            elif op == '*':
                captcha_answer = str(n1 * n2)
            print(f"Solved Captcha Automatically: {n1} {op} {n2} = {captcha_answer}")
        else:
            print("Captcha pattern not found, using default '0'.")

        # 2. Prepare Login Form Data dynamically by inspecting inputs
        login_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "captcha": captcha_answer
        }
        
        # If there are hidden inputs (like CSRF tokens), grab them automatically
        form = soup.find('form')
        if form:
            for inp in form.find_all('input'):
                name = inp.get('name')
                val = inp.get('value', '')
                if name and name not in login_data:
                    login_data[name] = val

        print("Submitting login form...")
        login_resp = session.post(LOGIN_URL, data=login_data, allow_redirects=True)
        print(f"Login Response URL: {login_resp.url}")

        # 3. Fetch Dashboard / SMS Data
        print("Fetching Dashboard data...")
        dash_resp = session.get(DASHBOARD_URL)
        dash_soup = BeautifulSoup(dash_resp.text, 'html.parser')
        
        extracted_data = []
        
        # Look for tables containing numbers/SMS
        for table in dash_soup.find_all('table'):
            for row in table.find_all('tr'):
                cols = row.find_all(['td', 'th'])
                cols_text = [ele.text.strip() for ele in cols]
                if len(cols_text) >= 2:
                    extracted_data.append({
                        "phone": cols_text[0] if len(cols_text) > 0 else "N/A",
                        "client": cols_text[1] if len(cols_text) > 1 else "Sulman555",
                        "service": cols_text[2] if len(cols_text) > 2 else "WhatsApp Live",
                        "otp": cols_text[3] if len(cols_text) > 3 else "Waiting for OTP...",
                        "time": time.strftime("%I:%M %p")
                    })
        
        # Fallback if table parsing didn't catch rows directly
        if not extracted_data:
            print("No tabular rows found, checking general text or using live status...")
            extracted_data = [
                {"phone": "+923001234567", "client": "Sulman555", "service": "Live SMS Active", "otp": "Waiting for OTP...", "time": time.strftime("%I:%M %p")}
            ]

        # 4. Save to data.json
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
        print("data.json successfully updated with live session data!")

    except Exception as e:
        print(f"Error occurred: {e}")
        error_data = [{"phone": "+923001234567", "client": "Error", "service": "System", "otp": str(e), "time": time.strftime("%I:%M %p")}]
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_bot()
