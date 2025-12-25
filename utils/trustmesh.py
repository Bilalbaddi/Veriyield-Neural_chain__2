import pandas as pd
import numpy as np
import random
import hashlib
import json
from datetime import datetime, timedelta

class TrustMeshOracle:
    def __init__(self):
        # Simulating a connection to a MongoDB cluster
        self.connection_status = "Connected to Cluster: verified-nodes-mumbai-1"
    
    def fetch_sensor_history(self, farm_id, crop_type):
        """
        Generates a 90-day realistic sensor log for a crop.
        (Same logic as before...)
        """
        dates = [datetime.now() - timedelta(days=x) for x in range(90)]
        dates.reverse()
        
        # Base parameters based on crop (Tomato/Wheat)
        if crop_type == "Tomato":
            ideal_moisture = 60
            ideal_temp = 24
        else:
            ideal_moisture = 40
            ideal_temp = 28
            
        data = []
        abnormalities = 0
        
        for d in dates:
            noise = random.uniform(-2, 2)
            is_stress = random.random() > 0.95
            
            moisture = ideal_moisture + noise
            if is_stress: 
                moisture -= 15
                abnormalities += 1
            
            temp = ideal_temp + noise
            
            irrigated = False
            if moisture < (ideal_moisture - 5):
                moisture += 10
                irrigated = True
                
            data.append({
                "date": d.strftime("%Y-%m-%d"),
                "soil_moisture": round(moisture, 1),
                "temperature": round(temp, 1),
                "humidity": round(random.uniform(40, 60), 1),
                "irrigation_event": irrigated,
                "stress_detected": is_stress
            })
            
        df = pd.DataFrame(data)
        trust_score = max(0, 100 - (abnormalities * 5))
        
        return df, trust_score

    def generate_agentic_log(self, df):
        """Extracts key 'Agent Actions' from the data history."""
        logs = []
        stress_days = df[df['stress_detected'] == True]
        
        for index, row in stress_days.head(3).iterrows():
            logs.append(f"⚠️ {row['date']}: Moisture dropped to {row['soil_moisture']}%. Alert sent to farmer.")
            
        irrigation_days = df[df['irrigation_event'] == True]
        for index, row in irrigation_days.tail(3).iterrows():
            logs.append(f"💧 {row['date']}: Verified irrigation cycle completed.")
            
        logs.append("✅ Today: Crop is harvest-ready. Quality locked.")
        return logs

    def mint_digital_identity(self, farm_id, crop, current_score):
        """
        Creates the Cryptographic Proof of Quality.
        NOW INCLUDES: Historical Performance Data.
        """
        raw_data = f"{farm_id}-{crop}-{current_score}-{datetime.now()}"
        hash_id = hashlib.sha256(raw_data.encode()).hexdigest()
        
        # GENERATE FAKE HISTORY (Simulates previous harvests)
        # This proves the farmer is consistently good, not just lucky once.
        history = [
            {"date": "2024-06-15", "crop": "Wheat", "score": random.randint(80, 95)},
            {"date": "2024-02-20", "crop": "Onion", "score": random.randint(75, 90)},
            {"date": "2023-11-10", "crop": "Tomato", "score": random.randint(85, 98)},
        ]
        
        certificate = {
            "certificate_id": f"VY-{hash_id[:8].upper()}",
            "farm_node_id": farm_id,
            "current_harvest": {
                "crop": crop,
                "trust_score": current_score,
                "verification_method": "IoT_SENSOR_CONSENSUS",
                "grade": "Grade A" if current_score > 85 else "Grade B"
            },
            "farmer_reputation": {
                "total_harvests_verified": 4, # 3 history + 1 current
                "average_score": int((sum(h['score'] for h in history) + current_score) / 4),
                "score_history": history  # <-- NEW FIELD ADDED HERE
            },
            "blockchain_hash": f"0x{hash_id}",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        return certificate

# Singleton Instance
mesh_agent = TrustMeshOracle()