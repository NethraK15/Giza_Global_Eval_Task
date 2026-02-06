import { NavLink } from "react-router-dom";

export default function Navbar() {
    return (
        <nav>
            <div style={{ marginRight: 'auto', fontSize: '1.5rem', fontWeight: '700', color: 'var(--primary)' }}>
                PID Parser SaaS
            </div>
            <NavLink to="/" className={({ isActive }) => isActive ? "active" : ""}>Upload</NavLink>
            <NavLink to="/jobs" className={({ isActive }) => isActive ? "active" : ""}>My Jobs</NavLink>
        </nav>
    );
}
