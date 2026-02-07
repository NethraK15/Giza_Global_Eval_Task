import { useState, useRef } from "react";
import { api } from "../api/client";
import { useNavigate } from "react-router-dom";

export default function Upload() {
    const [file, setFile] = useState(null);
    const [preview, setPreview] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");
    const navigate = useNavigate();
    const fileInputRef = useRef(null);

    const handleFileChange = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setPreview(URL.createObjectURL(selectedFile));
            setError("");
        }
    };

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

    const triggerFileInput = () => {
        fileInputRef.current.click();
    };

    return (
        <div className="card animate-fade-in" style={{ maxWidth: '700px', margin: '0 auto', textAlign: 'center' }}>
            <h2 style={{ fontSize: '2.5rem', marginBottom: '0.5rem', background: 'linear-gradient(to right, #818cf8, #c084fc)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                Analyze P&ID
            </h2>
            <p style={{ color: 'var(--text-muted)', marginBottom: '2.5rem', fontSize: '1.1rem' }}>
                Our advanced YOLO model detects instruments and equipment in your diagrams with high precision.
            </p>

            <div
                className="upload-zone"
                onClick={triggerFileInput}
                style={{
                    border: '2px dashed var(--border)',
                    borderRadius: '2rem',
                    padding: '3rem',
                    marginBottom: '2rem',
                    cursor: 'pointer',
                    background: 'rgba(255, 255, 255, 0.03)',
                    transition: 'all 0.3s ease',
                    position: 'relative',
                    overflow: 'hidden'
                }}
            >
                <input
                    type="file"
                    ref={fileInputRef}
                    accept="image/png, image/jpeg"
                    onChange={handleFileChange}
                    style={{ display: 'none' }}
                />

                {!preview ? (
                    <div>
                        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📁</div>
                        <p style={{ fontWeight: '600', marginBottom: '0.5rem' }}>Click to select or drag & drop</p>
                        <p style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>PNG or JPG (max. 10MB)</p>
                    </div>
                ) : (
                    <div style={{ position: 'relative' }}>
                        <img
                            src={preview}
                            alt="Preview"
                            style={{ maxWidth: '100%', maxHeight: '300px', borderRadius: '1rem', boxShadow: '0 10px 25px rgba(0,0,0,0.3)' }}
                        />
                        <div style={{ marginTop: '1rem', color: 'var(--primary)', fontWeight: '600' }}>
                            {file.name}
                        </div>
                    </div>
                )}
            </div>

            {error && (
                <div style={{
                    background: 'rgba(239, 68, 68, 0.1)',
                    color: 'var(--error)',
                    padding: '1rem',
                    borderRadius: '1rem',
                    marginBottom: '1.5rem',
                    fontSize: '0.875rem',
                    border: '1px solid rgba(239, 68, 68, 0.2)'
                }}>
                    {error}
                </div>
            )}

            <button
                onClick={handleUpload}
                disabled={loading || !file}
                style={{
                    width: '100%',
                    padding: '1.25rem',
                    fontSize: '1.1rem',
                    boxShadow: '0 10px 15px -3px rgba(99, 102, 241, 0.3)',
                    opacity: (!file || loading) ? 0.6 : 1
                }}
            >
                {loading ? (
                    <span style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '0.5rem' }}>
                        <svg className="animate-spin" width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" style={{ opacity: 0.25 }}></circle>
                            <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        Uploading...
                    </span>
                ) : "Start Machine Analysis"}
            </button>
        </div >
    );
}

