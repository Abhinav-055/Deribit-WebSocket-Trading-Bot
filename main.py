import asyncio
import websockets
import json
import os
import time
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
DERIBIT_WS_URL = "wss://test.deribit.com/ws/api/v2" 
RECONNECT_ATTEMPTS = 5
BASE_DELAY = 2

async def send_request(ws, request):
    await ws.send(json.dumps(request))
    response = await ws.recv()
    return json.loads(response)

async def authenticate(ws):
    auth_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "public/auth",
        "params": {
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
            "grant_type": "client_credentials"
        }
    }
    response = await send_request(ws, auth_request)
    print(" Authentication Successful" if response.get("result") else " Authentication Failed", response)

async def get_contract_size(ws, instrument_name):
    response = await send_request(ws, {"jsonrpc": "2.0", "id": 2, "method": "public/get_instrument", "params": {"instrument_name": instrument_name}})
    return response.get("result", {}).get("contract_size", None)

async def place_order(ws):
    instrument_name = input("Instrument (e.g., ETH-PERPETUAL): ")
    contract_size = await get_contract_size(ws, instrument_name)
    if not contract_size:
        print(" Invalid instrument.")
        return
    try:
        amount = float(input(f"Order amount (multiple of {contract_size}): "))
        if amount % contract_size != 0:
            raise ValueError("Invalid amount!")
        order_type = input("Order type (buy/sell): ").strip().lower()
        order_kind = input("Order kind (market/limit): ").strip().lower()
        if order_kind == "limit":
            price = float(input("Limit price: "))
        
        order_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": f"private/{order_type}",
            "params": {
                "instrument_name": instrument_name,
                "amount": amount,
                "type": order_kind,
                "label": input("Order label (optional): ") or "custom_order"
            }
        }
        if order_kind == "limit":
            order_request["params"].update({"price": price, "post_only": True})
        start_time = time.perf_counter()
        response = await send_request(ws, order_request)
        print(" Order Response:", response)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Time taken: {elapsed_time:.6f} seconds")
    except ValueError as e:
        print(f" Error: {e}")

async def modify_order(ws):
    try:
        order_id = input("Order ID to modify: ")
        new_amount = float(input("New amount: "))
        new_price = float(input("New price: "))
        start_time = time.perf_counter()
        response = await send_request(ws, {"jsonrpc": "2.0", "id": 4, "method": "private/edit", "params": {"order_id": order_id, "amount": new_amount, "price": new_price}})
        print(" Modify Order Response:", response)
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"Time taken: {elapsed_time:.6f} seconds")
    except ValueError:
        print(" Invalid input.")

async def cancel_order(ws):
    order_id = input("Order ID to cancel: ")
    start_time = time.perf_counter()
    response = await send_request(ws, {"jsonrpc": "2.0", "id": 5, "method": "private/cancel", "params": {"order_id": order_id}})
    print(" Cancel Order Response:", response)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.6f} seconds")

async def get_positions(ws):
    currency = input("Currency (e.g., ETH, BTC): ")
    start_time = time.perf_counter()
    response = await send_request(ws, {"jsonrpc": "2.0", "id": 6, "method": "private/get_positions", "params": {"currency": currency}})
    print(" Open Positions:", response)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.6f} seconds")

async def stream_market_data(ws):
    instrument_name = input("Instrument to stream (e.g., ETH-PERPETUAL): ")
    await ws.send(json.dumps({"jsonrpc": "2.0", "id": 7, "method": "public/subscribe", "params": {"channels": [f"book.{instrument_name}.100ms"]}}))
    print(f" Streaming order book for {instrument_name}... Press Ctrl+C to stop.")
    async for response in ws:
        data = json.loads(response)
        print(" Market Data Update:", data.get("params", {}).get("data", {}))

async def get_order_book(ws):
    instrument_name = input("Instrument for order book (e.g., BTC-PERPETUAL): ")
    start_time = time.perf_counter()
    response = await send_request(ws, {"jsonrpc": "2.0", "id": 8, "method": "public/get_order_book", "params": {"instrument_name": instrument_name, "depth": 5}})
    print(" Order Book:", response)
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time
    print(f"Time taken: {elapsed_time:.6f} seconds")

async def main():
    reconnect_attempts = 0
    while reconnect_attempts < RECONNECT_ATTEMPTS:
        try:
            async with websockets.connect(DERIBIT_WS_URL) as ws:
                await authenticate(ws)
                while True:
                    print("\n🔹 MENU:")
                    options = ["1.Place Order", "2.Modify Order", "3.Cancel Order", "4.View Positions", "5.Stream Market Data", "6.Get Order Book", "7.Exit"]
                    print("\n".join(options))
                    choice = input("Select an option: ")
                    actions = {"1": place_order, "2": modify_order, "3": cancel_order, "4": get_positions, "5": stream_market_data, "6": get_order_book}
                    if choice == "7":
                        print(" Exiting..."); return
                    await actions.get(choice, lambda ws: print("Invalid option."))(ws)
        except (websockets.exceptions.ConnectionClosed, asyncio.TimeoutError) as e:
            print(f" Connection lost: {str(e)}. Retrying in {BASE_DELAY} seconds...")
            await asyncio.sleep(BASE_DELAY)
            reconnect_attempts += 1
            BASE_DELAY *= 2
    print(" Max reconnection attempts reached. Exiting.")

asyncio.run(main())
