import json
import random
import os
from faker import Faker

fake = Faker()
output_dir = "NexusData_Output"
os.makedirs(output_dir, exist_ok=True)

# --- SCALING PARAMETERS ---
NUM_CUSTOMERS = 2000
NUM_DRIVERS = 650
NUM_VEHICLES = 700
NUM_SHIPMENTS = 50000
NUM_TELEMETRY = 250000 
NUM_MAINTENANCE = 15000
NUM_INCIDENTS = 1500

# --- REFERENTIAL POOLS ---
pools = {
    "CUST": [], "DRV": [], "VEH": [], "SHIP": [], 
    "PROV": ["PUNJAB", "SINDH", "KPK", "BALOCHISTAN", "GB"], 
    "PATH": [], "VND": []
}

def save_json(data, name):
    with open(f"{output_dir}/{name}.json", "w") as f:
        json.dump(data, f, indent=2)
    print(f"✔ {name}.json -> {len(data)} records")

# ==========================================
# PHASE 1: INDEPENDENT & STATIC DATA
# ==========================================
def gen_phase_1():
    # 7) Regional-Policies
    regional = []
    for p in pools["PROV"]:
        p_id = f"PROV_{p}"
        regional.append({
            "_id": p_id,
            "name": p.capitalize(),
            "tax_rules": {"gst_rate": 0.16, "transit_tax_fixed": 500.00},
            "local_laws": [{"law_id": fake.bothify("LAW_???_##"), "law_text": fake.sentence(), "penalty": random.randint(1000, 10000)}],
            "management_contacts": [{"role": "Regional Manager", "name": fake.name(), "phone": fake.phone_number()}]
        })
    save_json(regional, "regional_policies")

    # 10) Supplier-Network
    suppliers = []
    for i in range(20):
        v_id = f"VND_{fake.bothify('???_##')}"
        pools["VND"].append(v_id)
        suppliers.append({
            "_id": v_id,
            "vendor_name": fake.company(),
            "category": random.choice(["Electronics", "Auto Parts", "Textiles", "Medical"]),
            "contact_details": {"primary_email": fake.company_email(), "phone": fake.phone_number(), "address": fake.address()},
            "performance_rating": round(random.uniform(3.5, 5.0), 1),
            "active_contracts": [fake.bothify("CN-2026-##")]
        })
    save_json(suppliers, "supplier_network")

    # 8) Route-Intelligence
    routes = []
    for i in range(15):
        r_id = f"PATH_{fake.bothify('???_???_##')}"
        pools["PATH"].append(r_id)
        routes.append({
            "_id": r_id,
            "origin": fake.city(),
            "destination": fake.city(),
            "distance_km": random.randint(300, 1500),
            "toll_details": [{"toll_id": fake.bothify("TOLL_M#_##"), "location": fake.city(), "cost": random.randint(300, 1500)}],
            "current_weather": {"forecast": random.choice(["Clear", "Heavy Rain", "Fog"]), "visibility_km": round(random.uniform(0.5, 10.0), 1), "last_updated": str(fake.date_time_this_month())},
            "traffic_history": {"congestion_level": random.choice(["Low", "Medium", "High"]), "avg_speed_kph": random.randint(40, 90), "bottleneck_points": [fake.street_name()]}
        })
    save_json(routes, "route_intelligence")

