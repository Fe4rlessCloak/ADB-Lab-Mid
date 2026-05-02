import streamlit as st
from pymongo import MongoClient
import pandas as pd
import plotly.express as px
import time
# --- 1. SETUP & CONNECTION ---
st.set_page_config(page_title="Nexus DB Control", layout="wide")

@st.cache_resource
def init_connection():
    client = MongoClient("mongodb://admin:password@localhost:27017/")
    return client.NexusLogisticsDB

db = init_connection()

st.title("📦 Nexus Logistics | Core Operations")
st.markdown("---")
# --- 2. OVERVIEW SECTION (KPI COMMAND CENTER) ---
st.header("1. Global Operations Overview")

# 1. --- CACHED HEAVY QUERIES ---
# ttl=86400 caches the result for exactly 24 hours. 
@st.cache_data(ttl=86400)
def get_anomaly_alerts():
    # Anomaly Detection: Vehicles hitting critical engine temps (>105C)
    pipeline = [
        {"$match": {"metrics.engine_temp_c": {"$gt": 105}}},
        # Group by vehicle so we don't count the same overheating truck twice
        {"$group": {"_id": "$vehicle_id"}}
    ]
    # We return the length of the list, which is our unique vehicle count
    return len(list(db.telemetry_stream.aggregate(pipeline)))

@st.cache_data(ttl=300) # Cache this for 5 minutes, as shipment statuses change faster
def get_delayed_high_value():
    return db.shipment_ops.count_documents({
        "customs_clearance.declaration_value": {"$gte": 500000},
        "status_history.update": "Delayed"
    })

# 2. --- REAL-TIME COUNTS (Fast Operations) ---
total_shipments = db.shipment_ops.estimated_document_count()
total_drivers = db.driver_performance.estimated_document_count()
total_vehicles = db.fleet_assets.estimated_document_count()
in_transit_count = db.shipment_ops.count_documents({"status_history.update": "In-Transit"})

# Fetch cached complex data
critical_maintenance_count = get_anomaly_alerts()
delayed_high_value_count = get_delayed_high_value()

# 3. --- UI LAYOUT: TOP METRICS ---
c1, c2, c3, c4 = st.columns(4)
c1.metric("📦 Total Shipments", f"{total_shipments:,}")
c2.metric("🚚 In-Transit Shipments", f"{in_transit_count:,}")
# New Metric placed right next to In-Transit
c3.metric("⚠️ Delayed High-Value (>500k)", f"{delayed_high_value_count:,}", delta="Critical", delta_color="inverse")
c4.metric("🚛 Fleet Vehicles", f"{total_vehicles:,}")

st.markdown("---")

# 4. --- UI LAYOUT: CRITICAL ALERTS & REFRESH ---
col_alert1, col_alert2 = st.columns([3, 1])

with col_alert1:
    if critical_maintenance_count > 0:
        st.error(f"🚨 **URGENT:** {critical_maintenance_count} vehicles require immediate maintenance based on IoT Telemetry Anomalies (Engine Temp > 100°C).")
    else:
        st.success("✅ All telemetry data is within normal parameters. No immediate maintenance required.")

with col_alert2:
    # The Manual Refresh Button
    st.write("Last Anomaly Scan: Cached")
    if st.button("🔄 Force IoT Anomaly Scan Now"):
        # This clears the Streamlit cache and forces the queries to run again immediately
        st.cache_data.clear() 
        st.rerun() # Refreshes the UI instantly

st.markdown("---")

# --- 3. PRE-BAKED QUERIES ---
st.header("2. Common Operations (Pre-Indexed)")

tab_a, tab_b, tab_c, tab_d = st.tabs([
    "A: Driver Incidents", 
    "B: Shipment/Customer Search", 
    "C: Top 10 High-Value Shipments", 
    "D: Vehicle Maintenance"
])

