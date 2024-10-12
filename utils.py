import requests
from config import *
from pprint import pprint
import time
from datetime import datetime, timezone

class TradovateAPI:
    def __init__(self, username, password, application, app_version, device_id, cid, secret):
        self.username = username
        self.password = password
        self.application = application
        self.app_version = app_version
        self.device_id = device_id
        self.cid = cid
        self.secret = secret        
        self.token = None
        self.token_expiration_time = 0  # To store token expiration time

    def _get_new_token(self):
        """Fetch a new access token and update token information."""
        if  USE_LIVE:
            url = LIVE_URL_TOKEN
        else:
            url = DEMO_URL_TOKEN

        headers = {
            "accept": "application/json",
            "Content-Type": "application/json"
        }
        data = {
            "name": self.username,
            "password": self.password,
            "appId": self.application,
            "appVersion": self.app_version,
            "deviceId": self.device_id,
            "cid": self.cid,
            "sec": self.secret
        }
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            token_data = response.json()
            self.token = token_data['accessToken']
            self.token_expiration_time = token_data['expirationTime'] # Convert ms to seconds
            print(f"New token obtained: {self.token}, expires at {self.token_expiration_time}")
        else:
            raise Exception(f"Error obtaining token: {response.status_code} - {response.text}")

    def get_token(self):
        """Return the access token, fetch a new one if expired."""
        # Get current UTC time as a datetime object
        current_time = datetime.now(timezone.utc).timestamp()

        # Convert ISO 8601 string to Unix timestamp if it's a string
        if isinstance(self.token_expiration_time, str):
            try:
                # Parse the ISO 8601 date string and convert it to a datetime object
                expiration_dt = datetime.strptime(self.token_expiration_time, '%Y-%m-%dT%H:%M:%S.%fZ')
                # Ensure the datetime is in UTC and convert it to a Unix timestamp
                expiration_dt = expiration_dt.replace(tzinfo=timezone.utc)
                self.token_expiration_time = expiration_dt.timestamp()
            except ValueError:
                print("Error: Invalid expiration time format. Fetching a new token...")
                self._get_new_token()
                return self.token

        # If the token is not present or expired, get a new one
        if self.token is None or current_time >= self.token_expiration_time:
            print("Token expired or not available, fetching a new one...")
            self._get_new_token()
        
        return self.token

    def get_filled_orders(self):
        """Retrieve filled orders using the access token."""
        token = self.get_token()
        if  USE_LIVE:
            orders_url = LIVE_URL_FillS
        else:
            orders_url = DEMO_URL_FillS
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.get(orders_url, headers=headers)
        
        if response.status_code == 200:
            filled_orders = response.json()
            return filled_orders
        else:
            raise Exception(f"Error fetching filled orders: {response.status_code} - {response.text}")

    def filter_recent_orders(self,seconds=REFRESH_INTERVAL*0.95):
        """Filter orders placed within the last `seconds` from the current UTC time."""
        orders = self.get_filled_orders()
        current_time = datetime.now(timezone.utc)
        recent_orders = []
        for order in orders:
            order_time = datetime.strptime(order['timestamp'], '%Y-%m-%dT%H:%M:%S.%fZ')
            order_time = order_time.replace(tzinfo=timezone.utc)
            time_difference = (current_time - order_time).total_seconds()
            if time_difference <= seconds:
                recent_orders.append(order)

        return recent_orders

    def place_order(self, action, symbol, order_qty, order_type="Market", is_automated=True):
        """Place an order using the Tradovate API."""
        token = self.get_token()
        if USE_LIVE:
            url = LIVE_URL_ORDER_PLACE
        else:
            url = DEMO_URL_ORDER_PLACE

        # Request body
        body = {
            "accountSpec": self.username,
            "accountId": 1283991,
            "action": action,
            "symbol": symbol,
            "orderQty": int(order_qty),
            "orderType": order_type,
            "isAutomated": is_automated
        }
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, headers=headers, json=body)

        if response.status_code == 200:
            order_response = response.json()
            return order_response
        else:

            print(f"Error placing order: {response.status_code} - {response.text}")
    
    def get_contract_details(self, contract_id):
        """Retrieve details about a contract using its ID."""
        token = self.get_token()
        contract_url = f"https://demo.tradovateapi.com/v1/contract/item?id={contract_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.get(contract_url, headers=headers)
        
        if response.status_code == 200:
            contract_details = response.json()
            return contract_details
        else:
            raise Exception(f"Error fetching contract details: {response.status_code} - {response.text}")
    
    

