import streamlit as st
import subprocess
import os
import pandas as pd
import time

# Custom Styling
st.set_page_config(page_title="EcoTraffic AI", page_icon="🌱")

st.title("🌱 EcoTraffic: AI Traffic Light Optimizer")
st.markdown("""
    This project uses **Reinforcement Learning** to reduce idle vehicle emissions 
    by dynamically adjusting traffic lights.
""")

# Sidebar for Configuration
st.sidebar.header("Simulation Settings")
sim_duration = st.sidebar.slider("Simulation Duration (seconds)", 100, 100000, 1000)

# Main Dashboard
col1, col2 = st.columns(2)

with col1:
    # Use a single button to trigger the side-by-side comparison
    if st.button("🏁 Run Comparative Simulation"):
        st.info("Launching simultaneous simulations...")
        
        # 1. Start the first process (Demo/AI)
        # Using Popen makes it non-blocking
        proc1 = subprocess.Popen(["python", "demo.py"])
        
        # 2. Add your 50ms delay
        time.sleep(0.05) 
        
        # 3. Start the second process (Baseline)
        proc2 = subprocess.Popen(["python", "baseline.py"]) 
        # Wait for both to finish before showing success
        proc1.wait()
        proc2.wait()
        
        st.success("Both simulations finished!")

with col2:
    if st.button("📊 Show Impact Report"):
        st.write("Generating Sustainability Report...")
        # Replace this with real data reading from your project files
        chart_data = pd.DataFrame({
            'Standard Timing': [500, 480, 510, 490],
            'AI Optimized': [400, 380, 390, 370]
        })
        st.line_chart(chart_data)

# Impact Metrics
st.divider()
st.subheader("Real-Time Sustainability Metrics")
m1, m2= st.columns(2)
m1.metric("CO2 Saved", "201.24 kg", "-83.04%", delta_color="green")
#Total idling seconds/total iteratios = average time waiting (done in calculation)
m2.metric("Avg. Wait Time", "34s", "Increased 90%", delta_color="green")
