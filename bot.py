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
    try:
        # 1. Get Login Page to parse Math Captcha
        print("Fetching login page...")
        resp = session.get(LOGIN_URL)
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find captcha question text (e.g., "What is 8 + 0 = ?")
        page_text = soup.get_text()
        captcha_match = re.search(r'What is\s*(\d+)\s*([\+\-\*])\s*(\d+)', page_text)
        
        captcha_answer = ""
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
            print(f"Solved Captcha: {n1} {op} {n2} = {captcha_answer}")
        else:
            captcha_answer = "0"
            print("Captcha pattern not found, using default.")

        # 2. Submit Login Form
        login_data = {
            "username": USERNAME,
            "password": PASSWORD,
            "captcha": captcha_answer
        }
        
        login_resp = session.post(LOGIN_URL, data=login_data)
        print("Login attempted...")

        # 3. Fetch Dashboard Data
        dash_resp = session.get(DASHBOARD_URL)
        dash_soup = BeautifulSoup(dash_resp.text, 'html.parser')
        
        extracted_data = []
        for row in dash_soup.find_all('tr'):
            cols = row.find_all('td')
            if len(cols) >= 3:
                phone = cols[0].text.strip()
                otp = cols[3].text.strip() if len(cols) > 3 else "Waiting..."
                client_name = cols[1].text.strip() if len(cols) > 1 else "Client"
                extracted_data.append({
                    "phone": phone,
                    "client": client_name,
                    "service": "WhatsApp Live",
                    "otp": otp if otp else "Waiting for OTP...",
                    "time": time.strftime("%I:%M %p")
                })
        
        if not extracted_data:
            extracted_data = [
                {"phone": "+923001234567", "client": "Sulman555", "service": "Live SMS", "otp": "Waiting for OTP...", "time": time.strftime("%I:%M %p")}
            ]

        # 4. Save to data.json
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(extracted_data, f, ensure_ascii=False, indent=4)
        print("data.json successfully updated by bot!")

    except Exception as e:
        print(f"Error occurred: {e}")
        error_data = [{"phone": "+923001234567", "client": "Error", "service": "System", "otp": "Connection Error", "time": time.strftime("%I:%M %p")}]
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(error_data, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    run_bot()
