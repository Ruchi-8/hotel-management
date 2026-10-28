import express from "express";
import mongoose from "mongoose";
import cors from "cors";
import dotenv from "dotenv";
import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";

dotenv.config();
const app = express();
app.use(cors({ origin: process.env.CLIENT_ORIGIN || "http://localhost:5173" }));
app.use(express.json());

const userSchema = new mongoose.Schema({
  name: { type: String, required: true, trim: true },
  email: { type: String, required: true, unique: true, lowercase: true, trim: true },
  passwordHash: { type: String, required: true }
}, { timestamps: true });

const roomSchema = new mongoose.Schema({
  number: { type: String, required: true, trim: true },
  type: { type: String, enum: ["Single", "Double", "Deluxe", "Suite"], default: "Double" },
  price: { type: Number, required: true, min: 0 },
  status: { type: String, enum: ["Available", "Occupied", "Maintenance"], default: "Available" }
}, { timestamps: true });

const reservationSchema = new mongoose.Schema({
  guestName: { type: String, required: true, trim: true },
  guestEmail: { type: String, required: true, trim: true, lowercase: true },
  room: { type: mongoose.Schema.Types.ObjectId, ref: "Room", required: true },
  checkIn: { type: Date, required: true },
  checkOut: { type: Date, required: true },
  guests: { type: Number, default: 1, min: 1 },
  status: { type: String, enum: ["Confirmed", "Checked-in", "Checked-out", "Cancelled"], default: "Confirmed" },
  paymentStatus: { type: String, enum: ["Pending", "Paid"], default: "Pending" }
}, { timestamps: true });

const User = mongoose.model("User", userSchema);
const Room = mongoose.model("Room", roomSchema);
const Reservation = mongoose.model("Reservation", reservationSchema);

function auth(req, res, next) {
  const header = req.headers.authorization || "";
  const token = header.startsWith("Bearer ") ? header.slice(7) : "";
  if (!token) return res.status(401).json({ message: "Please sign in to continue." });
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET || "development_secret_change_me");
    next();
  } catch {
    return res.status(401).json({ message: "Session expired. Please sign in again." });
  }
}

app.get("/api/health", (_req, res) => res.json({ status: "ok", service: "HotelPro API" }));

app.post("/api/auth/register", async (req, res) => {
  try {
    const { name, email, password } = req.body;
    if (!name?.trim() || !email?.trim() || !password || password.length < 6)
      return res.status(400).json({ message: "Enter your name, email, and a password of at least 6 characters." });
    const existing = await User.findOne({ email: email.toLowerCase().trim() });
    if (existing) return res.status(409).json({ message: "An account with this email already exists." });
    const passwordHash = await bcrypt.hash(password, 12);
    const user = await User.create({ name, email, passwordHash });
    const token = jwt.sign({ id: user._id, name: user.name, email: user.email }, process.env.JWT_SECRET || "development_secret_change_me", { expiresIn: "12h" });
    res.status(201).json({ token, user: { id: user._id, name: user.name, email: user.email } });
  } catch (error) { res.status(500).json({ message: "Could not create account.", detail: error.message }); }
});

app.post("/api/auth/login", async (req, res) => {
  try {
    const email = req.body.email?.toLowerCase().trim();
    const user = await User.findOne({ email });
    if (!user || !(await bcrypt.compare(req.body.password || "", user.passwordHash)))
      return res.status(401).json({ message: "Invalid email or password." });
    const token = jwt.sign({ id: user._id, name: user.name, email: user.email }, process.env.JWT_SECRET || "development_secret_change_me", { expiresIn: "12h" });
    res.json({ token, user: { id: user._id, name: user.name, email: user.email } });
  } catch (error) { res.status(500).json({ message: "Could not sign in.", detail: error.message }); }
});

app.get("/api/dashboard", auth, async (_req, res) => {
  try {
    const [rooms, reservations, guests] = await Promise.all([
      Room.countDocuments(),
      Reservation.countDocuments({ status: { $ne: "Cancelled" } }),
      Reservation.distinct("guestEmail")
    ]);
    const occupied = await Room.countDocuments({ status: "Occupied" });
    const latest = await Reservation.find().populate("room").sort({ createdAt: -1 }).limit(5);
    res.json({ rooms, reservations, guests: guests.length, occupied, latest });
  } catch (error) { res.status(500).json({ message: "Could not load dashboard.", detail: error.message }); }
});

app.get("/api/rooms", auth, async (_req, res) => {
  try { res.json(await Room.find().sort({ createdAt: -1 })); }
  catch (error) { res.status(500).json({ message: "Could not load rooms.", detail: error.message }); }
});

