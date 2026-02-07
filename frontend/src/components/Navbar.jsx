import { NavLink, useNavigate } from "react-router-dom";
import { setAuthToken } from "../api/client";

export default function Navbar() {
    const navigate = useNavigate();
    const user = JSON.parse(localStorage.getItem("user") || "{}");

    const handleLogout = () => {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        setAuthToken(null);
        navigate("/login");
    };

    return (
        <nav>
            <div style={{ marginRight: 'auto', fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary)' }}>
                PID Parser SaaS
            </div>
            <NavLink to="/" className={({ isActive }) => isActive ? "active" : ""}>Upload</NavLink>
            <NavLink to="/jobs" className={({ isActive }) => isActive ? "active" : ""}>My Jobs</NavLink>

            <div style={{ marginLeft: 'auto', display: 'flex', alignItems: 'center', gap: '1rem' }}>
                <span style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    {user.email}
                </span>
                <button
                    onClick={handleLogout}
                    style={{
                        padding: '0.5rem 1rem',
                        fontSize: '0.875rem',
                        background: 'rgba(239, 68, 68, 0.1)',
                        color: 'var(--error)',
                        border: '1px solid rgba(239, 68, 68, 0.2)'
                    }}
                >
                    Logout
                </button>
            </div>
        </nav>
    );
}