# Query A: Search driver by ID and show their incidents
with tab_a:
    st.subheader("Driver Incident & Liability Center")
    
    # --- 1. INDIVIDUAL SEARCH ---
    st.markdown("#### Individual Driver Lookup")
    drv_search = st.text_input("Enter Driver ID:", placeholder="e.g., DRV_9084")
    if st.button("Search Driver"):

        start_time = time.time() # ⏱️ START TIMER
        incidents = list(db.incident_reports.find({"related_ids.driver_id": drv_search}, {"_id": 0}))
        end_time = time.time()   # ⏱️ STOP TIMER

        exec_ms = (end_time - start_time) * 1000
        
        incidents = list(db.incident_reports.find({"related_ids.driver_id": drv_search}, {"_id": 0}))
        if incidents:
            df_incidents = pd.json_normalize(incidents)
            st.success(f"Found {len(incidents)} incident(s) for {drv_search}. (Execution Time: {exec_ms:.2f} ms)")
            st.dataframe(df_incidents, use_container_width=True, hide_index=True)
        else:
            st.info(f"No incidents found. (Execution Time: {exec_ms:.2f} ms)")

    st.markdown("---")
    
    # --- 2. MONTHLY LIABILITY REPORT ---
    st.markdown("#### Monthly Liability Report (Top 20 Worst Offenders)")
    st.write("Aggregates driver incident damage estimates to assess financial liability.")
    
    col_m1, col_m2 = st.columns([1, 3])
    with col_m1:
        # Defaulting to index=4 (2026-05) since that's where your data lives
        selected_month = st.selectbox(
            "Select Billing Month:", 
            ["2026-01", "2026-02", "2026-03", "2026-04", "2026-05"], 
            index=4 
        )
        run_report = st.button("Generate Report")
        
    if run_report:
        
        pipeline = [
            {
                "$match": {
                    "incident_details.timestamp": {"$regex": f"^{selected_month}"}
                }
            },
            {
                "$group": {
                    "_id": "$related_ids.driver_id",
                    "total_damage_pkr": {"$sum": "$insurance_claim.damage_est_pkr"},
                    # FIXED: Just pushing the raw string ID instead of an object
                    "incident_list": {"$push": "$_id"} 
                }
            },
            {
                "$lookup": {
                    "from": "driver_performance",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "driver_info"
                }
            },
            {"$unwind": "$driver_info"},
            {
                "$project": {
                    "Driver ID": "$_id",
                    "Name": "$driver_info.name",
                    "Safety Score": "$driver_info.safety_score",
                    "Total Damage Caused (PKR)": "$total_damage_pkr",
                    "Incidents": "$incident_list",
                    "_id": 0
                }
            },
            {"$sort": {"Total Damage Caused (PKR)": -1}},
            {"$limit": 20}
        ]
        
         
        start_time = time.time() # ⏱️ START TIMER
        liability_data = list(db.incident_reports.aggregate(pipeline))
        end_time = time.time() # ⏱️ STOP TIMER

        exec_ms = (end_time - start_time) * 1000  

        if liability_data:
            st.success(f"Generated damage liability report for {selected_month}. (Execution Time: {exec_ms:.2f} ms)")
            
            df_liability = pd.DataFrame(liability_data)
            df_liability['Total Damage Caused (PKR)'] = df_liability['Total Damage Caused (PKR)'].apply(lambda x: f"PKR {x:,.2f}")
            df_liability = df_liability[['Driver ID', 'Name', 'Safety Score', 'Total Damage Caused (PKR)', 'Incidents']]
            
            st.dataframe(
                df_liability, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    # Streamlit will now render the list of strings beautifully
                    "Incidents": st.column_config.ListColumn("Incident IDs")
                }
            )
        else:
            st.info(f"No incident damage records found for {selected_month}. (Execution Time: {exec_ms:.2f} ms)")
