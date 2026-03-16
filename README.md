# AI Data Insight Copilot

End-to-end analytics platform with Airflow ETL, DuckDB data mart, Superset dashboards, and an LLM-powered data copilot.

## Table of Contents

- [1. Project Overview](#1-project-overview)
- [2. Architecture](#2-architecture)
- [3. Project Structure](#3-project-structure)
- [4. Airflow Pipeline](#4-airflow-pipeline)
- [5. Data Mart Design](#5-data-mart-design)
- [6. Superset Dashboard](#6-superset-dashboard)
- [7. AI Data Copilot](#7-ai-data-copilot)
- [8. Run the Project](#8-run-the-project)

## 1. Project Overview

AI Data Insight Copilot is an end-to-end analytics platform that integrates a data pipeline, analytical data mart, BI dashboards, and an AI-powered data copilot.

The system generates synthetic e-commerce data and processes it through an automated Airflow pipeline. The pipeline performs synthetic data generation, data quality validation, and builds a DuckDB-based analytical data mart optimized for analytical queries.

The data mart is used by two main components:

- **Superset BI Dashboard** for KPI monitoring and exploratory analysis
- **AI Data Copilot** that enables natural-language analytics using LLM-generated SQL queries

Through this architecture, users can explore data both through traditional BI dashboards and through conversational analytics powered by large language models.

This project demonstrates a practical architecture for integrating data engineering pipelines, BI dashboards, and LLM-powered analytics in a unified analytics platform.

### Key Components

- **Airflow Pipeline**  
  Automates synthetic data generation, data quality validation, and data mart construction.

- **DuckDB Data Mart**  
  Stores analytical tables and KPI views optimized for BI queries.

- **Superset Dashboard**  
  Provides interactive KPI visualizations such as revenue trends, order counts, and category performance.

- **AI Data Copilot**  
  Allows users to query data using natural language, where an LLM converts questions into SQL queries executed on DuckDB.

## 2. Architecture

The system is designed as an end-to-end analytics platform that integrates a data pipeline, analytical data mart, BI dashboards, and an AI-powered data copilot.

Synthetic e-commerce data is generated and processed through an automated Airflow pipeline. After passing data quality validation, the data is stored in a DuckDB-based analytical data mart.  
The data mart is then used by both a BI dashboard (Superset) and an AI-driven natural language analytics interface (AI Data Copilot).

### System Architecture
```
            +-------------------------------+
            |   Synthetic Data Generator    |
            | generate_synthetic_data.py    |
            +---------------+---------------+
                            |
                            v
            +-------------------------------+
            |          Airflow DAG          |
            |      daily_data_pipeline      |
            |                               |
            | 1. generate_synthetic_data    |
            | 2. data_quality_check         |
            | 3. build_duckdb               |
            +---------------+---------------+
                            |
                            v
            +-------------------------------+
            |         DuckDB Data Mart      |
            |                               |
            | tables                        |
            |  - users                      |
            |  - products                   |
            |  - events                     |
            |  - orders                     |
            |                               |
            | views                         |
            |  - mart_daily_revenue         |
            |  - mart_funnel_daily          |
            +---------------+---------------+
                            |
           +----------------+----------------+
           |                                 |
           v                                 v

 +-----------------------+       +---------------------------+
 |    Superset Dashboard |       |       AI Data Copilot     |
 |                       |       |                           |
 | KPI Visualization     |       | Natural Language Query    |
 |                       |       |                           |
 | • Revenue Trend       |       | Planner → SQL Agent       |
 | • Total Orders        |       | → DuckDB Query            |
 | • Unique Users        |       | → Analyst → Insights      |
 | • Category Revenue    |       |                           |
 +-----------------------+       +---------------------------+
 ```

### Data Flow

1. **Synthetic Data Generation**  
   Test data simulating e-commerce user activity is generated.

2. **Airflow Pipeline**  
   Airflow orchestrates the pipeline consisting of:
   - synthetic data generation
   - data quality validation
   - DuckDB data mart construction

3. **DuckDB Data Mart**  
   Analytical tables and KPI views are created to support BI queries.

4. **Superset Dashboard**  
   Superset visualizes key business metrics such as revenue trends and order statistics.

5. **AI Data Copilot**  
   Users can query data using natural language.  
   The LLM converts user questions into SQL queries that are executed against DuckDB.

## 3. Project Structure
```
ai-data-insight-copilot/
│
├── Infrastructure & Config
│ ├── .env # Environment variables (e.g., API keys)
│ ├── .env.example # Example environment configuration
│ ├── .gitignore # Git ignore rules
│ ├── docker-compose.airflow.yml # Docker Compose configuration for Airflow
│ └── requirements.txt # Python dependency list
│
├── airflow/ (Workflow Orchestration)
│ ├── dags/
│ │ └── daily_data_pipeline.py # Airflow DAG (generate → quality check → mart build)
│ ├── logs/ # Airflow execution logs
│ └── plugins/ # Custom Airflow plugins (currently unused)
│
├── src/copilot/ (AI Data Copilot Core)
│ ├── agents/
│ │ ├── planner.py # Analyze user query and identify intent/metrics
│ │ ├── sql_agent.py # Convert natural language into SQL
│ │ ├── analyst.py # Summarize query results in natural language
│ │ ├── insight_engine.py # Generate structured insights from query results
│ │ ├── sql_normalizer.py # Normalize LLM-generated SQL to DuckDB syntax
│ │ └── validator.py # Validate SQL safety and allowed tables
│ │
│ ├── pipeline/
│ │ └── orchestrator.py # Orchestrates planner → retrieval → SQL → analysis
│ │
│ ├── retrieval/
│ │ └── retriever.py # Retrieve metadata and examples (RAG-style context)
│ │
│ ├── datastore/
│ │ └── duckdb_client.py # DuckDB connection and query execution
│ │
│ ├── context/
│ │ └── schema_registry.py # Schema metadata management for prompt context
│ │
│ ├── evaluation/
│ │ └── evaluator.py # Evaluate query results and store evaluation logs
│ │
│ ├── interfaces/
│ │ ├── api/
│ │ │ ├── app.py # FastAPI server entry point
│ │ │ └── schemas.py # API request/response schemas (Pydantic)
│ │ │
│ │ └── web/
│ │ └── streamlit_app.py # Streamlit-based Data Copilot interface
│ │
│ └── main.py # CLI entry point for the copilot
│
├── data/ (Data Storage)
│ ├── raw/ # Raw CSV data (users, products, events, orders)
│ └── processed/
│ └── insight.duckdb # DuckDB analytical database (Data Mart)
│
├── metadata/ (Business Knowledge)
│ ├── business/
│ │ ├── kpi_definitions.json # KPI definitions and business metrics
│ │ └── sql_examples.json # Few-shot SQL examples for query generation
│ │
│ └── schema/
│ └── tables.json # Table and column descriptions
│
├── scripts/ (ETL & Utilities)
│ ├── build_duckdb.py # Build DuckDB mart from raw CSV data
│ ├── data_quality_check.py # Data validation checks
│ ├── generate_synthetic_data.py # Synthetic dataset generator
│ ├── run.ps1 # Run copilot via CLI
│ ├── run_api.ps1 # Run FastAPI server
│ └── run_ui.ps1 # Run Streamlit UI
│
└── outputs/
└── eval_results/ # Evaluation result logs (JSON)
```

This structure separates infrastructure, data pipelines, analytics storage, and the AI copilot components to clearly reflect the architecture of the analytics platform.

## 4. Airflow Pipeline

The project uses **Apache Airflow** to orchestrate the end-to-end ETL workflow for the analytics platform.

The DAG automates the following steps:

1. **generate_synthetic_data**  
   Generates synthetic e-commerce datasets including users, products, events, and orders.

2. **data_quality_check**  
   Validates the generated raw data before further processing.  
   Example checks include:
   - null value validation
   - valid event type validation
   - positive order amount validation

3. **build_duckdb**  
   Loads raw CSV data into DuckDB and builds the analytical data mart, including KPI-oriented views such as:
   - `mart_daily_revenue`
   - `mart_funnel_daily`

### DAG Flow
```
generate_synthetic_data
↓
data_quality_check
↓
build_duckdb
```

### DAG Description

- **DAG ID**: `daily_data_pipeline`
- **Schedule**: `@daily`
- **Executor**: `LocalExecutor`
- **Storage**: DuckDB-based analytical data mart

### Pipeline Purpose

This workflow demonstrates how a modern analytics platform can automate:

- synthetic data generation
- raw data validation
- analytical mart construction

By integrating Airflow with DuckDB, the project provides a lightweight but practical example of a batch-oriented analytics pipeline.

### DAG Execution Example

![Airflow DAG](docs/images/AirflowDag.png)

## 5. Data Mart Design

The project uses **DuckDB** as an analytical data mart to support both BI dashboards and natural-language analytics.

The data mart is built from raw synthetic CSV files generated through the ETL pipeline and is stored as:

```text
data/processed/insight.duckdb
```

---

### Raw Tables

The following raw tables are created in DuckDB:

- `users`
- `products`
- `events`
- `orders`

These tables preserve the original event and transaction-level data required for detailed analysis.

---

#### users

Stores user-level profile and signup information.

| Column | Type | Description |
|------|------|-------------|
| user_id | BIGINT | Unique user identifier |
| country | VARCHAR | User country |
| device_type | VARCHAR | Device type used by the user |
| signup_at | TIMESTAMP | User signup timestamp |

---

#### products

Stores product-level metadata.

| Column | Type | Description |
|------|------|-------------|
| product_id | BIGINT | Unique product identifier |
| product_name | VARCHAR | Product name |
| category | VARCHAR | Product category |
| price | BIGINT | Product price |

---

#### events

Stores user activity events.

| Column | Type | Description |
|------|------|-------------|
| event_id | BIGINT | Unique event identifier |
| user_id | BIGINT | User identifier |
| product_id | BIGINT | Product identifier |
| event_type | VARCHAR | Event type (`view`, `click`, `add_to_cart`, `purchase`) |
| event_time | TIMESTAMP | Event timestamp |

---

#### orders

Stores completed purchase transactions.

| Column | Type | Description |
|------|------|-------------|
| order_id | BIGINT | Unique order identifier |
| user_id | BIGINT | User identifier |
| product_id | BIGINT | Product identifier |
| order_time | TIMESTAMP | Order timestamp |
| amount | BIGINT | Order amount |
| category | VARCHAR | Product category |

---

### Analytical Views

To optimize BI queries and KPI analysis, the project creates aggregated analytical views on top of the raw transaction data.

---

#### mart_daily_revenue

Provides daily revenue and order count by category.

| Column | Type | Description |
|------|------|-------------|
| order_date | DATE | Aggregated order date |
| category | VARCHAR | Product category |
| order_count | BIGINT | Number of orders |
| revenue | INTEGER | Total revenue |

Used for:

- Daily revenue trend analysis
- Order count monitoring
- Category revenue comparison

---

#### mart_funnel_daily

Provides daily funnel metrics across the user journey.

| Column | Type | Description |
|------|------|-------------|
| event_date | DATE | Aggregated event date |
| views | BIGINT | Number of view events |
| clicks | BIGINT | Number of click events |
| add_to_carts | BIGINT | Number of add-to-cart events |
| purchases | BIGINT | Number of purchase events |

Used for:

- Conversion funnel analysis
- User behavior trend monitoring
- Event-based KPI tracking

---

### Design Rationale

The data mart follows a layered analytical design:

**Raw Layer**

Stores event-level and transaction-level source data.

**Mart Layer**

Builds aggregated analytical views optimized for KPI queries and dashboards.

**Consumption Layer**

Supports:

- **Superset BI dashboards**
- **AI Data Copilot (LLM-based analytics)**

This design keeps the platform lightweight while demonstrating a practical modern analytics architecture.

## 6. Superset Dashboard

Apache Superset is used as the BI visualization layer for exploring business KPIs generated from the DuckDB data mart.

The dashboard connects directly to:

```text
data/processed/insight.duckdb
```

and visualizes aggregated analytical views created during the Airflow data pipeline.

---

## Dashboard Purpose

The Superset dashboard provides an interactive analytics interface for monitoring business performance and exploring data trends.

It allows users to:

- monitor daily revenue trends
- analyze product category performance
- track order volume over time
- explore key business KPIs

The dashboard serves as the **BI layer on top of the DuckDB analytical data mart**.

---

## Data Sources

The dashboard is built on the following analytical view:

| Dataset | Description |
|---|---|
| `mart_daily_revenue` | Daily revenue and order metrics by category |

This view is generated by the **Airflow pipeline** during the `build_duckdb` step.

---

## Example Visualizations

The dashboard typically includes the following charts.

---

### Revenue Trend

Displays revenue trends over time.

Metrics:

- `SUM(revenue)`
- `SUM(order_count)`

Purpose:

- monitor business growth
- detect revenue fluctuations
- analyze seasonal patterns

---

### Category Revenue

Shows revenue distribution by product category.

Metrics:

- `SUM(revenue)` grouped by `category`

Purpose:

- identify top performing product categories
- analyze product demand distribution

---

### Order Volume

Displays total order volume across time.

Metrics:

- `SUM(order_count)`

Purpose:

- monitor order activity
- track business traffic changes

---

## Dashboard Data Flow

The dashboard is part of the full analytics pipeline.
```
Synthetic Data Generator
↓
Airflow DAG
(generate → quality check → build mart)
↓
DuckDB Data Mart
↓
Superset Dataset
↓
Superset Dashboard
```

---

## Running Superset

Superset runs inside a Docker container.

Start Superset with:
```bash
docker compose up
```

Then access the dashboard at: http://localhost:8088

After logging in, connect the DuckDB database and open the dashboard to explore the KPI visualizations.

## 7. AI Data Copilot

AI Data Copilot is a lightweight **LLM-powered analytics assistant** that allows users to query business data using natural language.

Instead of writing SQL manually, users can ask questions such as:

- What was the total revenue yesterday?
- Show revenue by category
- How many orders were created last week?

The system automatically converts natural language into SQL queries, executes them on DuckDB, and returns structured analytical insights.

---

### System Components

The AI Data Copilot is composed of modular agents that collaborate to execute the analysis workflow.

| Component | Role |
|---|---|
| Planner | Interprets the user question and determines the analysis plan |
| SQL Agent | Generates SQL queries using schema context |
| DuckDB Client | Executes SQL queries against the DuckDB data mart |
| Analyst | Interprets query results |
| Insight Engine | Generates business insights from the data |
| Validator | Validates generated SQL queries |

These components are orchestrated by a central controller.

---

### Query Execution Flow
```
User Question
↓
Planner
↓
SQL Agent
↓
DuckDB Query
↓
Analyst
↓
Insight Engine
↓
Natural Language Insight
```

---

### Example Query

User question:

```
What is the revenue by category today?
```

Generated SQL:

```sql
SELECT
  category,
  SUM(revenue) AS total_revenue
FROM mart_daily_revenue
GROUP BY category
```

The system executes the query and returns both:

 - structured result table

 - natural language insight

---

### Schema Context

To improve SQL generation accuracy, the AI agent uses schema metadata stored in:

``` metadata/schema/tables.json ```

This metadata includes:

- table descriptions

- column definitions

- business meanings

Providing schema context enables more accurate SQL generation.

---
### Business Knowledge Context

Business KPI definitions are stored in:

``` metadata/business/kpi_definitions.json ```

This file defines important metrics such as:

- revenue

- order_count

- category revenue

This helps the LLM generate queries aligned with business semantics.

### API Interface

The AI Data Copilot exposes a REST API via FastAPI.

Example endpoint:

``` POST /query ```

### Example request:
```
{
  "question": "Show revenue by category"
}
```

Example response:
```
{
  "sql": "SELECT category, SUM(revenue) FROM mart_daily_revenue GROUP BY category",
  "result": "...",
  "insight": "Category A generated the highest revenue."
}
```
The response includes:

- generated SQL query

- query execution result

- summarized business insight

---

### Web Interface

A Streamlit UI is provided for interactive exploration.

Start the UI:

```
./scripts/run_ui.ps1
```

Then open:

```
http://localhost:8501
```

Users can ask questions and receive:

- generated SQL queries
- query results
- AI-generated insights
---

### Design Goals

The AI Data Copilot demonstrates:

- natural language analytics
- LLM-driven SQL generation
- schema-aware query generation
- modular agent architecture
- integration with a modern data pipeline

It serves as an intelligent analytical layer on top of the DuckDB data mart.

---

## 8. Run the Project

This section explains how to run the full **AI Data Insight Copilot** project locally.

The system consists of:

- Airflow data pipeline
- DuckDB analytical data mart
- Superset BI dashboard
- FastAPI backend
- Streamlit AI Copilot interface

---

### 1. Install Dependencies

First install the required Python packages.

```bash
pip install -r requirements.txt
```

---

### 2. Generate Synthetic Data

Create sample business data used for analytics.

```
python scripts/generate_synthetic_data.py
```

This generates CSV files in:

```
data/raw/
```

Example files:
- users.csv
- products.csv
- events.csv
- orders.csv

---

### 3. Build DuckDB Data Mart

Build the analytical database.

```
python scripts/build_duckdb.py
```

This creates the DuckDB database:

```
data/processed/insight.duckdb
```

The script also generates analytical views:
- mart_daily_revenue
- mart_funnel_daily

---

### 4. Run Airflow Pipeline

Start the Airflow orchestration environment.

```
docker compose -f docker-compose.airflow.yml up
```

Open Airflow UI:

```
http://localhost:8081
```

Enable and run the DAG:

```
daily_data_pipeline
```

Pipeline tasks:
1. generate_synthetic_data
2. data_quality_check
3. build_duckdb

---

### 5. Run Superset Dashboard

Start Superset for BI visualization.

```
docker compose up
```

Open Superset:

```
http://localhost:8088
```

Connect the DuckDB dataset and open the dashboard.

---

### 6. Run FastAPI Server

Start the backend API for the AI Copilot.

```
./scripts/run_api.ps1
```

API endpoint:

```
http://localhost:8000
```

---

### 7. Run AI Data Copilot UI

Launch the Streamlit interface.

```
./scripts/run_ui.ps1
```

Open the UI:

```
http://localhost:8501
```

You can now ask questions such as:

- Show revenue by category
- What is the daily revenue trend?
- How many orders were created yesterday?

The system will generate SQL queries, execute them on DuckDB, and return analytical insights.

---
### System Overview

```
Airflow Pipeline
      ↓
DuckDB Data Mart
      ↓
Superset Dashboard
      ↓
AI Data Copilot (FastAPI + Streamlit)
```

The pipeline automatically generates data, validates it, builds the analytical mart, and exposes it to both BI dashboards and the AI analytics assistant.
