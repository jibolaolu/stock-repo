from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import yfinance as yf
import os
import httpx
from dotenv import load_dotenv

# ✅ Load environment variables
load_dotenv()

# ✅ Use correct Spring Boot URL (avoid duplicate `/api/` in path)
SPRING_BOOT_URL = os.getenv("SPRING_BOOT_URL", "http://api.techbleats.eaglesoncloude.com:8080")

app = FastAPI()

# ✅ Health Check Endpoint
@app.get("/health")
async def health_check():
    return {"status": "UP"}

# ✅ CORS configuration
origins = [
    "http://localhost",
    "http://127.0.0.1",
    "https://techbleats.eaglesoncloude.com",
    "http://techbleats.eaglesoncloude.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # ✅ Allow frontend domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Define response model
class StockPriceResponse(BaseModel):
    ticker: str
    date: str
    price: float

# ✅ Fix API Path & Error Handling
@app.get("/api/stock/{ticker}", response_model=StockPriceResponse)
async def get_stock_price(ticker: str, date: str = None):
    # ✅ Ensure valid date format
    if date:
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD.")

    # ✅ Try Fetching Data from Spring Boot Cache
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{SPRING_BOOT_URL}/stock/{ticker}", params={"date": date})

        print(f"Response from {SPRING_BOOT_URL}/stock/{ticker}?date={date}: {response.status_code}")

        if response.status_code == 200:
            data = response.json()

            # ✅ Ensure `price` exists before returning response
            if "price" not in data:
                raise HTTPException(status_code=500, detail="Spring Boot API response missing 'price' field.")

            return StockPriceResponse(ticker=data["ticker"], date=data["date"], price=data["price"])

    except httpx.RequestError as e:
        print(f"Error reaching Spring Boot Backend: {e}")

    # ✅ Fetch Data from Yahoo Finance as Fallback
    try:
        stock = yf.Ticker(ticker)
        stock_data = stock.history(period="1d")

        if stock_data.empty:
            raise HTTPException(status_code=404, detail=f"No data found for {ticker} on {date}")

        # ✅ Extract price correctly
        price = round(stock_data['Close'].iloc[-1], 2) if not date else round(stock_data['Close'].iloc[0], 2)
        print(f"Stock price for {ticker}: {price}")

        # ✅ Store in cache (Spring Boot)
        try:
            async with httpx.AsyncClient() as client:
                cache_response = await client.post(
                    f"{SPRING_BOOT_URL}/stock/save",
                    params={"ticker": ticker, "date": date, "price": price}
                )
                print(f"Cache save response: {cache_response.status_code}")
        except httpx.RequestError as e:
            print(f"Error caching data in Spring Boot: {e}")

        return StockPriceResponse(ticker=ticker, date=date or str(datetime.today().date()), price=price)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch stock price: {str(e)}")
