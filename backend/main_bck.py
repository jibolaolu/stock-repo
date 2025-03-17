from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import yfinance as yf
import pickle
import os
import time
import httpx

from dotenv import load_dotenv


# Load environment variables from the .env file
load_dotenv()

# Get SPRING_BOOT_URL from environment variables
SPRING_BOOT_URL = os.getenv("SPRING_BOOT_URL", "http://localhost:8080")  # Default to localhost if not found


app = FastAPI()

@app.get("/health")
async def health_check():
        return {"status": "UP"}

# CORS configuration
origins = [
    "http://localhost",  # Allow requests from localhost
    "http://localhost:80",  # Allow requests from localhost on port 3000 (if you use React, for example)
    "http://127.0.0.1",
    "http://techbleats.eaglesoncloude.com/",
    "https://techbleats.eaglesoncloude.com/"
]

# Add CORSMiddleware to allow CORS for the specified origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows CORS for these origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

# Define the response model
class StockPriceResponse(BaseModel):
    ticker: str
    date: str
    price: float


@app.get("/api/stock/{ticker}", response_model=StockPriceResponse)
async def get_stock_price(ticker: str, date: str = None):

    async with httpx.AsyncClient() as client:
        response = await client.get(f"{SPRING_BOOT_URL}/{ticker}/{date}")
    
    print (f"response code for {SPRING_BOOT_URL}/{ticker}/{date} is {response.status_code}")

    if response.status_code == 200:
        price = response.json()
        return StockPriceResponse(ticker=ticker, date=date, price=price)

    price = "yay"
    try:
        stock = yf.Ticker(ticker)
        print (f"about to post 1 {price}")

        if date:
            print (f"about to post 0 {price}")
            stock_date = datetime.strptime(date, "%Y-%m-%d")
            stock_data = stock.history(period="1d")
            print (f"about to post 2 {price}")
            if stock_data.empty:
                print (f"about to post 3 {price}")
                raise HTTPException(status_code=404, detail="No data for this date")
            price = round (stock_data['Close'].iloc[0], 2)
            print (f"about to post 3b {price} ")
        else:
            stock_data = stock.history(period="1d")
            price = round (stock_data['Close'].iloc[-1] , 2)
        
            print (f"about to post 4 {price}")

        print (f"about to post {price}")

        #cache_data = {"price": price}

        async with httpx.AsyncClient() as client:
          await client.post(f"{SPRING_BOOT_URL}/save?ticker={ticker}&date={date}&price={price}")

        return StockPriceResponse(ticker=ticker, date=date or str(datetime.today().date()), price=price)

    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