# ==========================================
# PHASE 2: MASTER ASSETS
# ==========================================
def gen_phase_2():
    # 2) Client-Portals
    clients = []
    for i in range(NUM_CUSTOMERS):
        c_id = f"CUST_{fake.bothify('?????_PK')}"
        pools["CUST"].append(c_id)
        clients.append({
            "_id": c_id,
            "profile": {"name": fake.company(), "contact_email": fake.company_email(), "tax_id": fake.bothify("NTN-######-#")},
            "billing_details": {"address": fake.address(), "payment_method": "Corporate Wire", "currency": "PKR"},
            "financial_standing": {"max_credit": 5000000.00, "current_balance": float(random.randint(10000, 4000000)), "status": "Good Standing"},
            "representative": {"name": fake.name(), "phone": fake.phone_number()}
        })
    save_json(clients, "client_portals")

    # 3) Driver-Performance
    drivers = []
    for i in range(NUM_DRIVERS):
        d_id = f"DRV_{random.randint(1000, 9999)}"
        pools["DRV"].append(d_id)
        drivers.append({
            "_id": d_id,
            "name": fake.name(),
            "license_details": {"license_id": fake.bothify("LNC_PK_####"), "class": "Heavy Commercial", "expiration_date": str(fake.date_between(start_date='+1y', end_date='+5y'))},
            "safety_score": random.randint(60, 100),
            "incident_history": [{"record_id": fake.bothify("SR_###"), "event": "Minor Scrape", "score_impact": -2, "date": str(fake.date_this_year())} for _ in range(random.randint(0, 2))],
            "customer_complaints": [{"complaint_id": fake.bothify("CMP_###"), "details": fake.sentence(), "timestamp": str(fake.date_this_year())} for _ in range(random.randint(0, 2))]
        })
    save_json(drivers, "driver_performance")

    # 4) Fleet-Assets
    assets = []
    for i in range(NUM_VEHICLES):
        v_id = f"VEH_{fake.bothify('???_##')}"
        pools["VEH"].append(v_id)
        assets.append({
            "_id": v_id,
            "specs": {"make_model": random.choice(["Volvo FH16", "Hino 500", "Isuzu NPR"]), "capacity_kg": 25000, "fuel_type": "Diesel"},
            "registration": {"plate_number": fake.bothify("???-####"), "tax_status": "Paid", "permit_expiry": str(fake.date_between(start_date='+1y', end_date='+3y'))},
            "current_health": {"engine_status": random.choice(["Optimal", "Warning"]), "tire_pressure_psi": random.randint(90, 110), "last_service_date": str(fake.date_this_year()), "diagnostics": {"battery": "Good", "brake_wear": f"{random.randint(5, 40)}%"}}
        })
    save_json(assets, "fleet_assets")

    # 12) Warehouse-Hubs
    warehouses = []
    for i in range(10):
        warehouses.append({
            "_id": f"WH_{fake.bothify('???_##')}",
            "province_id": f"PROV_{random.choice(pools['PROV'])}",
            "address": fake.address(),
            "total_capacity_sqft": random.randint(20000, 100000),
            "security_protocols": {"access_level": "Level 4 - Restricted", "biometric_enabled": True, "last_inspection": str(fake.date_this_year())},
            "bin_locations": [{"bin_id": fake.bothify("BIN_A#_##"), "aisle_number": f"A{random.randint(1,5)}", "type": random.choice(["Cold Storage", "Dry Storage"]), "occupied": random.choice([True, False])} for _ in range(5)],
            "loadi  ng_docks": [{"dock_number": j+1, "is_occupied": random.choice([True, False]), "current_vehicle": random.choice(pools["VEH"]) if random.choice([True, False]) else None} for j in range(3)]
        })
    save_json(warehouses, "warehouse_hubs")

# ==========================================
# PHASE 3: DEPENDENT TRANSACTIONS
# ==========================================
def gen_phase_3():
    # 9) Shipment-Ops
    shipments = []
    for i in range(NUM_SHIPMENTS):
        s_id = f"SHIP_{2026}_{random.randint(1000, 9999)}"
        pools["SHIP"].append(s_id)
        shipments.append({
            "_id": s_id,
            "customer_id": random.choice(pools["CUST"]),
            "assigned_driver": random.choice(pools["DRV"]),
            "assigned_vehicle": random.choice(pools["VEH"]),
            "path_id": random.choice(pools["PATH"]),
            "created_at": str(fake.date_time_this_month()),
            "customs_clearance": {"customs_id": fake.bothify("CUST_###"), "status": random.choice(["Cleared", "Pending"]), "declaration_value": random.randint(50000, 1000000)},
            "items": [{"item_id": fake.bothify("ITM_##"), "vendor_id": random.choice(pools["VND"]), "description": fake.word(), "qty": random.randint(10, 500)} for _ in range(random.randint(1, 4))],
            "status_history": [{"checkpoint": fake.city(), "update": random.choice(["Picked Up", "In-Transit", "Delayed"]), "timestamp": str(fake.date_time_this_month())}]
        })
    save_json(shipments, "shipment_ops")