app.post("/api/rooms", auth, async (req, res) => {
  try {
    const { number, type, price, status } = req.body;
    if (!number?.trim() || price === "" || !Number.isFinite(Number(price)) || Number(price) < 0)
      return res.status(400).json({ message: "Enter a room number and a valid non-negative price." });
    if (await Room.findOne({ number: number.trim() })) return res.status(409).json({ message: "That room number already exists." });
    const room = await Room.create({ number, type, price: Number(price), status });
    res.status(201).json(room);
  } catch (error) { res.status(500).json({ message: "Could not add room.", detail: error.message }); }
});

app.patch("/api/rooms/:id", auth, async (req, res) => {
  try {
    const room = await Room.findByIdAndUpdate(req.params.id, req.body, { new: true, runValidators: true });
    if (!room) return res.status(404).json({ message: "Room not found." });
    res.json(room);
  } catch (error) { res.status(400).json({ message: "Could not update room.", detail: error.message }); }
});

app.delete("/api/rooms/:id", auth, async (req, res) => {
  try {
    const active = await Reservation.exists({ room: req.params.id, status: { $nin: ["Cancelled", "Checked-out"] } });
    if (active) return res.status(409).json({ message: "This room has an active reservation and cannot be deleted." });
    const room = await Room.findByIdAndDelete(req.params.id);
    if (!room) return res.status(404).json({ message: "Room not found." });
    res.json({ message: "Room deleted." });
  } catch (error) { res.status(500).json({ message: "Could not delete room.", detail: error.message }); }
});

app.get("/api/reservations", auth, async (_req, res) => {
  try { res.json(await Reservation.find().populate("room").sort({ createdAt: -1 })); }
  catch (error) { res.status(500).json({ message: "Could not load reservations.", detail: error.message }); }
});

app.post("/api/reservations", auth, async (req, res) => {
  try {
    const { guestName, guestEmail, room: roomId, checkIn, checkOut, guests } = req.body;
    if (!guestName?.trim() || !guestEmail?.trim() || !roomId || !checkIn || !checkOut)
      return res.status(400).json({ message: "Complete all required reservation fields." });
    if (new Date(checkOut) <= new Date(checkIn))
      return res.status(400).json({ message: "Check-out must be after check-in." });
    const room = await Room.findById(roomId);
    if (!room) return res.status(404).json({ message: "Selected room was not found." });
    if (room.status === "Maintenance") return res.status(409).json({ message: "This room is under maintenance." });
    const conflict = await Reservation.exists({
      room: roomId, status: { $nin: ["Cancelled", "Checked-out"] },
      checkIn: { $lt: new Date(checkOut) }, checkOut: { $gt: new Date(checkIn) }
    });
    if (conflict) return res.status(409).json({ message: "This room already has a reservation for those dates." });
    const reservation = await Reservation.create({ guestName, guestEmail, room: roomId, checkIn, checkOut, guests: Number(guests) || 1 });
    res.status(201).json(await reservation.populate("room"));
  } catch (error) { res.status(500).json({ message: "Could not create reservation.", detail: error.message }); }
});

app.patch("/api/reservations/:id", auth, async (req, res) => {
  try {
    const allowed = ["status", "paymentStatus"];
    const update = Object.fromEntries(Object.entries(req.body).filter(([key]) => allowed.includes(key)));
    const reservation = await Reservation.findByIdAndUpdate(req.params.id, update, { new: true, runValidators: true }).populate("room");
    if (!reservation) return res.status(404).json({ message: "Reservation not found." });
    res.json(reservation);
  } catch (error) { res.status(400).json({ message: "Could not update reservation.", detail: error.message }); }
});

app.delete("/api/reservations/:id", auth, async (req, res) => {
  try {
    const reservation = await Reservation.findByIdAndUpdate(req.params.id, { status: "Cancelled" }, { new: true }).populate("room");
    if (!reservation) return res.status(404).json({ message: "Reservation not found." });
    res.json(reservation);
  } catch (error) { res.status(500).json({ message: "Could not cancel reservation.", detail: error.message }); }
});

const port = process.env.PORT || 5000;
mongoose.connect(process.env.MONGO_URI || "mongodb://127.0.0.1:27017/hotelpro")
  .then(() => app.listen(port, () => console.log(`HotelPro API running at http://localhost:${port}`)))
  .catch(error => {
    console.error("MongoDB connection failed. Make sure MongoDB is running and MONGO_URI is correct.", error.message);
    process.exit(1);
  });
