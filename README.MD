# Deribit WebSocket Trading Bot

This Python program connects to Deribit via WebSocket, allowing users to place, modify, and cancel orders, stream market data, and view positions interactively.

## Features
- Authenticate using client credentials.
- Place buy/sell orders (market & limit).
- Modify or cancel existing orders.
- Fetch open positions.
- Stream market data in real time.
- Retrieve the latest order book.
- Automatic reconnection handling.

## Prerequisites
- Python 3.7+
- `websockets`

## Installation
1. Clone the repository:
   ```sh
   git clone https://github.com/your-repo/deribit-trading-bot.git
   cd deribit-trading-bot
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up environment variables:
   - Create a `.env` file in the project directory.
   - Add the following lines:
     ```ini
     CLIENT_ID=your_client_id
     CLIENT_SECRET=your_client_secret
     ```

## Usage
Run the script using:
```sh
python main.py
```

## Menu Options
When running the program, users can choose from the following options:
1. **Place Order** - Submit a buy or sell order.
2. **Modify Order** - Update an existing order's amount or price.
3. **Cancel Order** - Cancel an existing order by ID.
4. **View Positions** - Retrieve open positions for a given currency.
5. **Stream Market Data** - Subscribe to real-time market updates.
6. **Get Order Book** - View the order book for a given instrument.
7. **Exit** - Close the program.

## Error Handling & Reconnection
- The bot will attempt to reconnect up to 5 times with exponential backoff if the WebSocket connection is lost.
- Users should ensure their `CLIENT_ID` and `CLIENT_SECRET` are correctly set in the `.env` file to authenticate successfully.


