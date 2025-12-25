import os
from langchain_groq import ChatGroq
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.prompts import ChatPromptTemplate

# Initialize Brains
llm = ChatGroq(model_name="llama-3.3-70b-versatile", temperature=0.3)
search_tool = DuckDuckGoSearchRun()

class BuyerAssistant:
    def explain_trust_score(self, certificate):
        """
        Uses AI to explain 'Why this score?' so it's not a black box.
        """
        score = certificate['current_harvest']['trust_score']
        crop = certificate['current_harvest']['crop']
        history = certificate['farmer_reputation']['score_history']
        
        # Dynamic Prompt
        prompt = f"""
        You are an expert Agricultural Quality Auditor. 
        Explain this Trust Score to a Buyer in simple terms.
        
        DATA:
        - Crop: {crop}
        - Current Score: {score}/100
        - History: {history}
        
        RULES:
        1. If score > 90: Explain that soil moisture was perfectly consistent (Stable variance).
        2. If score < 80: Warn about potential irrigation stress detected in the logs.
        3. Mention the farmer's history (e.g., "This farmer is consistent/improving").
        4. Keep it under 50 words. Professional tone.
        """
        response = llm.invoke(prompt)
        return response.content

    def get_fair_price_analysis(self, crop, location="Nashik"):
        """
        Fetches LIVE market price and calculates a 'Premium' based on the score.
        """
        # 1. Search Live Price
        try:
            query = f"current wholesale price {crop} {location} today per kg"
            search_res = search_tool.invoke(query)
        except:
            search_res = "Market volatile. Avg est: ₹25/kg."
            
        # 2. AI Pricing Logic
        prompt = f"""
        Act as a Market Analyst.
        
        CONTEXT:
        - Crop: {crop}
        - Market Data: {search_res}
        
        TASK:
        1. Identify the base market price range (e.g., ₹20-25).
        2. Suggest a 'Fair Price' for a GRADE A Verified crop (usually +20% premium).
        3. Return ONLY a JSON string like:
           {{"market_price": "₹22/kg", "suggested_premium": "₹26/kg", "reason": "High demand + Grade A premium"}}
        """
        
        response = llm.invoke(prompt)
        # Simple cleaning to ensure valid JSON
        content = response.content.replace("```json", "").replace("```", "").strip()
        return content

buyer_brain = BuyerAssistant()