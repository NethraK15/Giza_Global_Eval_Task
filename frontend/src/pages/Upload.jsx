import { useState } from "react";
import { api } from "../api/client";
import { useNavigate } from "react-router-dom";

export default function Upload() {
    const [file, setFile] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const navigate = useNavigate();

    const handleUpload = async () => {
        if (!file) {
            setError("Please select a file first.");
            return;
        }

        setLoading(true);
        setError("");

        try {
            const formData = new FormData();
            formData.append("file", file);

            const res = await api.post("/api/jobs", formData);
            console.log("Job created:", res.data);
            navigate("/jobs");
        } catch (err) {
            setError(err.response?.data?.detail || "Upload failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="card animate-fade-in" style={{ maxWidth: '600px', margin: '0 auto' }}>
            <h2 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Analyze P&ID</h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2rem' }}>
                Upload a P&ID diagram (PNG/JPG) to detect instruments and equipment using YOLO.
            </p>

            <div style={{ marginBottom: '1.5rem' }}>
                <input
                    type="file"
                    accept="image/png, image/jpeg"
                    onChange={e => {
                        setFile(e.target.files[0]);
                        setError("");
                    }}
                />
                {file && (
                    <p style={{ fontSize: '0.875rem', color: 'var(--primary)', marginBottom: '1rem' }}>
                        Selected: {file.name}
                    </p>
                )}
            </div>

            {error && (
                <div style={{ color: 'var(--error)', marginBottom: '1rem', fontSize: '0.875rem' }}>
                    {error}
                </div>
            )}

            <button
                onClick={handleUpload}
                disabled={loading}
                style={{ width: '100%', padding: '1rem' }}
            >
                {loading ? "Uploading..." : "Start Analysis"}
            </button>
        </div >
    );
}
