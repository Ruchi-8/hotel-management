"""
HotelPro Database Module
Supports SQLite by default for zero-config Streamlit Cloud deployment,
with optional MongoDB Atlas synchronization.
"""

import sqlite3
import datetime
import os
import bcrypt

DB_PATH = os.path.join(os.path.dirname(__file__), "hotelpro.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))
    except Exception:
        return False


def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'Administrator',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS rooms (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT NOT NULL UNIQUE,
        type TEXT NOT NULL DEFAULT 'Double',
        price REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Available',
        amenities TEXT DEFAULT 'Wi-Fi, AC, Smart TV',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        guest_name TEXT NOT NULL,
        guest_email TEXT NOT NULL,
        guest_phone TEXT DEFAULT '',
        room_id INTEGER NOT NULL,
        check_in DATE NOT NULL,
        check_out DATE NOT NULL,
        guests INTEGER NOT NULL DEFAULT 1,
        status TEXT NOT NULL DEFAULT 'Confirmed',
        payment_status TEXT NOT NULL DEFAULT 'Pending',
        total_amount REAL NOT NULL DEFAULT 0.0,
        notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (room_id) REFERENCES rooms(id) ON DELETE RESTRICT
    );
    """)

    conn.commit()

    # Seed default Admin user if none exists
    cursor.execute("SELECT COUNT(*) as count FROM users")
    if cursor.fetchone()["count"] == 0:
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, ("Admin User", "admin@hotelpro.com", hash_password("admin123"), "Administrator"))
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, ("Front Desk Staff", "staff@hotelpro.com", hash_password("staff123"), "Front Desk"))
        conn.commit()

    # Seed sample rooms if none exists
    cursor.execute("SELECT COUNT(*) as count FROM rooms")
    if cursor.fetchone()["count"] == 0:
        sample_rooms = [
            ("101", "Single", 1800, "Available", "Wi-Fi, AC, TV, Workspace"),
            ("102", "Single", 1800, "Occupied", "Wi-Fi, AC, TV, Coffee Maker"),
            ("201", "Double", 2800, "Available", "Wi-Fi, AC, King Bed, Mini Bar, Balcony"),
            ("202", "Double", 2800, "Occupied", "Wi-Fi, AC, Queen Bed, Garden View"),
            ("301", "Deluxe", 4500, "Available", "Wi-Fi, AC, King Bed, Jacuzzi, Ocean View"),
            ("302", "Deluxe", 4500, "Maintenance", "Wi-Fi, AC, King Bed, Panoramic View"),
            ("401", "Suite", 8000, "Available", "Wi-Fi, Penthouse Suite, Private Pool, Butler Service"),
            ("402", "Suite", 8000, "Available", "Wi-Fi, Presidential Suite, Lounge Area, Spa Bath"),
        ]
        cursor.executemany("""
            INSERT INTO rooms (number, type, price, status, amenities)
            VALUES (?, ?, ?, ?, ?)
        """, sample_rooms)
        conn.commit()

    # Seed sample reservations if none exists
    cursor.execute("SELECT COUNT(*) as count FROM reservations")
    if cursor.fetchone()["count"] == 0:
        today = datetime.date.today()
        sample_reservations = [
            ("Ananya Sharma", "ananya.sharma@example.com", "+91 98765 43210", 2,
             (today - datetime.timedelta(days=1)).strftime("%Y-%m-%d"),
             (today + datetime.timedelta(days=2)).strftime("%Y-%m-%d"),
             1, "Checked-in", "Paid", 5400, "Late check-in requested."),
            ("Rohan Kapoor", "rohan.k@example.com", "+91 98111 22334", 4,
             (today).strftime("%Y-%m-%d"),
             (today + datetime.timedelta(days=3)).strftime("%Y-%m-%d"),
             2, "Checked-in", "Pending", 8400, "Airport pickup arranged."),
            ("Dr. Meera Iyer", "meera.iyer@example.com", "+91 99200 55443", 5,
             (today + datetime.timedelta(days=4)).strftime("%Y-%m-%d"),
             (today + datetime.timedelta(days=7)).strftime("%Y-%m-%d"),
             2, "Confirmed", "Paid", 13500, "Quiet room preference."),
            ("Vikram Malhotra", "vikram.m@example.com", "+91 97654 32190", 7,
             (today + datetime.timedelta(days=6)).strftime("%Y-%m-%d"),
             (today + datetime.timedelta(days=10)).strftime("%Y-%m-%d"),
             4, "Confirmed", "Pending", 32000, "Executive stay with VIP welcome."),
        ]
        cursor.executemany("""
            INSERT INTO reservations (guest_name, guest_email, guest_phone, room_id, check_in, check_out, guests, status, payment_status, total_amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_reservations)
        conn.commit()

    conn.close()


# Authentication functions
def register_user(name, email, password, role="Administrator"):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
        if cursor.fetchone():
            return False, "An account with this email already exists."
        
        pwd_hash = hash_password(password)
        cursor.execute("""
            INSERT INTO users (name, email, password_hash, role)
            VALUES (?, ?, ?, ?)
        """, (name.strip(), email.strip().lower(), pwd_hash, role))
        conn.commit()
        return True, "Account registered successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def authenticate_user(email, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
        user = cursor.fetchone()
        if not user:
            return None, "Invalid email or password."
        
        if verify_password(password, user["password_hash"]):
            return dict(user), "Success"
        return None, "Invalid email or password."
    finally:
        conn.close()


# Rooms management functions
def get_all_rooms():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM rooms ORDER BY number ASC")
    rooms = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rooms


def add_room(number, room_type, price, status="Available", amenities="Wi-Fi, AC, TV"):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM rooms WHERE LOWER(number) = LOWER(?)", (number.strip(),))
        if cursor.fetchone():
            return False, f"Room number '{number}' already exists."
        cursor.execute("""
            INSERT INTO rooms (number, type, price, status, amenities)
            VALUES (?, ?, ?, ?, ?)
        """, (number.strip(), room_type, float(price), status, amenities.strip()))
        conn.commit()
        return True, "Room added successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def update_room(room_id, number, room_type, price, status, amenities="Wi-Fi, AC, TV"):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM rooms WHERE LOWER(number) = LOWER(?) AND id != ?", (number.strip(), room_id))
        if cursor.fetchone():
            return False, f"Room number '{number}' is already assigned to another room."
        cursor.execute("""
            UPDATE rooms
            SET number = ?, type = ?, price = ?, status = ?, amenities = ?
            WHERE id = ?
        """, (number.strip(), room_type, float(price), status, amenities.strip(), room_id))
        conn.commit()
        return True, "Room updated successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def delete_room(room_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Check active reservations
        cursor.execute("""
            SELECT id FROM reservations 
            WHERE room_id = ? AND status IN ('Confirmed', 'Checked-in')
        """, (room_id,))
        if cursor.fetchone():
            return False, "Cannot delete room: It has active (Confirmed/Checked-in) reservations."
        cursor.execute("DELETE FROM rooms WHERE id = ?", (room_id,))
        conn.commit()
        return True, "Room deleted successfully."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


