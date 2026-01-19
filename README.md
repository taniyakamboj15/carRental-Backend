# Car Rental System - Backend

**Author:** Taniya Kamboj
**Description:** A robust, high-performance backend system for managing car rentals, vehicle availability, and user bookings. Designed for local rental services and corporate fleets.

---

## 🏗️ Architecture & Tech Stack

This project is built using modern, scalable technologies to ensure performance and reliability.

*   **Framework:** **FastAPI** (High-performance, Async Python web framework).
*   **Database:** **PostgreSQL** with **SQLModel** (ORM).
*   **Authentication:**  **HttpOnly Cookies** (Secure, Stateless).
*   **Background Tasks:** **Celery** + **Redis** (For Emails, PDF Generation, Scheduled Cleanup).
*   **Migrations:** **Alembic** (Database schema version control).

### 🔄 Data Flow
1.  **Client Request**: User sends JSON request (e.g., Book a Car).
2.  **API Layer**: FastAPI validates input using **Pydantic Schemas**.
3.  **Auth Layer**: Dependency Injection checks `HttpOnly Cookie` for **JWT Token**.
4.  **Service Layer**: Business logic executes (e.g., Conflict Check, Payment Processing).
5.  **Data Layer**: SQLModel interacts with **PostgreSQL**.
6.  **Async Layer**: Heavy tasks (Emails) are pushed to **Redis Queue** -> Processed by **Celery Workers**.

---

## ✅ Requirement Fulfillment Matrix

Here is how each assigned feature was architected and implemented:

| Feature | Requirement | Implementation Details |
| :--- | :--- | :--- |
| **User Profiles & KYC** | Manage user data and verify identity. | • **User Model**: Stores `email`, `hashed_password`, `role`.<br>• **KYC Workflow**: Users submit `document_url` (Status: `SUBMITTED`).<br>• **Verification**: Admins use `PUT /users/{id}/kyc` to Approve/Reject (Status -> `VERIFIED`). |
| **Vehicle Listing & Availability** | List cars and track when they are free. | • **Vehicle Model**: Stores `make`, `model`, `rate`, `is_available`.<br>• **Availability Logic**: Dynamic check. A car is "Unavailable" if a confirmed booking acts on it during the requested dates. |
| **Booking Conflict Resolution** | Prevent double booking. | • **Service Logic**: `booking_service.check_availability()` runs a SQL Query checking for date overlaps: `(StartA <= EndB) and (EndA >= StartB)`.<br>• **Atomic Transaction**: DB locks ensure race conditions are handled. |
| **Payment Integration** | Process payments (Dummy). | • **Payment Service**: `process_payment()` simulates a gateway.<br>• **Flow**: Booking starts as `PENDING`. Payment success triggers status update to `CONFIRMED`.<br>• **Async Invoice**: Successful payment triggers a Celery task to generate a PDF invoice. |
| **Booking History & Cancellation** | View past trips and cancel rules. | • **History**: `GET /bookings` returns personal history for Users, or Global history for Admins.<br>• **Cancellation Policy**: enforced in `POST /cancel`.<br>• **Rule**: Users can only cancel if `start_date` is > 24 hours away. Admins can override. |

---

## 🚀 Key Features

### 1. Security First
*   **No LocalStorage Tokens**: Tokens are stored in secure, `HttpOnly` cookies to prevent XSS attacks.
*   **Password Hashing**: Uses `Bcrypt` for salt-and-hash storage.
*   **Role Based Access Control (RBAC)**: Distinct permissions for `Admin` vs `Customer`.

### 2. Reliability (Idempotency) 🛡️
*   **Prevent Double Booking/Charging**: API supports `Idempotency-Key` header.
*   **Mechanism**: If a user clicks "Pay" twice, the second request (with same Key) returns the *saved result* of the first one, protecting against duplicate charges.


### 3. Rate Limiting 🚦
*   **Protection**: Uses `SlowAPI` (based on Redis/Memory).
*   **Rules**:
    *   **Login/Signup**: Restricted to **5 requests/minute** per IP to prevent Brute Force attacks.
    *   **Global**: Scalable infrastructure to add limits to any route easily.

### 4. Background Jobs (Celery)
*   **Welcome Emails**: Sent asynchronously on Signup.
*   **Invoicing**: Generated in background after payment.
*   **Scheduled Cleanup**: Using **Celery Beat** to auto-expire unpaid bookings.

### 5. Permissions & Roles 👮‍♂️

*   **`is_superuser` (Technical Power) ⚡**
    *   This is the "System Admin". In the codebase, security checks (like `deps.get_current_active_superuser`) strictly check this flag.
    *   If `True`, the user has full access (Delete, Create, Edit).
*   **`role="admin"` (Business Label) 🏷️**
    *   This is a metadata label for the Frontend.
    *   Example: If `role == "admin"`, the UI shows the "Dashboard" button. Useful for future roles like "Manager" or "Support".

**Protected Routes (Where `is_superuser` is Checked):**
1.  **Vehicles Management** (`/api/v1/vehicles/`):
    *   `POST /`, `PUT /{id}`, `DELETE /{id}` -> **Admin Only** (Manage Fleet).
2.  **KYC Verification** (`/api/v1/users/{id}/kyc`):
    *   `PUT /` -> **Admin Only** (Approve/Reject Docs).
3.  **Bookings List** (`/api/v1/bookings/`):
    *   `GET /`: **Conditional**. If Admin -> View *ALL*. If User -> View *OWN*.

---

## 🛠️ Setup & Installation

**Prerequisites:** Python 3.11+, PostgreSQL, Redis.

1.  **Clone & Install Dependencies:**
    ```bash
    git clone <repo-url>
    cd carRental-Backend
    python -m venv venv
    .\venv\Scripts\activate
    pip install -r requirements.txt
    ```

2.  **Environment Setup:**
    Create a `.env` file:
    ```ini
    POSTGRES_SERVER=localhost
    POSTGRES_USER=postgres
    POSTGRES_PASSWORD=yourpassword
    POSTGRES_DB=car_rental
    SECRET_KEY=your_secret_key
    ```

3.  **Run Migrations:**
    ```bash
    alembic upgrade head
    ```

4.  **Start Services:**
    *   **API Server:** `uvicorn app.main:app --reload`
    *   **Celery Worker:** `celery -A app.worker.celery_app worker --loglevel=info -P solo`
    *   **Celery Beat:** `celery -A app.worker.celery_app beat --loglevel=info`
    *   **Flower:** `celery -A app.worker.celery_app flower --loglevel=info`
5.  **Access Documentation:**
    *   Swagger UI: `http://localhost:8000/docs`

---
*Generated By Taniya Kamboj - Car Rental System Backend Project*
