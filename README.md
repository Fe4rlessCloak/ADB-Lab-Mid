#  Nexus Logistics: Advanced NoSQL Engine

##  Project Overview
**Nexus Logistics** is a specialized database system designed to address the challenges of real-time supply chain management. By leveraging a document-oriented architecture with MongoDB, the system replaces traditional relational bottlenecks with a denormalized, query-optimized model.

### Key Focus Areas:
* **Shipment Tracking:** Monitoring high-value shipments in real-time.
* **Driver Performance:** Tracking metrics and efficiency.
* **Fleet Health:** Maintaining maintenance schedules and vehicle status.
* **Concurrency:** Supporting high-traffic, high-concurrency environments.

*Developed as part of the Advanced Databases curriculum at COMSATS University Islamabad.*

---

##  Architectural Design
The database employs advanced NoSQL modeling techniques to ensure data locality and low-latency access:

###  Embedded Data Model Pattern
* Consolidates **43 relational entities** into just **12 collections**.
* Eliminates expensive multi-table joins.
* Significantly improves read performance through data locality.


---

##  Execution Plan Analysis
Performance improvements were validated using MongoDB’s `explain()` utility:

| Stage | Documents Examined | Method |
| :--- | :--- | :--- |
| **Pre-Optimization** | 953 | `COLLSCAN` (Collection Scan) |
| **Post-Optimization** | 30 | `IXSCAN` (Index Scan) |

###  Results
* **96.8% reduction** in documents scanned.
* Achieves **$O(\log n)$** scalability.
* Highly efficient for datasets exceeding **1,000,000+ records**.

---

##  Deployment & Environment
The system runs in a containerized environment to ensure consistency across development and production.

###  Infrastructure Requirements
* **OS:** Any
* **Container Runtime:** Docker CE
* **Database:** MongoDB 

###  Getting Started
1. **Start the Container**
   ```bash
   docker compose up -d
  
2. **Access MongoDB Shell**
    ```bash
     docker exec -it nexus-mongodb mongosh -u admin -p password --authenticationDatabase admin
Note: The Docker Compose file is specifically built for the Fedora distribution of Linux. You may need to change the volume mapping section to better suit your Operating System.
### Technical Stack

    Language: Python 3.10 (Data generation using Faker)

    Database: MongoDB 5.0

    Modeling Tool: PlantUML

    Environment: Docker
   
