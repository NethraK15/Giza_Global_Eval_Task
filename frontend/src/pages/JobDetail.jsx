import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { api } from "../api/client";

export default function JobDetail() {
    const { jobId } = useParams();
    const [job, setJob] = useState(null);
    const [overlayUrl, setOverlayUrl] = useState(null);
    const [csvData, setCsvData] = useState([]);
    const [error, setError] = useState(null);
    const [polling, setPolling] = useState(true);

    const fetchJobStatus = async () => {
        try {
            const res = await api.get(`/api/jobs/${jobId}`);
            setJob(res.data);

            if (res.data.status === "succeeded") {
                setPolling(false);
                fetchResults();
            } else if (res.data.status === "failed") {
                setPolling(false);
                setError("Job failed during processing.");
            }
        } catch (err) {
            console.error("Error fetching job:", err);
            setError("Failed to load job details.");
            setPolling(false);
        }
    };

    const fetchResults = async () => {
        try {
            // Fetch Overlay Image
            const imgRes = await api.get(`/api/jobs/${jobId}/overlay`, { responseType: 'blob' });
            const imgUrl = URL.createObjectURL(imgRes.data);
            setOverlayUrl(imgUrl);

            // Fetch CSV Data
            const csvRes = await api.get(`/api/jobs/${jobId}/csv`, { responseType: 'text' });
            parseCSV(csvRes.data);
        } catch (err) {
            console.error("Error fetching results:", err);
            // Don't fail the whole page if results are missing, just log it.
        }
    };

    const parseCSV = (text) => {
        const lines = text.split("\n").filter(line => line.trim() !== "");
        if (lines.length > 0) {
            const parsed = lines.map(line => line.split(","));
            setCsvData(parsed);
        }
    };

    useEffect(() => {
        fetchJobStatus();
        const interval = setInterval(() => {
            if (polling) {
                fetchJobStatus();
            }
        }, 3000);

        return () => clearInterval(interval);
    }, [jobId, polling]);

    const downloadFile = (url, filename) => {
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    };

    const downloadCSV = () => {
        // Re-construct CSV for download or fetch again as blob
        api.get(`/api/jobs/${jobId}/csv`, { responseType: 'blob' })
            .then((res) => {
                const url = URL.createObjectURL(res.data);
                downloadFile(url, "results.csv");
            })
            .catch(err => console.error("Download failed", err));
    };

    if (!job) return <div className="loading-spinner">Loading job details...</div>;

    return (
        <div className="animate-fade-in">
            <div style={{ marginBottom: '2rem' }}>
                <Link to="/jobs" style={{ color: 'var(--primary)', textDecoration: 'none', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    ← Back to Jobs
                </Link>
            </div>

            <div className="card" style={{ marginBottom: '2rem' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                    <h2 style={{ margin: 0 }}>Job Analysis</h2>
                    <span className={`status-badge status-${job.status}`}>
                        {job.status.toUpperCase()}
                    </span>
                </div>

                <div style={{ color: 'var(--text-muted)' }}>
                    Job ID: {job.id}
                </div>
                {error && <div className="error-message" style={{ color: 'var(--error)', marginTop: '1rem' }}>{error}</div>}
            </div>

            {job.status === "succeeded" && (
                <>
                    <div className="card" style={{ marginBottom: '2rem' }}>
                        <h3 style={{ marginBottom: '1rem' }}>Overlay Preview</h3>
                        {overlayUrl ? (
                            <div style={{ textAlign: 'center' }}>
                                <img src={overlayUrl} alt="Analyzed Overlay" style={{ maxWidth: '100%', borderRadius: '0.5rem', marginBottom: '1rem' }} />
                                <button onClick={() => downloadFile(overlayUrl, "overlay.png")} className="btn-primary">
                                    Download Overlay Image
                                </button>
                            </div>
                        ) : (
                            <p>Loading overlay...</p>
                        )}
                    </div>

                    <div className="card">
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                            <h3 style={{ margin: 0 }}>Analysis Results</h3>
                            <button onClick={downloadCSV} className="btn-secondary">
                                Download CSV
                            </button>
                        </div>

                        {csvData.length > 0 ? (
                            <div style={{ overflowX: 'auto' }}>
                                <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '1rem' }}>
                                    <thead>
                                        <tr>
                                            {csvData[0].map((header, i) => (
                                                <th key={i} style={{ textAlign: 'left', padding: '0.75rem', borderBottom: '1px solid var(--border)', color: 'var(--text-muted)' }}>
                                                    {header}
                                                </th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {csvData.slice(1).map((row, i) => (
                                            <tr key={i}>
                                                {row.map((cell, j) => (
                                                    <td key={j} style={{ padding: '0.75rem', borderBottom: '1px solid var(--border)' }}>
                                                        {cell}
                                                    </td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        ) : (
                            <p>No valid CSV data found.</p>
                        )}
                    </div>
                </>
            )}
        </div>
    );
}
