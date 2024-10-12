from utils import TradovateAPI
from config import*
from datetime import datetime, timezone
import time


if __name__ == "__main__":
    api          = TradovateAPI(USERNAME, PASSWORD, APPLICATION, APP_VERSION, DEVICE_ID, CID, SECRET)
    api_follower = TradovateAPI(FOLLOWER_USERNAME, FOLLOWER_PASSWORD, FOLLOWER_APPLICATION, FOLLOWER_APP_VERSION, FOLLOWER_DEVICE_ID, FOLLOWER_CID, FOLLOWER_SECRET)
    
    while True:
        print(f'last checked in  {datetime.now()}')
        try:
            filled_orders = api.filter_recent_orders()
            for elt in filled_orders:
                action          = elt["action"]
                contract_symbol = api.get_contract_details(elt["contractId"])["name"]
                qty             = elt["qty"]
                print(api.get_contract_details(elt["contractId"]))
                print(f"New contract detected: {action} {contract_symbol} for quantity {qty}")
                print(api_follower.place_order( action, contract_symbol, qty, order_type="Market", is_automated=True))
                input()
        except Exception as e:
            print(f"Error: {str(e)}")

        time.sleep(REFRESH_INTERVAL)