import time
import random
import json
import re
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage

# Initialize Tools
search_tool = DuckDuckGoSearchRun()
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.5)

def get_real_market_rate(crop_name, location="Nashik"):
    """
    Step 1: Search the web for the REAL market price.
    """
    try:
        # Search Query
        query = f"current wholesale market price {crop_name} {location} mandi rates India today per kg"
        search_results = search_tool.invoke(query)
        return search_results
    except:
        return "Market data unavailable. Assume base price is 20."

def broadcast_to_ondc(crop_data):
    """
    RAG-Powered Simulation:
    1. Finds the REAL price on the web.
    2. Generates 'Live Bids' centered around that real price.
    """
    # Simulate Network Latency (The "Searching..." feeling)
    time.sleep(1.5)
    
    crop = crop_data.get('crop_type', 'Vegetable')
    grade = crop_data.get('fci_grade', 'Grade B')
    location = "Nashik" # Default for demo
    
    # 1. RAG: Get Real Data
    real_market_context = get_real_market_rate(crop, location)
    
    # 2. LLM: Generate Structured Bids based on Real Data
    system_prompt = f"""
    You are the ONDC Network Gateway.
    
    CONTEXT:
    - Crop: {crop} ({grade})
    - Location: {location}
    - LATEST WEB SEARCH DATA: "{real_market_context}"
    
    TASK:
    Based on the REAL market prices found above, generate 3 realistic bids from Buyer Apps.
    - If the web says price is ₹20, generate bids around ₹19-₹24.
    - If Grade is 'Grade A', give a 10% premium.
    
    RETURN JSON ONLY:
    [
        {{
            "buyer_app": "BigBasket (via ONDC)", 
            "logo": "🥬", 
            "price": 24, 
            "distance": "12 km", 
            "rating": "4.8/5"
        }},
        ... (2 more)
    ]
    """
    
    try:
        # Invoke LLM
        response = llm.invoke([SystemMessage(content=system_prompt)])
        content = response.content
        
        # Clean JSON (remove markdown wrappers)
        if "```json" in content:
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            content = content.split("```")[1].strip()
            
        bids = json.loads(content)
        return bids

    except Exception as e:
        print(f"RAG Failed: {e}. Using Fallback.")
        # FALLBACK (Safe Mode if Internet fails)
        base = 25 if grade == "Grade A" else 18
        return [
            {"buyer_app": "BigBasket (via ONDC)", "logo": "🥬", "price": base+2, "distance": "12 km", "rating": "4.8/5"},
            {"buyer_app": "Reliance Fresh", "logo": "🏬", "price": base, "distance": "8 km", "rating": "4.5/5"},
            {"buyer_app": "Ninjacart (B2B)", "logo": "🥷", "price": base-1, "distance": "Pickup", "rating": "4.9/5"}
        ]

def generate_invoice(buyer, crop_data, qty):
    """Generates a smart contract invoice"""
    return {
        "invoice_id": f"ONDC-TXN-{random.randint(10000, 99999)}",
        "buyer": buyer['buyer_app'],
        "crop": crop_data.get('crop_type'),
        "quantity": f"{qty} kg",
        "price_per_kg": f"₹ {buyer['price']}",
        "total_amount": f"₹ {buyer['price'] * qty:,}",
        "status": "Smart Contract Locked 🔒",
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }