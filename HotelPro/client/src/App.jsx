import React, { useEffect, useMemo, useState } from "react";

const API = "http://localhost:5000/api";
const money = value => new Intl.NumberFormat("en-IN", { style: "currency", currency: "INR", maximumFractionDigits: 0 }).format(value || 0);
const date = value => value ? new Date(value).toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) : "—";

export default function App() {
  const [token, setToken] = useState(localStorage.getItem("hotelpro_token") || "");
  const [user, setUser] = useState(JSON.parse(localStorage.getItem("hotelpro_user") || "null"));
  const [authMode, setAuthMode] = useState("login");
  const [page, setPage] = useState("Overview");
  const [notice, setNotice] = useState("");
  const [loading, setLoading] = useState(false);
  const [dashboard, setDashboard] = useState({ rooms: 0, reservations: 0, guests: 0, occupied: 0, latest: [] });
  const [rooms, setRooms] = useState([]);
  const [reservations, setReservations] = useState([]);
  const [search, setSearch] = useState("");
  const [roomForm, setRoomForm] = useState({ number: "", type: "Double", price: "2500", status: "Available" });
  const [reservationForm, setReservationForm] = useState({ guestName: "", guestEmail: "", room: "", checkIn: "", checkOut: "", guests: 1 });
  const [authForm, setAuthForm] = useState({ name: "", email: "", password: "" });

  async function request(path, options = {}) {
    const response = await fetch(`${API}${path}`, {
      ...options,
      headers: { "Content-Type": "application/json", ...(token ? { Authorization: `Bearer ${token}` } : {}), ...(options.headers || {}) }
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.message || "Something went wrong.");
    return data;
  }

  async function loadData() {
    if (!token) return;
    try {
      const [d, r, b] = await Promise.all([request("/dashboard"), request("/rooms"), request("/reservations")]);
      setDashboard(d); setRooms(r); setReservations(b);
      setReservationForm(old => ({ ...old, room: old.room || r.find(x => x.status !== "Maintenance")?._id || "" }));
    } catch (e) {
      if (e.message.toLowerCase().includes("sign in") || e.message.toLowerCase().includes("session")) logout();
      else setNotice(e.message);
    }
  }

  useEffect(() => { if (token) loadData(); }, [token]);

  function saveSession(data) {
    localStorage.setItem("hotelpro_token", data.token);
    localStorage.setItem("hotelpro_user", JSON.stringify(data.user));
    setToken(data.token); setUser(data.user); setNotice("");
  }
  function logout() {
    localStorage.removeItem("hotelpro_token"); localStorage.removeItem("hotelpro_user");
    setToken(""); setUser(null); setPage("Overview");
  }
  async function submitAuth(e) {
    e.preventDefault(); setLoading(true); setNotice("");
    try {
      const data = await request(`/auth/${authMode}`, { method: "POST", body: JSON.stringify(authForm) });
      saveSession(data);
    } catch (e) { setNotice(e.message); }
    finally { setLoading(false); }
  }
  async function addRoom(e) {
    e.preventDefault(); setNotice("");
    try {
      await request("/rooms", { method: "POST", body: JSON.stringify(roomForm) });
      setRoomForm({ number: "", type: "Double", price: "2500", status: "Available" });
      setNotice("Room added successfully."); await loadData();
    } catch (e) { setNotice(e.message); }
  }
  async function addReservation(e) {
    e.preventDefault(); setNotice("");
    try {
      await request("/reservations", { method: "POST", body: JSON.stringify(reservationForm) });
      setReservationForm(old => ({ ...old, guestName: "", guestEmail: "", checkIn: "", checkOut: "", guests: 1 }));
      setNotice("Reservation created successfully."); await loadData();
    } catch (e) { setNotice(e.message); }
  }
  async function deleteRoom(id) {
    if (!confirm("Delete this room?")) return;
    try { await request(`/rooms/${id}`, { method: "DELETE" }); setNotice("Room deleted."); await loadData(); }
    catch (e) { setNotice(e.message); }
  }
  async function cancelReservation(id) {
    try { await request(`/reservations/${id}`, { method: "DELETE" }); setNotice("Reservation cancelled."); await loadData(); }
    catch (e) { setNotice(e.message); }
  }
  async function updateReservation(id, body) {
    try { await request(`/reservations/${id}`, { method: "PATCH", body: JSON.stringify(body) }); await loadData(); setNotice("Reservation updated."); }
    catch (e) { setNotice(e.message); }
  }

  const filteredRooms = useMemo(() => rooms.filter(r => `${r.number} ${r.type} ${r.status}`.toLowerCase().includes(search.toLowerCase())), [rooms, search]);
  const filteredReservations = useMemo(() => reservations.filter(r => `${r.guestName} ${r.guestEmail} ${r.room?.number || ""} ${r.status}`.toLowerCase().includes(search.toLowerCase())), [reservations, search]);

  if (!token) return <div className="auth-screen"><div className="auth-art"><div className="brand brand-light"><span className="brand-mark"><i className="bi bi-buildings-fill" /></span> HotelPro</div><div className="art-copy"><span className="eyebrow">THE ART OF HOSPITALITY</span><h1>Every stay,<br/><em>beautifully</em> managed.</h1><p>One calm, clear place to manage your rooms, guests and reservations.</p><div className="art-foot"><i className="bi bi-shield-check" /> Secure operations. Thoughtful experiences.</div></div><div className="art-orb orb-one"/><div className="art-orb orb-two"/></div><div className="auth-panel"><div className="auth-box"><div className="mobile-brand brand"><span className="brand-mark"><i className="bi bi-buildings-fill" /></span> HotelPro</div><span className="eyebrow">WELCOME TO HOTELPRO</span><h2>{authMode === "login" ? "Good to have you back." : "Create your workspace."}</h2><p className="muted">{authMode === "login" ? "Sign in to continue to your dashboard." : "Set up your administrator account to get started."}</p>{notice && <div className="alert alert-warning py-2">{notice}</div>}<form onSubmit={submitAuth} className="auth-form">{authMode === "register" && <label>Full name<input className="form-control" required value={authForm.name} onChange={e => setAuthForm({...authForm, name:e.target.value})} placeholder="e.g. Aanya Sharma"/></label>}<label>Email address<input className="form-control" type="email" required value={authForm.email} onChange={e => setAuthForm({...authForm, email:e.target.value})} placeholder="you@hotel.com"/></label><label>Password<input className="form-control" type="password" minLength="6" required value={authForm.password} onChange={e => setAuthForm({...authForm, password:e.target.value})} placeholder="At least 6 characters"/></label><button className="btn btn-forest w-100 mt-2" disabled={loading}>{loading ? "Please wait…" : authMode === "login" ? "Sign in" : "Create account"} <i className="bi bi-arrow-right ms-2"/></button></form><div className="auth-switch">{authMode === "login" ? "New to HotelPro?" : "Already have an account?"} <button onClick={() => {setAuthMode(authMode === "login" ? "register" : "login");setNotice("");}}>{authMode === "login" ? "Create an account" : "Sign in"}</button></div><div className="auth-privacy"><i className="bi bi-lock-fill"/> Your workspace is protected with secure authentication.</div></div></div></div>;

  const nav = [{ name:"Overview", icon:"grid-1x2" }, { name:"Rooms", icon:"door-open" }, { name:"Reservations", icon:"calendar2-check" }, { name:"Guests", icon:"people" }];
  const activeReservations = reservations.filter(r => !["Cancelled","Checked-out"].includes(r.status)).length;
  const guestsCount = new Set(reservations.map(r => r.guestEmail)).size;

  return <div className="app-shell"><aside className="sidebar"><div className="brand"><span className="brand-mark"><i className="bi bi-buildings-fill"/></span> HotelPro</div><div className="side-label">WORKSPACE</div><nav>{nav.map(n => <button key={n.name} className={`nav-item ${page === n.name ? "active" : ""}`} onClick={() => {setPage(n.name);setSearch("");}}><i className={`bi bi-${n.icon}`}/><span>{n.name}</span>{n.name === "Reservations" && <small>{activeReservations}</small>}</button>)}</nav><div className="sidebar-bottom"><div className="help-card"><div className="help-icon"><i className="bi bi-stars"/></div><strong>Make every stay count.</strong><p>Keep your hotel running smoothly, one detail at a time.</p></div><div className="user-card"><div className="avatar">{(user?.name || "H").split(" ").map(x=>x[0]).join("").slice(0,2).toUpperCase()}</div><div className="user-meta"><strong>{user?.name || "Hotel Admin"}</strong><span>Administrator</span></div><button className="icon-btn" title="Sign out" onClick={logout}><i className="bi bi-box-arrow-right"/></button></div></div></aside><main className="main-area"><header className="topbar"><div className="breadcrumb-text">Workspace <i className="bi bi-chevron-right"/> <strong>{page}</strong></div><div className="top-actions"><span className="status-pill"><span/> System operational</span><div className="top-avatar">{(user?.name || "H")[0].toUpperCase()}</div></div></header><div className="page-content"><div className="page-heading"><div><div className="eyebrow">{page === "Overview" ? "YOUR HOTEL AT A GLANCE" : "HOTEL OPERATIONS"}</div><h1>{page === "Overview" ? <>Good day, {user?.name?.split(" ")[0] || "there"} <span className="wave">✦</span></> : page}</h1><p>{page === "Overview" ? "Here’s what’s happening across your property today." : page === "Rooms" ? "Manage room types, rates and availability." : page === "Reservations" ? "Keep every booking organised from arrival to departure." : "A clear view of the guests staying with you."}</p></div>{page === "Rooms" && <button className="btn btn-forest" onClick={() => document.getElementById("room-number")?.focus()}><i className="bi bi-plus-lg me-2"/>Add a room</button>}{page === "Reservations" && <button className="btn btn-forest" onClick={() => document.getElementById("guest-name")?.focus()}><i className="bi bi-plus-lg me-2"/>New reservation</button>}</div>
      {notice && <div className="alert alert-info alert-dismissible py-2 notice">{notice}<button className="btn-close" onClick={() => setNotice("")}/></div>}
      {page === "Overview" && <><div className="welcome-banner"><div className="banner-text"><span className="eyebrow">YOUR HOSPITALITY, IN HARMONY</span><h2>Good service starts<br/>behind the scenes.</h2><p>Stay on top of your rooms and reservations with a little more peace of mind.</p><button className="banner-link" onClick={() => setPage("Reservations")}>Explore reservations <i className="bi bi-arrow-up-right"/></button></div><div className="banner-illustration"><div className="sun"/><div className="building"><div className="roof"/><div className="windows">{Array.from({length:12},(_,i)=><span key={i}/>)}</div><div className="door"/></div><div className="plant plant-a">✦</div><div className="plant plant-b">✧</div></div></div><div className="stats-grid"><Stat icon="door-open" label="Total rooms" value={dashboard.rooms} note={`${Math.max(dashboard.rooms-dashboard.occupied,0)} not occupied`} tone="green"/><Stat icon="calendar2-check" label="Reservations" value={activeReservations} note="Active bookings" tone="blue"/><Stat icon="people" label="Unique guests" value={guestsCount} note="Across all bookings" tone="peach"/><Stat icon="key" label="Occupied rooms" value={dashboard.occupied} note={dashboard.rooms ? `${Math.round(dashboard.occupied/dashboard.rooms*100)}% of all rooms` : "No rooms added yet"} tone="purple"/></div><div className="content-grid"><section className="panel recent-panel"><div className="panel-heading"><div><h3>Recent reservations</h3><p>Your latest guest activity</p></div><button className="text-action" onClick={() => setPage("Reservations")}>View all <i className="bi bi-arrow-right"/></button></div><ReservationTable data={dashboard.latest} compact onCancel={cancelReservation} onUpdate={updateReservation}/>{dashboard.latest.length === 0 && <Empty text="Your recent reservations will appear here."/>}</section><section className="panel occupancy-panel"><div className="panel-heading"><div><h3>Room availability</h3><p>A quick look at your property</p></div><i className="bi bi-three-dots"/></div><div className="occupancy-number"><strong>{dashboard.rooms ? Math.round((dashboard.rooms-dashboard.occupied)/dashboard.rooms*100) : 0}%</strong><span>available</span></div><div className="progress occupancy-progress"><div style={{width:`${dashboard.rooms ? Math.max(0,Math.min(100,(dashboard.rooms-dashboard.occupied)/dashboard.rooms*100)) : 0}%`}}/></div><div className="legend-row"><span><i className="dot available"/> Available</span><strong>{rooms.filter(r=>r.status==="Available").length}</strong></div><div className="legend-row"><span><i className="dot occupied"/> Occupied</span><strong>{rooms.filter(r=>r.status==="Occupied").length}</strong></div><div className="legend-row"><span><i className="dot maintenance"/> Maintenance</span><strong>{rooms.filter(r=>r.status==="Maintenance").length}</strong></div><button className="outline-action w-100 mt-4" onClick={() => setPage("Rooms")}>Manage rooms <i className="bi bi-arrow-right"/></button></section></div></>}
      {page === "Rooms" && <><section className="panel form-panel"><div className="panel-heading"><div><h3>Add a room</h3><p>Enter room details to add it to your inventory.</p></div><span className="soft-tag">ROOM INVENTORY</span></div><form onSubmit={addRoom} className="form-grid"><label>Room number<input id="room-number" className="form-control" required value={roomForm.number} onChange={e=>setRoomForm({...roomForm,number:e.target.value})} placeholder="e.g. 204"/></label><label>Room type<select className="form-select" value={roomForm.type} onChange={e=>setRoomForm({...roomForm,type:e.target.value})}><option>Single</option><option>Double</option><option>Deluxe</option><option>Suite</option></select></label><label>Price per night (₹)<input className="form-control" type="number" min="0" required value={roomForm.price} onChange={e=>setRoomForm({...roomForm,price:e.target.value})}/></label><label>Status<select className="form-select" value={roomForm.status} onChange={e=>setRoomForm({...roomForm,status:e.target.value})}><option>Available</option><option>Occupied</option><option>Maintenance</option></select></label><div className="form-submit"><button className="btn btn-forest"><i className="bi bi-plus-lg me-2"/>Save room</button></div></form></section><section className="panel table-panel"><div className="panel-heading"><div><h3>All rooms <span className="count-tag">{rooms.length}</span></h3><p>Room inventory and current status</p></div><SearchBox value={search} onChange={setSearch} placeholder="Search rooms…"/></div><div className="table-responsive"><table className="table hotel-table"><thead><tr><th>ROOM</th><th>TYPE</th><th>PRICE / NIGHT</th><th>STATUS</th><th></th></tr></thead><tbody>{filteredRooms.map(r=><tr key={r._id}><td><strong className="room-number">{r.number}</strong></td><td>{r.type}</td><td>{money(r.price)}</td><td><Status value={r.status}/></td><td className="text-end"><button className="icon-btn danger" title="Delete room" onClick={()=>deleteRoom(r._id)}><i className="bi bi-trash3"/></button></td></tr>)}</tbody></table>{filteredRooms.length===0 && <Empty text="No rooms found. Add your first room above."/ >}</div></section></>}
      {page === "Reservations" && <><section className="panel form-panel"><div className="panel-heading"><div><h3>Create a reservation</h3><p>Record a guest booking and select an available room.</p></div><span className="soft-tag">NEW BOOKING</span></div>{rooms.filter(r=>r.status!=="Maintenance").length===0 && <div className="alert alert-warning">Add a room before creating a reservation.</div>}<form onSubmit={addReservation} className="form-grid"><label>Guest name<input id="guest-name" className="form-control" required value={reservationForm.guestName} onChange={e=>setReservationForm({...reservationForm,guestName:e.target.value})} placeholder="Full name"/></label><label>Guest email<input className="form-control" type="email" required value={reservationForm.guestEmail} onChange={e=>setReservationForm({...reservationForm,guestEmail:e.target.value})} placeholder="guest@email.com"/></label><label>Room<select className="form-select" required value={reservationForm.room} onChange={e=>setReservationForm({...reservationForm,room:e.target.value})}><option value="">Select a room</option>{rooms.filter(r=>r.status!=="Maintenance").map(r=><option key={r._id} value={r._id}>{r.number} · {r.type} · {money(r.price)}/night</option>)}</select></label><label>Guests<input className="form-control" type="number" min="1" max="20" required value={reservationForm.guests} onChange={e=>setReservationForm({...reservationForm,guests:e.target.value})}/></label><label>Check-in<input className="form-control" type="date" required value={reservationForm.checkIn} onChange={e=>setReservationForm({...reservationForm,checkIn:e.target.value})}/></label><label>Check-out<input className="form-control" type="date" required min={reservationForm.checkIn || undefined} value={reservationForm.checkOut} onChange={e=>setReservationForm({...reservationForm,checkOut:e.target.value})}/></label><div className="form-submit"><button className="btn btn-forest" disabled={!rooms.some(r=>r.status!=="Maintenance")}><i className="bi bi-calendar-plus me-2"/>Confirm reservation</button></div></form></section><section className="panel table-panel"><div className="panel-heading"><div><h3>All reservations <span className="count-tag">{reservations.length}</span></h3><p>Bookings, guest details and payment status</p></div><SearchBox value={search} onChange={setSearch} placeholder="Search reservations…"/></div><ReservationTable data={filteredReservations} onCancel={cancelReservation} onUpdate={updateReservation}/>{filteredReservations.length===0 && <Empty text="No reservations found yet."/>}</section></>}
      {page === "Guests" && <section className="panel table-panel"><div className="panel-heading"><div><h3>Guest directory <span className="count-tag">{guestsCount}</span></h3><p>Guests who have made a reservation</p></div><SearchBox value={search} onChange={setSearch} placeholder="Search guests…"/></div><div className="table-responsive"><table className="table hotel-table"><thead><tr><th>GUEST</th><th>EMAIL</th><th>BOOKINGS</th><th>LATEST CHECK-IN</th></tr></thead><tbody>{[...new Map(reservations.map(r=>[r.guestEmail,{...r,bookings:reservations.filter(x=>x.guestEmail===r.guestEmail).length}])).values()].filter(g=>`${g.guestName} ${g.guestEmail}`.toLowerCase().includes(search.toLowerCase())).map(g=><tr key={g.guestEmail}><td><div className="guest-cell"><span className="guest-avatar">{g.guestName?.[0]?.toUpperCase()}</span><strong>{g.guestName}</strong></div></td><td>{g.guestEmail}</td><td>{g.bookings}</td><td>{date(g.checkIn)}</td></tr>)}</tbody></table>{guestsCount===0 && <Empty text="Guest details will appear after your first reservation."/>}</div></section>}
      <footer className="page-footer"><span>© 2026 HotelPro</span><span><i className="bi bi-shield-check me-1"/>Built for better hospitality</span></footer></div></main></div>;
}

function Stat({icon,label,value,note,tone}) { return <div className="stat-card"><div className={`stat-icon ${tone}`}><i className={`bi bi-${icon}`}/></div><span className="stat-label">{label}</span><strong className="stat-value">{value}</strong><span className="stat-note">{note}</span></div>; }
function SearchBox({value,onChange,placeholder}) { return <div className="search-box"><i className="bi bi-search"/><input value={value} onChange={e=>onChange(e.target.value)} placeholder={placeholder}/></div>; }
function Status({value}) { const cls = value?.toLowerCase().replace(/[^a-z]+/g,"-"); return <span className={`status-badge ${cls}`}>{value}</span>; }
function Empty({text}) { return <div className="empty-state"><div className="empty-icon"><i className="bi bi-inbox"/></div><p>{text}</p></div>; }
function ReservationTable({data=[],compact=false,onCancel,onUpdate}) {
  return <div className="table-responsive"><table className="table hotel-table"><thead><tr><th>GUEST</th><th>ROOM</th><th>STAY</th><th>STATUS</th>{!compact && <th>PAYMENT</th>}{!compact && <th></th>}</tr></thead><tbody>{data.map(r=><tr key={r._id}><td><div className="guest-cell"><span className="guest-avatar">{r.guestName?.[0]?.toUpperCase() || "G"}</span><div><strong>{r.guestName}</strong><small>{r.guestEmail}</small></div></div></td><td><strong>{r.room?.number || "—"}</strong><small>{r.room?.type || "Room"}</small></td><td><span className="stay-date">{date(r.checkIn)}</span><small>to {date(r.checkOut)}</small></td><td>{compact ? <Status value={r.status}/> : <select className="status-select" value={r.status} onChange={e=>onUpdate?.(r._id,{status:e.target.value})}><option>Confirmed</option><option>Checked-in</option><option>Checked-out</option><option>Cancelled</option></select>}</td>{!compact && <td><button className={`payment-chip ${r.paymentStatus==="Paid"?"paid":""}`} onClick={()=>onUpdate?.(r._id,{paymentStatus:r.paymentStatus==="Paid"?"Pending":"Paid"})}><i className={`bi ${r.paymentStatus==="Paid"?"bi-check-circle-fill":"bi-clock"}`}/> {r.paymentStatus || "Pending"}</button></td>}{!compact && <td className="text-end">{r.status!=="Cancelled" && r.status!=="Checked-out" && <button className="icon-btn danger" title="Cancel reservation" onClick={()=>onCancel?.(r._id)}><i className="bi bi-x-circle"/></button>}</td>}</tr>)}</tbody></table></div>;
}
