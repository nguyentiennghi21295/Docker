import requests
import json
import string
import random
import os
from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


CLIENT_ID = '78v7vw8a6gbdr4'
CLIENT_SECRET = 'MxIQdlEGkRGGxlAe'
REDIRECT_URL = 'http://localhost:8000/'


letters = string.ascii_lowercase
random.choice(letters)
CSRF_TOKEN = ''.join(random.choice(letters) for i in range(24))


# Your LinkedIn credentials
USERNAME = 'nguyentiennghi212@gmail.com'
PASSWORD = 'edogawaconan'

auth_params1 = {
    'response_type': 'code',
    'client_id': CLIENT_ID,
    'redirect_uri': REDIRECT_URL,
    'state': CSRF_TOKEN,
    'scope': 'r_liteprofile,r_emailaddress,w_member_social'
}


response = requests.get('https://www.linkedin.com/oauth/v2/authorization', params=auth_params1)
login_url = response.url

def get_authorization_code():
    options = webdriver.ChromeOptions()
    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280x1696")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")
    driver_path = "/opt/chromedriver"
    service = ChromeService(executable_path="/opt/chromedriver")
    driver = webdriver.Chrome(service = service,
                              options=options)
    driver.get(login_url)
    email1 = driver.find_element(By.ID, "username")
    password1 = driver.find_element(By.ID, "password")
    email1.send_keys(USERNAME)
    password1.send_keys(PASSWORD)
    driver.find_element(By.CSS_SELECTOR, '.btn__primary--large').click()

        # Step 3: Wait for the redirect and extract the authorization code from the URL
    WebDriverWait(driver, 10).until(
        EC.url_contains(REDIRECT_URL) and EC.url_contains('code=')
    )
    AUTH_CODE = driver.current_url.split('code=')[1].split('&')[0]
    driver.quit()    
    return AUTH_CODE

def lambda_handler(event=None, context=None):
    AUTH_CODE = get_authorization_code()
    ACCESS_TOKEN_URL = 'https://www.linkedin.com/oauth/v2/accessToken'
    access_data = {
         'grant_type': 'authorization_code',
         'code': AUTH_CODE,
        'redirect_uri': REDIRECT_URL,
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET
    }
    response = requests.post(ACCESS_TOKEN_URL, data=access_data, timeout=60)
    response = response.json()
    access_token = response['access_token']
    params = {'oauth2_access_token': access_token}
    response = requests.get('https://api.linkedin.com/v2/me', params=params)
    
    return {
        'statusCode': 200,
        'body': json.dumps(response.json(), indent=1)
    }

lambda_handler()
