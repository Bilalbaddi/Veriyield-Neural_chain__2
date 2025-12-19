import streamlit as st
import time
import pandas as pd
import numpy as np
from datetime import datetime
import io
import random

# --- CUSTOM MODULE IMPORTS ---
from utils.vision import analyze_crop_disease
from utils.insurance import check_weather_oracle, trigger_payout_transaction,generate_insurance_policy

from utils.carbon import calculate_green_score, mint_carbon_tokens
from utils.history import load_history, save_transaction
from utils.rag import agent_chain
from utils.market_agent import broker_agent
# Try to import Qrcode (Fail gracefully if not installed)
try:
    import qrcode
except ImportError:
    qrcode = None



from fpdf import FPDF




def generate_quality_pdf(result):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="VeriYield - FCI Quality Certificate", ln=1, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Grade: {result.get('fci_grade', 'N/A')}", ln=1)
    pdf.cell(200, 10, txt=f"Defects: {', '.join(result.get('visual_defects', []))}", ln=1)
    pdf.cell(200, 10, txt=f"Confidence: {result.get('confidence', 'N/A')}", ln=1)
    pdf.cell(200, 10, txt=f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", ln=1)
    
    # Save to a temporary file
    filename = "quality_certificate.pdf"
    pdf.output(filename)
    return filename

# --- CONFIGURATION ---
st.set_page_config(layout="wide", page_title="VeriYield Protocol", page_icon="🌾")

# --- SESSION STATE INITIALIZATION ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'chat_history' not in st.session_state: st.session_state.chat_history = []
if 'crop_data' not in st.session_state: st.session_state.crop_data = None
if 'last_analysis' not in st.session_state: st.session_state.last_analysis = None
if 'user_input' not in st.session_state: st.session_state.user_input = ""

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .verified-badge { 
        background-color: #E3F2FD; color: #1565C0; padding: 4px 12px; 
        border-radius: 20px; font-size: 0.8rem; border: 1px solid #90CAF9; 
        display: inline-block; margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: GOD MODE ---
with st.sidebar:
    st.title("⚙️ Protocol Admin")
    st.info("Simulating Polygon Amoy Network")
    god_mode = st.toggle("⚡ God Mode (Force Drought)", value=False)
    st.caption("Toggle to trigger Insurance Payout demo.")
    st.divider()
    st.caption("VeriYield Neural-Chain v2.0")
    st.divider()
    st.markdown("### 🎒 Farmer Wallet")

    
    history = load_history()

    # Calculate Balance dynamically
    balance = 0
    for h in history:
        if "ETH" in str(h['details']):
            balance += 0.5 # Simple logic for demo

    st.metric("Wallet Balance", f"{balance} ETH")

    with st.expander("📜 Transaction History"):
        for h in reversed(history[-5:]): # Show last 5
            st.caption(f"{h['timestamp']} - {h['type']}")
            st.code(h['details'].get('tx', 'N/A')[:10] + "...", language="text")

# --- LOGIN LAYER: ZK-IDENTITY ---
# --- LOGIN LAYER: ZK-IDENTITY & AGRISTACK ---
# --- LOGIN LAYER: ZK-IDENTITY & AGRISTACK ---
if not st.session_state.logged_in:
    st.markdown("<div style='text-align: center; padding: 40px;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size: 3rem;'>🔐 VeriYield Protocol</h1>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 1.2rem; color: #666;'>Decentralized Agricultural Risk & Commerce Layer</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        # 1. ZK-Identity Login Card
        with st.container():
            st.markdown("### 🆔 Connect Identity")
            st.info("Authenticating via Anon Aadhaar (ZK-Proof)...")
            
            # Consent Checkbox (DEPA Compliance)
            consent = st.checkbox("I authorize VeriYield to fetch my Land Records from AgriStack (UFSI).", value=True)
            
            if st.button("Connect Identity (Zero-Knowledge)", type="primary", use_container_width=True, disabled=not consent):
                
                # STEP 1: ZK PROOF GENERATION
                with st.spinner("Generating Cryptographic Proof (ZK-SNARK)..."):
                    time.sleep(1.5) # Simulate heavy computation
                    st.success("✅ Proof Verified: Resident of Maharashtra (Valid Aadhaar)")
                    time.sleep(0.5)
                
                # STEP 2: AGRISTACK SIMULATION (The New Feature)
                # This simulates calling the UFSI API mentioned in your research
                with st.status("🚜 Accessing AgriStack Farmland Registry...", expanded=True) as status:
                    st.write("📡 Connecting to UFSI Gateway...")
                    time.sleep(0.8)
                    
                    st.write("🔍 Querying Farmer ID: `F-2025-MH-12345`")
                    time.sleep(0.8)
                    
                    st.write("📍 Found Land Parcel: **Survey No. 45/2A (Nashik)**")
                    time.sleep(0.8)
                    
                    st.write("📐 Verifying Geo-Polygon Geometry...")
                    time.sleep(0.5)
                    
                    status.update(label="✅ Digital Twin Linked Successfully!", state="complete", expanded=False)
                
                # SAVE MOCK DATA TO SESSION FOR MAPS LATER
                st.session_state.land_data = {
                    "survey_no": "45/2A",
                    "area": "2.5 Hectares",
                    "lat": 19.9975,
                    "lon": 73.7898,
                    "district": "Nashik"
                }
                
                time.sleep(1)
                st.session_state.logged_in = True
                st.rerun()

else:
    # --- MAIN APPLICATION ---
    st.markdown("## 🌾 VeriYield Dashboard")
    
    # The 5 Pillars of the Protocol
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Vision & Grading", 
        "Supply Chain & Trust",
        "Insurance (DeFi)", 
        "Market Negotiator",
        "Sustainability"
    ])

    # --- TAB 1: VISION & FCI GRADING ---
    with tab1:
        st.subheader("FCI-Standard Quality Assayer")
        col_img, col_metrics = st.columns([1, 1])
        
        with col_img:
            img = st.file_uploader("Upload Crop Image", type=['jpg', 'png', 'jpeg'])
            if img:
                st.image(img, caption="Field Capture", use_column_width=True)
        
        with col_metrics:
            if img and st.button("Analyze Quality", type="primary"):
                with st.spinner("Running Llama-Vision Assayer..."):
                    result = analyze_crop_disease(img)
                    st.session_state.crop_data = result
                    st.session_state.last_analysis = result # For Tab 2 compatibility
                    
                    # Display Results
                    st.markdown(f"### Grade: {result.get('fci_grade', 'N/A')}")
                    
                    m1, m2 = st.columns(2)
                    m1.metric("Est. Size", result.get('estimated_size_mm', 'N/A'))
                    m2.metric("Confidence", result.get('confidence', 'N/A'))
                    
                    st.write("**Visual Defects:**")
                    st.write(", ".join(result.get('visual_defects', ['None'])))
                    
                    st.info(f"**Explanation:** {result.get('explanation', 'Analysis complete.')}")
                    st.divider()
                    st.subheader("🧠 Multi-Modal Research Agent")
                    
                    with st.status("🕵️ Agent is searching the web...", expanded=True) as status:
                        st.write(f"🔍 Searching: '{result.get('search_term', 'Crop disease treatment')}'")
                        st.write("🌐 Browsing: agmarknet.gov.in, amazon.in, krishijagran.com...")
                        
                        # CALL THE LANGGRAPH AGENT
                        advisory = agent_chain.generate_detailed_advisory(
                            disease_data=result,
                            weather_context="Live", # Agent fetches this automatically now
                            market_context="Live"
                        )
                        status.update(label="✅ Research Complete!", state="complete", expanded=False)
                    
                    # Display the Agent's Report
                    st.markdown(advisory)
                    
                    if result.get('fci_grade') == 'Grade A':
                        st.balloons()
                        pdf_file = generate_quality_pdf(result)
                        with open(pdf_file, "rb") as f:
                            st.download_button(
                                label="📄 Download FCI Quality Certificate",
                                data=f,
                                file_name="VeriYield_Certificate.pdf",
                                mime="application/pdf"
                            )


    # --- TAB 2: SUPPLY CHAIN (SIMULATED BLOCKCHAIN) ---
    # --- TAB 2: SUPPLY CHAIN (Enterprise Logistics Layer) ---
    with tab2:
        st.subheader("🚛 Logistics Control Tower & Digital Passport")
        
        # 1. 3D INTERACTIVE ROUTE MAP (PyDeck)
        # Real-world apps use ArcLayers to show connection, not just dots.
        import pydeck as pdk
        
        # Route: Nashik (Farm) -> Mumbai (Port/Market)
        route_data = [{
            "from_name": "Nashik Farm (Survey 24/A)",
            "to_name": "Mumbai APMC Port",
            "start": [73.7898, 19.9975], # Lon, Lat
            "end": [73.0297, 19.0330],
            "distance": "167 km"
        }]
        
        # Define the 3D Map Layers
        layer_arc = pdk.Layer(
            "ArcLayer",
            data=route_data,
            get_source_position="start",
            get_target_position="end",
            get_width=5,
            get_tilt=15,
            get_source_color=[46, 125, 50, 160], # Green
            get_target_color=[255, 140, 0, 160], # Orange
        )
        
        layer_scatter = pdk.Layer(
            "ScatterplotLayer",
            data=route_data,
            get_position="start",
            get_color=[46, 125, 50],
            get_radius=8000, # 8km radius visual
            pickable=True,
        )

        # Render Map
        view_state = pdk.ViewState(latitude=19.5, longitude=73.4, zoom=7, pitch=45)
        r = pdk.Deck(
            layers=[layer_arc, layer_scatter], 
            initial_view_state=view_state,
            tooltip={"text": "{from_name} ➝ {to_name}"}
        )
        
        c1, c2 = st.columns([2, 1])
        with c1:
            st.markdown("### 📍 Live Fleet Tracking")
            st.pydeck_chart(r)
        
        with c2:
            st.markdown("### 📡 IoT Sensor Telemetry")
            st.caption("Monitoring Cold Chain Integrity (Reefer Truck #MH-15-GT-9921)")
            
            # Simulated IoT Data (Temp/Humidity)
            telemetry = pd.DataFrame({
                'Temp (°C)': np.random.normal(4, 0.5, 24), # Ideal cold storage is 4°C
                'Humidity (%)': np.random.normal(85, 2, 24)
            })
            st.line_chart(telemetry['Temp (°C)'], height=150)
            
            avg_temp = telemetry['Temp (°C)'].mean()
            if avg_temp < 6:
                st.success(f"✅ Cold Chain Intact (Avg: {avg_temp:.1f}°C)")
            else:
                st.error(f"⚠️ Temperature Breach Detected! ({avg_temp:.1f}°C)")

        st.divider()

        # 2. IMMUTABLE BLOCKCHAIN PASSPORT
        st.markdown("### ⛓️ Digital Product Passport (DPP)")
        
        if not st.session_state.last_analysis:
            st.warning("⚠️ Pending: Analyze Crop in Tab 1 to generate passport.")
        else:
            result = st.session_state.last_analysis
            
            # Create the 'Block' Data
            passport_data = {
                "asset_id": f"CROP-{random.randint(1000,9999)}",
                "farmer_id": "0x71C...9E3F",
                "grade": result.get('fci_grade'),
                "harvest_date": datetime.now().strftime("%Y-%m-%d"),
                "origin": "Nashik, Maharashtra",
                "sustainability_score": st.session_state.get('carbon_result', {}).get('score', 'N/A')
            }
            
            c_a, c_b = st.columns(2)
            
            with c_a:
                st.info("📦 **Asset Metadata (JSON)**")
                st.json(passport_data)
                
            with c_b:
                st.write("#### 🛡️ Mint to Blockchain")
                st.caption("Hashes data to Polygon Amoy Network for traceability.")
                
                if st.button("🔗 Mint Digital Twin", type="primary"):
                    with st.spinner("Hashing Data & Generarting QR..."):
                        time.sleep(1.5)
                        tx_hash = "0x" + "".join([random.choice("0123456789abcdef") for _ in range(64)])
                        
                        # Generate REAL QR Code containing the Data
                        import qrcode
                        qr = qrcode.QRCode(box_size=10, border=4)
                        qr.add_data(str(passport_data)) # Encode the actual JSON
                        qr.make(fit=True)
                        img_qr = qr.make_image(fill_color="black", back_color="white")
                        
                        # Convert for Streamlit
                        import io
                        img_byte_arr = io.BytesIO()
                        img_qr.save(img_byte_arr, format='PNG')
                        img_byte_arr = img_byte_arr.getvalue()
                        
                        st.success("✅ Token Minted Successfully!")
                        st.write(f"**Tx Hash:** `{tx_hash}`")
                        
                        # Show QR
                        st.image(img_byte_arr, caption="Scan for Supply Chain History", width=150)
                        
                        # Download Button
                        st.download_button("⬇️ Download QR Label", img_byte_arr, "product_passport.png", "image/png")

    # --- TAB 3: PARAMETRIC INSURANCE ---
    # --- TAB 3: PARAMETRIC INSURANCE (Advanced) ---
    with tab3:
        st.subheader("☔ Parametric Insurance Oracle")
        st.caption("Smart Contract auto-claims based on Weather Oracle data.")
        
        # 1. Policy Download Section (New!)
        with st.expander("📄 Active Smart Policy Details", expanded=False):
            st.info("Policy #8492 active for Nashik Region.")
            from utils.insurance import generate_insurance_policy
            if st.button("Download Signed Policy Document"):
                pdf_path = generate_insurance_policy("Ramesh Patil", "Nashik")
                with open(pdf_path, "rb") as f:
                    st.download_button("Download PDF", f, "VeriYield_Policy.pdf", "application/pdf")

        st.divider()

        # 2. Oracle Monitor
        status = check_weather_oracle("Nashik", god_mode)
        
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Live Rainfall", f"{status['rainfall_mm']} mm")
            # Show Severity Badge
            if status['severity'] == "Normal":
                st.success(f"Condition: {status['condition']}")
            else:
                st.error(f"⚠️ Condition: {status['severity']}")
        
        with col_b:
            if status['trigger_met']:
                st.error("🚨 PARAMETRIC TRIGGER ACTIVATED")
                st.markdown(f"**Payout Tier:** {status['payout_amount']}")
                
                if st.button("Execute Smart Contract Payout"):
                    with st.spinner("Verifying Oracle Data & Transferring Funds..."):
                        # Pass the calculated amount to the transaction
                        tx = trigger_payout_transaction("0xUserWallet", status['payout_amount'])
                        st.success(f"💰 Funds Transferred: {status['payout_amount']}")
                        st.code(tx['tx_hash'], language="text")
            else:
                st.success("✅ Risk Threshold Not Breached.")
                st.caption("System monitoring for >50mm Rainfall.")
    # --- TAB 4: MARKET NEGOTIATOR ---
   # --- TAB 4: MARKET NEGOTIATOR (The "Raju Bhai" Agent) ---
   # --- TAB 4: MARKET & ONDC COMMERCE ---
    with tab4:
        st.subheader("🤝 e-NAM & ONDC Smart-Mandi")
        st.caption("Decentralized Commerce: Negotiate locally or connect with National Buyers.")

        # Import the Agents
        from utils.market_agent import broker_agent
        from utils.ondc import broadcast_to_ondc, generate_invoice
        
        if not st.session_state.crop_data:
            st.warning("⚠️ Please analyze a crop in Tab 1 first to establish quality.")
        else:
            # Layout: Left = Chat (Raju Bhai), Right = ONDC Network
            col_chat, col_ondc = st.columns([1, 1.2])
            
            # --- LEFT COLUMN: RAJU BHAI (Negotiation Agent) ---
            with col_chat:
                st.markdown("### 🤖 Local Mandi Agent")
                
                # Chat Container
                chat_container = st.container(height=400)
                
                # Display History
                with chat_container:
                    if not st.session_state.chat_history:
                        crop = st.session_state.crop_data.get('crop_type', 'Crop')
                        grade = st.session_state.crop_data.get('fci_grade', 'Standard')
                        greeting = f"Ram Ram Sir ji! I see you have some {crop} ({grade}). Market is busy today. What is your expected rate (Bhaav)?"
                        st.session_state.chat_history.append({"role": "assistant", "content": greeting})
                    
                    for msg in st.session_state.chat_history:
                        avatar = "👳" if msg['role'] == "assistant" else "👨‍🌾"
                        st.chat_message(msg['role'], avatar=avatar).write(msg["content"])

                # Quick Chips
                st.markdown("###### 🗣️ Quick Ask")
                cols = st.columns(3)
                if cols[0].button("Trend?"): st.session_state.user_input = "What is the market trend?"
                if cols[1].button("Best Price?"): st.session_state.user_input = "Give me your best final rate."
                if cols[2].button("Hold?"): st.session_state.user_input = "Should I sell now or wait?"

                # Chat Input
                prompt = st.chat_input("Message Raju Bhai...")
                if prompt: st.session_state.user_input = prompt

                # Chat Logic
                if st.session_state.user_input:
                    user_msg = st.session_state.user_input
                    st.session_state.user_input = "" 
                    
                    st.session_state.chat_history.append({"role": "user", "content": user_msg})
                    with chat_container: st.chat_message("user", avatar="👨‍🌾").write(user_msg)
                    
                    with st.spinner(f"{broker_agent.name} is checking rates..."):
                        response = broker_agent.chat_with_broker(st.session_state.chat_history, st.session_state.crop_data, user_msg)
                    
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    with chat_container: st.chat_message("assistant", avatar="👳").write(response)
                    st.rerun()

            # --- RIGHT COLUMN: ONDC NETWORK (The "Real World" Feature) ---
            with col_ondc:
                st.markdown("### 🌐 ONDC National Grid")
                
                with st.container():
                    # Listing Card
                    st.markdown(f"""
                    <div style="background: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; margin-bottom: 15px;">
                        <h4 style="margin:0; color: #2E7D32;">📦 Active Listing: {st.session_state.crop_data.get('crop_type')}</h4>
                        <p style="margin:0; font-size: 0.9rem;">Grade: <b>{st.session_state.crop_data.get('fci_grade')}</b> | Verified by Vision AI</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    qty = st.slider("Quantity to Sell (kg)", 100, 5000, 500)
                    
                    st.info("💡 **Pro Tip:** Use the 'Broadcast' button below to find REAL market rates via the ONDC Gateway.")
                    
                    # THE "REAL WORLD" MOMENT
                    if st.button("📡 Broadcast to ONDC Network", type="primary", use_container_width=True):
                        with st.status("🔄 Handshaking with ONDC Gateway...", expanded=True):
                            st.write("🔍 Searching for active Buyer Apps...")
                            time.sleep(1)
                            st.write("📡 Pinging BigBasket, Blinkit, Ninjacart...")
                            time.sleep(1)
                            
                            # CALL THE NEW RAG-POWERED FUNCTION
                            st.session_state.bids = broadcast_to_ondc(st.session_state.crop_data)
                            
                            st.write(f"✅ {len(st.session_state.bids)} Competitive Bids Received!")
                    
                    # Display Bids
                    if 'bids' in st.session_state:
                        st.markdown("#### ⚡ Live Bids (Expires in 5:00)")
                        
                        for bid in st.session_state.bids:
                            with st.container():
                                # Custom Card Layout for Bid
                                c1, c2, c3 = st.columns([0.8, 2, 1.2])
                                with c1: st.markdown(f"## {bid['logo']}")
                                with c2: 
                                    st.write(f"**{bid['buyer_app']}**")
                                    st.caption(f"⭐ {bid['rating']} • {bid['distance']}")
                                with c3:
                                    st.metric("Offer", f"₹{bid['price']}/kg")
                                    if st.button(f"Accept", key=bid['buyer_app']):
                                        inv = generate_invoice(bid, st.session_state.crop_data, qty)
                                        st.session_state.invoice = inv
                                        st.rerun()
                        
                        # Show Invoice if Deal Accepted
                        # ... (Previous code for displaying bids) ...
                        
                        # Show Invoice if Deal Accepted
                        if 'invoice' in st.session_state:
                            st.divider()
                            inv = st.session_state.invoice
                            
                            # 1. VISUAL RECEIPT CARD
                            st.markdown(f"""
                            <div style="background-color: #F0FDF4; border: 1px solid #22C55E; border-radius: 10px; padding: 20px; text-align: center;">
                                <h2 style="color: #15803D; margin:0;">🎉 Deal Confirmed!</h2>
                                <p style="color: #166534;">Smart Contract Locked on ONDC Network</p>
                                <hr style="border-top: 1px dashed #22C55E; margin: 15px 0;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                    <strong>Buyer:</strong> <span>{inv['buyer']}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                    <strong>Quantity:</strong> <span>{inv['quantity']}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                    <strong>Total Payout:</strong> <span style="font-size: 1.2rem; font-weight: bold; color: #15803D;">{inv['total_amount']}</span>
                                </div>
                                <div style="font-family: monospace; background: #e6e6e6; padding: 5px; border-radius: 5px; font-size: 0.8rem; margin-top: 10px;">
                                    Contract Hash: {inv['invoice_id']}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            st.balloons()
                            
                            # 2. DOWNLOAD ACTION
                            # Convert JSON to String for download
                            json_str = json.dumps(inv, indent=4)
                            st.download_button(
                                label="⬇️ Download Digital Contract (JSON)",
                                data=json_str,
                                file_name=f"veriyield_invoice_{inv['invoice_id']}.json",
                                mime="application/json",
                                type="primary"
                            )
    # --- TAB 5: SUSTAINABILITY ---
    # --- TAB 5: SUSTAINABILITY (Fixed Logic) ---
    # --- TAB 5: SUSTAINABILITY (With AI "Proof of Green") ---
    with tab5:
        st.subheader("🌍 Regenerative Farming Audit (AI-Verified)")
        
        # Import the new function
        from utils.vision import verify_sustainable_practice

        with st.form("carbon_audit"):
            st.info("📝 Self-Reporting Protocol")
            c1, c2 = st.columns(2)
            with c1:
                tillage = st.selectbox("Tillage Method", ["Conventional", "No-Till (+20 pts)"])
                irrigation = st.selectbox("Irrigation Type", ["Flood", "Drip (+15 pts)", "Sprinkler"])
            with c2:
                fertilizer = st.selectbox("Fertilizer", ["Synthetic", "Organic (+15 pts)"])
                cover_crop = st.checkbox("Used Cover Crops? (+10 pts)")
            
            st.divider()
            st.info("📸 Proof of Work (Required for High Scores)")
            audit_img = st.file_uploader("Upload Field Photo for AI Verification", type=['jpg', 'png'])
            
            submitted = st.form_submit_button("Run AI Audit & Calculate Score")
            
        if submitted:
            # 1. Base Calculation
            inputs = {
                "tillage": "No-Till" if "No-Till" in tillage else "Conventional",
                "irrigation": "Drip" if "Drip" in irrigation else "Flood",
                "fertilizer": "Organic" if "Organic" in fertilizer else "Synthetic",
                "cover_crop": cover_crop
            }
            base_result = calculate_green_score(inputs)
            final_score = base_result['total_score']
            
            # 2. AI Verification Layer (The "Advanced" Upgrade)
            verification_bonus = False
            if audit_img:
                with st.spinner("AI Auditor is inspecting the field..."):
                    # We verify the highest value claim (e.g., No-Till or Drip)
                    claim_to_check = inputs['tillage'] if inputs['tillage'] == 'No-Till' else inputs['irrigation']
                    audit_result = verify_sustainable_practice(audit_img, claim_to_check)
                    
                    if audit_result.get('verified'):
                        st.success(f"AI Verified: {claim_to_check}")
                        st.caption(f"Evidence: {audit_result.get('evidence')}")
                        final_score += 20 # BONUS for Verified Proof
                        verification_bonus = True
                    else:
                        st.error(f"AI Rejection: Could not verify {claim_to_check}")
                        st.caption(f"Reason: {audit_result.get('evidence')}")
            
            # 3. Save to Session State
            st.session_state.carbon_result = {
                "score": final_score,
                "tokens": int(final_score * 0.5),
                "breakdown": base_result['breakdown']
            }
            if verification_bonus:
                st.session_state.carbon_result['breakdown'].append("🌟 +20: AI Visual Proof Bonus")

        # 4. Results & Minting
        if 'carbon_result' in st.session_state:
            res = st.session_state.carbon_result
            
            st.metric("VeriYield Green Score", f"{res['score']}/170")
            for item in res['breakdown']: st.caption(item)
                
            if res['score'] > 100:
                st.success(f"🎉 Eligible for {res['tokens']} AgriTokens!")
                if st.button("Mint Carbon Credits (ERC-20)"):
                    with st.spinner("Minting on Polygon..."):
                        tx = mint_carbon_tokens("0xUser", res['tokens'])
                        st.balloons()
                        st.success(f"Minted {res['tokens']} Tokens!")
                        st.code(tx['tx_hash'], language="text")
            else:
                st.warning("Score too low. Upload photo proof to boost score!")