# ==========================================
# PHASE 4: HIGH-VOLUME LOGS
# ==========================================
def gen_phase_4():
    # 11) Telemetry-Stream
    telemetry = []
    for _ in range(NUM_TELEMETRY):
        telemetry.append({
            "_id": f"TEL_{random.randint(1000000, 9999999)}",
            "vehicle_id": random.choice(pools["VEH"]),
            "gps": {"lat": float(fake.latitude()), "long": float(fake.longitude())},
            "metrics": {"speed_kph": round(random.uniform(0, 100), 1), "fuel_level_percent": random.randint(10, 100), "engine_temp_c": random.randint(80, 105)},
            "timestamp": str(fake.date_time_this_month())
        })
    save_json(telemetry, "telemetry_stream")

    # 6) Maintenance-History
    maintenance = []
    for i in range(NUM_MAINTENANCE):
        maintenance.append({
            "_id": f"MAINT_2026_{random.randint(100, 999)}",
            "vehicle_id": random.choice(pools["VEH"]),
            "service_type": random.choice(["Scheduled", "Emergency"]),
            "repair_details": {"description": fake.sentence(), "parts_replaced": [fake.word(), fake.word()], "mechanic_id": fake.bothify("MECH_###")},
            "financials": {"repair_cost": float(random.randint(2000, 50000)), "currency": "PKR", "invoice_ref": fake.bothify("INV_SER_###")},
            "date": str(fake.date_this_year())
        })
    save_json(maintenance, "maintenance_history")

    # 5) Incident-Reports
    incidents = []
    for i in range(NUM_INCIDENTS):
        incidents.append({
            "_id": f"INC_2026_{random.randint(1000, 9999)}",
            "related_ids": {"driver_id": random.choice(pools["DRV"]), "vehicle_id": random.choice(pools["VEH"]), "shipment_id": random.choice(pools["SHIP"])},
            "incident_details": {"type": random.choice(["Collision", "Theft", "Breakdown"]), "severity": random.choice(["Low", "Medium", "High"]), "location": fake.address(), "timestamp": str(fake.date_time_this_month())},
            "investigation": {"investigation_id": fake.bothify("INV_###"), "details": fake.sentence(), "investigator_name": fake.name()},
            "insurance_claim": {"claim_id": fake.bothify("CLM_####"), "provider": "EFU General", "status": random.choice(["In-Progress", "Settled", "Denied"]), "damage_est_pkr": float(random.randint(10000, 2000000))}
        })
    save_json(incidents, "incident_reports")

    # 1) Audit-Logs
    audits = []
    for _ in range(500):
        audits.append({
            "_id": f"LOG_{random.randint(10000000, 99999999)}",
            "user_id": "USER_ADMIN_ABDULLAH",
            "action": random.choice(["UPDATE_SHIPMENT_STATUS", "DELETE_DOCUMENT", "CREATE_RECORD"]),
            "context": {"collection": "shipment_ops", "document_id": random.choice(pools["SHIP"]), "field": "status", "old_value": "Warehouse", "new_value": "In-Transit"},
            "ip_address": fake.ipv4(),
            "timestamp": str(fake.date_time_this_month())
        })
    save_json(audits, "audit_logs")

if __name__ == "__main__":
    print("Initializing Nexus DB Script...")
    gen_phase_1()
    gen_phase_2()
    gen_phase_3()
    gen_phase_4()
    print("\nComplete! 12 files created matching exact JSON prototypes.")