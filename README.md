
---

# 🌍 Country Currency & Exchange API

A **FastAPI + MySQL (Async SQLAlchemy)** backend that fetches global country data and currency exchange rates, computes GDP estimates, and exposes a RESTful API for data access and management.

This project is built for **HNG Stage 2 Backend Task**.

---

## ⚙️ Features Overview

✅ Fetches and caches data from external APIs
✅ Computes estimated GDP dynamically
✅ Supports filters, sorting, and CRUD operations
✅ Generates an image summary (`cache/summary.png`)
✅ Handles API failures gracefully
✅ Asynchronous database (SQLAlchemy + aiomysql)

---

## 🧩 Functional Requirements

### Data Sources

| Source                | Description                                                                                                                                                                      |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Countries API**     | [https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies](https://restcountries.com/v2/all?fields=name,capital,region,population,flag,currencies) |
| **Exchange Rate API** | [https://open.er-api.com/v6/latest/USD](https://open.er-api.com/v6/latest/USD)                                                                                                   |

---

## 🧠 Logic Summary

* Each country’s **first currency** code (e.g. `NGN`, `USD`, `EUR`) is used.

* The **exchange rate** is looked up from the exchange API.

* The field `estimated_gdp` is computed as:

  [
  \text{estimated_gdp} = \frac{\text{population} \times random(1000–2000)}{\text{exchange_rate}}
  ]

* Countries with no currency or missing rate:

  * `currency_code = null`
  * `exchange_rate = null`
  * `estimated_gdp = 0`

* Existing countries (matched by name, case-insensitive) are updated.

* New countries are inserted.

* Each successful refresh updates a global `last_refreshed_at` timestamp.

---

## 🏗️ Project Structure

```
app/
│
├── main.py                     # FastAPI entrypoint
├── config/
│   └── Config.py           # Async MySQL engine setup
├── models/
│   └── Country.py              # SQLAlchemy model
├── routes/
│   └── country.py              # API endpoints
├── utils/
│   ├── image_generator.py      # Creates summary.png
│   └── helpers.py              # Utility functions
├── cache/
│   └── summary.png             # Generated image
└── requirements.txt
```

---

## ⚡ Setup & Installation

### 1️⃣ Clone Repository

```bash
git clone https://github.com/RashidSWE/hng-stage2-backend.git
cd hng-stage2-backend
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate

```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment

Create `.env` in the root:

```
DATABASE_URL=mysql+aiomysql://<username>:<password>@<host>/<database>
```

Example (local):

```
DATABASE_URL=mysql+aiomysql://root:password@localhost/country_db
```

### 5️⃣ Run Migrations (if applicable)

```bash
alembic upgrade head
```

### 6️⃣ Start the Server

```bash
uvicorn app.main:app --reload
```

Server runs at:
👉 [http://127.0.0.1:8000](http://127.0.0.1:8000)

---

## 🌐 API Endpoints

| Endpoint             | Method     | Description                                                            |
| -------------------- | ---------- | ---------------------------------------------------------------------- |
| `/countries/refresh` | **POST**   | Fetch all countries + exchange rates, compute GDP, and store/update DB |
| `/countries`         | **GET**    | Retrieve all cached countries (supports filters/sorting)               |
| `/countries/{name}`  | **GET**    | Get one country by name                                                |
| `/countries/{name}`  | **DELETE** | Delete a specific country                                              |
| `/status`            | **GET**    | Show total cached countries and last refresh timestamp                 |
| `/countries/image`   | **GET**    | Serve generated summary image (`cache/summary.png`)                    |

---

## 🔍 Query Parameters

**GET /countries**

| Parameter  | Example          | Description             |
| ---------- | ---------------- | ----------------------- |
| `region`   | `?region=Africa` | Filter by region        |
| `currency` | `?currency=NGN`  | Filter by currency code |
| `sort`     | `?sort=gdp_desc` | Sort by GDP descending  |
| `sort`     | `?sort=gdp_asc`  | Sort by GDP ascending   |

---

## 🧮 Example API Responses

### ✅ GET /countries?region=Africa

```json
[
  {
    "id": 1,
    "name": "Nigeria",
    "capital": "Abuja",
    "region": "Africa",
    "population": 206139589,
    "currency_code": "NGN",
    "exchange_rate": 1600.23,
    "estimated_gdp": 25767448125.2,
    "flag_url": "https://flagcdn.com/ng.svg",
    "last_refreshed_at": "2025-10-22T18:00:00Z"
  },
  {
    "id": 2,
    "name": "Ghana",
    "capital": "Accra",
    "region": "Africa",
    "population": 31072940,
    "currency_code": "GHS",
    "exchange_rate": 15.34,
    "estimated_gdp": 3029834520.6,
    "flag_url": "https://flagcdn.com/gh.svg",
    "last_refreshed_at": "2025-10-22T18:00:00Z"
  }
]
```

---

### ✅ GET /status

```json
{
  "total_countries": 250,
  "last_refreshed_at": "2025-10-22T18:00:00Z"
}
```

---

### ✅ GET /countries/image

Returns the image file `cache/summary.png`
If missing:

```json
{
  "error": "Summary image not found"
}
```

---

## ⚠️ Error Handling

| Scenario              | Status | Response Example                                                                                            |
| --------------------- | ------ | ----------------------------------------------------------------------------------------------------------- |
| Validation error      | 400    | `{ "error": "Validation failed", "details": { "currency_code": "is required" } }`                           |
| Country not found     | 404    | `{ "error": "Country not found" }`                                                                          |
| External API down     | 503    | `{ "error": "External data source unavailable", "details": "Could not fetch data from restcountries.com" }` |
| Internal server error | 500    | `{ "error": "Internal server error" }`                                                                      |

---

## 🖼️ Summary Image

On each successful `/countries/refresh`:

* Generates an image at `cache/summary.png`
* Displays:

  * Total number of countries
  * Top 5 countries by estimated GDP
  * Last refresh timestamp

---

## 🧠 Implementation Notes

* Use `httpx.AsyncClient` for external API calls
* Use `async with AsyncSession(engine)` for DB operations
* Use `matplotlib` or `PIL` for image generation
* All routes must return JSON except `/countries/image`
* Ensure `/countries/image` route is **above** `/countries/{name}` to prevent conflicts

---

## 🧪 Testing Examples

### Refresh Data

```bash
curl -X POST http://127.0.0.1:8000/countries/refresh
```

### Get Summary Image

```bash
curl -O http://127.0.0.1:8000/countries/image
```

### Delete Country

```bash
curl -X DELETE http://127.0.0.1:8000/countries/Kenya
```

---

## 🧱 Tech Stack

| Component        | Tool                |
| ---------------- | ------------------- |
| Language         | Python 3.10+        |
| Framework        | FastAPI             |
| ORM              | SQLAlchemy (Async)  |
| Database         | MySQL               |
| HTTP Client      | httpx               |
| Image Generation | Matplotlib / Pillow |
| Runtime          | Uvicorn             |

---

## 📦 Deployment

### On Railway or Render

1. Add environment variable:

   ```
   DATABASE_URL=mysql+aiomysql://user:password@host/db
   ```
2. Deploy with command:

   ```
   uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

---

## 🧑‍💻 Author

**Abdirashid Rashid**
Backend Developer — HNG Internship 13
📧 Email: *[[rashidsamadina@gmail.com](mailto:rashidsamadina@gmail.com)]*

---