# Reservations management functions
def check_room_overlap(room_id, check_in, check_out, exclude_id=None):
    """
    Checks if there's any active booking conflicting with given dates:
    Conflict condition: check_in < existing_checkout AND check_out > existing_checkin
    """
    conn = get_connection()
    cursor = conn.cursor()
    query = """
        SELECT id, check_in, check_out, guest_name FROM reservations
        WHERE room_id = ? 
          AND status IN ('Confirmed', 'Checked-in')
          AND check_in < ? 
          AND check_out > ?
    """
    params = [room_id, check_out, check_in]
    if exclude_id:
        query += " AND id != ?"
        params.append(exclude_id)
        
    cursor.execute(query, params)
    conflict = cursor.fetchone()
    conn.close()
    return conflict


def get_all_reservations():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT r.*, rm.number as room_number, rm.type as room_type, rm.price as room_price
        FROM reservations r
        JOIN rooms rm ON r.room_id = rm.id
        ORDER BY r.created_at DESC
    """)
    reservations = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return reservations


def create_reservation(guest_name, guest_email, guest_phone, room_id, check_in, check_out, guests=1, payment_status="Pending", notes=""):
    try:
        d_in = datetime.date.fromisoformat(str(check_in))
        d_out = datetime.date.fromisoformat(str(check_out))
        if d_out <= d_in:
            return False, "Check-out date must be strictly after Check-in date."
        
        nights = (d_out - d_in).days
        
        # Check conflicts
        conflict = check_room_overlap(room_id, str(check_in), str(check_out))
        if conflict:
            return False, f"Room is already reserved from {conflict['check_in']} to {conflict['check_out']} by {conflict['guest_name']}."
        
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT price, status FROM rooms WHERE id = ?", (room_id,))
        room = cursor.fetchone()
        if not room:
            conn.close()
            return False, "Selected room was not found."
        if room["status"] == "Maintenance":
            conn.close()
            return False, "Selected room is currently under maintenance."
            
        total_amount = float(room["price"]) * nights
        
        cursor.execute("""
            INSERT INTO reservations (guest_name, guest_email, guest_phone, room_id, check_in, check_out, guests, status, payment_status, total_amount, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'Confirmed', ?, ?, ?)
        """, (guest_name.strip(), guest_email.strip().lower(), guest_phone.strip(), room_id, str(check_in), str(check_out), int(guests), payment_status, total_amount, notes.strip()))
        
        conn.commit()
        conn.close()
        return True, "Reservation confirmed successfully."
    except Exception as e:
        return False, str(e)


def update_reservation_status(res_id, new_status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE reservations SET status = ? WHERE id = ?", (new_status, res_id))
        
        # If checked in, optionally mark room occupied
        cursor.execute("SELECT room_id FROM reservations WHERE id = ?", (res_id,))
        row = cursor.fetchone()
        if row and new_status == "Checked-in":
            cursor.execute("UPDATE rooms SET status = 'Occupied' WHERE id = ?", (row["room_id"],))
        elif row and new_status in ("Checked-out", "Cancelled"):
            # Check if any other reservation is checked in right now
            cursor.execute("""
                SELECT id FROM reservations 
                WHERE room_id = ? AND status = 'Checked-in' AND id != ?
            """, (row["room_id"], res_id))
            if not cursor.fetchone():
                cursor.execute("UPDATE rooms SET status = 'Available' WHERE id = ? AND status != 'Maintenance'", (row["room_id"],))
                
        conn.commit()
        return True, f"Reservation marked as {new_status}."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def update_reservation_payment(res_id, new_payment_status):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE reservations SET payment_status = ? WHERE id = ?", (new_payment_status, res_id))
        conn.commit()
        return True, f"Payment status updated to {new_payment_status}."
    except Exception as e:
        return False, str(e)
    finally:
        conn.close()


def cancel_reservation(res_id):
    return update_reservation_status(res_id, "Cancelled")


def get_guest_summary():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            guest_email,
            MAX(guest_name) as guest_name,
            MAX(guest_phone) as guest_phone,
            COUNT(*) as total_bookings,
            SUM(CASE WHEN status != 'Cancelled' THEN total_amount ELSE 0 END) as total_spent,
            MAX(check_in) as latest_check_in,
            SUM(CASE WHEN payment_status = 'Pending' AND status != 'Cancelled' THEN total_amount ELSE 0 END) as outstanding_balance
        FROM reservations
        GROUP BY guest_email
        ORDER BY latest_check_in DESC
    """)
    guests = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return guests