# Query B: Search for a shipment by ID + Search all shipments by a customer
with tab_b:
    st.subheader("Shipment & Customer Lookup")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        ship_search = st.text_input("Find by Shipment ID:", placeholder="e.g., NEX-SHIP-000000")
        if st.button("Search Shipment"):
            start_time = time.time() # ⏱️ START TIMER
            shipment = db.shipment_ops.find_one({"_id": ship_search})
            end_time = time.time() # ⏱️ STOP TIMER
            exec_ms = (end_time - start_time) * 1000  
            if shipment:
                # FIXED: Visual layout replacing raw JSON
                st.markdown(f"#### Shipment Details: `{shipment['_id']}` (Execution Time: {exec_ms:.2f} ms)")
                
                # Core Metrics Row
                m1, m2, m3 = st.columns(3)
                m1.metric("Customer ID", shipment.get('customer_id', 'N/A'))
                m2.metric("Driver ID", shipment.get('assigned_driver', 'N/A'))
                m3.metric("Vehicle ID", shipment.get('assigned_vehicle', 'N/A'))
                
                # Customs Info
                customs = shipment.get('customs_clearance', {})
                st.info(f"**Customs Status:** {customs.get('status', 'N/A')} | **Declaration Value:** PKR {customs.get('declaration_value', 0):,} | **Customs ID:** {customs.get('customs_id', 'N/A')}")
                st.write(f"**Created At:** {shipment.get('created_at', 'N/A')} | **Path ID:** {shipment.get('path_id', 'N/A')}")
                
                # Embedded Arrays as clean tables
                st.markdown("##### Included Items")
                st.dataframe(pd.DataFrame(shipment.get('items', [])), use_container_width=True, hide_index=True)
                
                st.markdown("##### Status History")
                st.dataframe(pd.DataFrame(shipment.get('status_history', [])), use_container_width=True, hide_index=True)

            else:
                st.warning(f"Shipment not found. (Execution Time: {exec_ms:.2f} ms)")
                
    with col_s2:
        cust_search = st.text_input("Find by Customer ID:", placeholder="e.g., CUST_uOcdZ_PK")
        if st.button("Search Customer Operations"):
            start_time = time.time() # ⏱️ START TIMER
            cust_shipments = list(db.shipment_ops.find(
                {"customer_id": cust_search}, 
                {"_id": 1, "customs_clearance.status": 1, "assigned_driver": 1}
            ).limit(50)) 
            end_time = time.time() # ⏱️ STOP TIMER
            exec_ms = (end_time - start_time) * 1000
            if cust_shipments:
                df_cust = pd.json_normalize(cust_shipments)
                st.success(f"Showing up to 50 shipments for {cust_search}. (Execution Time: {exec_ms:.2f} ms)")
                st.dataframe(df_cust, use_container_width=True, hide_index=True)
            else:
                st.info(f"No shipments found for this customer. (Execution Time: {exec_ms:.2f} ms)")

# Query C: Top 10 highest value shipments right now, and their status
with tab_c:
    st.subheader("Top 10 High-Value Shipments")
    if st.button("Run High-Value Query"):
        start_time = time.time() # ⏱️ START TIMER
        top_10 = list(db.shipment_ops.find(
            {}, 
            {"_id": 1, "customs_clearance.declaration_value": 1, "customs_clearance.status": 1, "customer_id": 1}
        ).sort("customs_clearance.declaration_value", -1).limit(10))
        end_time = time.time() # ⏱️ STOP TIMER
        exec_ms = (end_time - start_time) * 1000
        st.info(f"(Execution Time: {exec_ms:.2f} ms)")
        if top_10:
            # FIXED: Explicitly defining the row dictionary to prevent pandas from swapping columns
            # FIXED: Added 'PKR' formatting to the value
            formatted_data = []
            for doc in top_10:
                formatted_data.append({
                    "Shipment ID": doc.get("_id"),
                    "Customer ID": doc.get("customer_id"),
                    "Declaration Value": f"PKR {doc.get('customs_clearance', {}).get('declaration_value', 0):,}",
                    "Status": doc.get("customs_clearance", {}).get("status", "Unknown")
                })
                
            df_top10 = pd.DataFrame(formatted_data)
            st.dataframe(df_top10, use_container_width=True, hide_index=True)

# Query D: Search a vehicle and show its maintenance history
with tab_d:
    st.subheader("Vehicle Maintenance History")
    veh_search = st.text_input("Enter Vehicle ID:", placeholder="e.g., VEH_DHW_15")
    if st.button("Search Vehicle"):
        start_time = time.time() # ⏱️ START TIMER
        maintenance = list(db.maintenance_history.find({"vehicle_id": veh_search}, {"_id": 0}))
        end_time = time.time() # ⏱️ STOP TIMER
        exec_ms = (end_time - start_time) * 1000
        if maintenance:
            df_maint = pd.json_normalize(maintenance)
            st.success(f"Found {len(maintenance)} maintenance record(s) for {veh_search}. (Execution Time: {exec_ms:.2f} ms)")
            st.dataframe(df_maint, use_container_width=True, hide_index=True)
        else:
            st.info(f"No maintenance history found for this vehicle. (Execution Time: {exec_ms:.2f} ms)")