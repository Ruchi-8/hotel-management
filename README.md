# HotelPro — Hotel Management Solution

**HotelPro** is a comprehensive, production-ready hotel management platform featuring:
1. **Streamlit Deployment Suite (`app.py` / `streamlit_app.py`)**: Deployable to **Streamlit Community Cloud** (share.streamlit.io) in 2 minutes with zero-configuration embedded SQLite database, real-time analytics, room inventory management, booking engine with date-conflict prevention, guest directory, billing & invoice generator, and CSV exports.
2. **MERN Stack (`client/` & `server/`)**: Full React + Express + Node.js + MongoDB architecture with JWT Bearer authentication, Bootstrap 5 UI, and RESTful API endpoints.

---

## 🚀 Quick Start 1: Run with Streamlit (Recommended for Deployment)

### 1. Launch Locally
In your terminal, run:
```bash
streamlit run app.py
```
Or:
```bash
python -m streamlit run app.py
```
Open your browser at **http://localhost:8501**.

### 2. Default Login Credentials
- **Administrator:** `admin@hotelpro.com` | Password: `admin123`
- **Front Desk Staff:** `staff@hotelpro.com` | Password: `staff123`
- *(Or click "Create Account" on the login screen to register a new administrator).*

---

## 🌐 Deploy to Streamlit Community Cloud (Free Hosting)

You can deploy HotelPro directly to **[Streamlit Community Cloud](https://share.streamlit.io)** with a public shareable URL:

1. **Push your repository to GitHub**:
   ```bash
   git init
   git add .
   git commit -m "Deploy HotelPro on Streamlit"
   git branch -M main
   git remote add origin https://github.com/<your-username>/hotelpro.git
   git push -u origin main
   ```
2. **Go to [share.streamlit.io](https://share.streamlit.io)** and sign in with GitHub.
3. Click **New app**.
4. Select your repository: `<your-username>/hotelpro`.
5. Main file path: `app.py` (or `streamlit_app.py`).
6. Click **Deploy!**

---

## 💻 Quick Start 2: Run MERN Stack (React + Express)

All dependencies have already been installed for root, client, and server.

1. Navigate to the `HotelPro` folder:
   ```bash
   cd HotelPro
   ```
2. Start MongoDB locally (or set your MongoDB Atlas connection string in `server/.env`).
3. Launch both the backend and frontend simultaneously:
   ```bash
   npm run dev
   ```
   *(On Windows PowerShell, use `npm.cmd run dev` if script execution is restricted).*
4. Access:
   - **Frontend (React + Vite):** [http://localhost:5173](http://localhost:5173)
   - **Backend API (Express):** [http://localhost:5000/api/health](http://localhost:5000/api/health)

---

## ✨ System Features & Epics Breakdown

| Epic | Features Covered |
| :--- | :--- |
| **Epic 1: Security & Auth** | Multi-role user authentication, bcrypt password hashing, session state persistence. |
| **Epic 2: Operations Dashboard** | Real-time KPIs, occupancy donut charts, revenue by room type, recent reservations. |
| **Epic 3: Room Inventory** | Room numbering, room categories (Single, Double, Deluxe, Suite), pricing, status badges, active booking protection on room deletion. |
| **Epic 4: Bookings & Reservations** | Live date conflict / double-booking prevention, night & price calculator, reservation status tracking (Confirmed, Checked-in, Checked-out, Cancelled). |
| **Epic 5: Guest Directory** | Lifetime spending records, booking count, contact info, guest stay history drawer. |
| **Epic 6: Billing & Data Export** | Itemized invoice generator with 12% GST calculation, print/text invoice download, CSV exports for rooms, bookings, and guests. |
