import { useEffect, useState } from "react";
import { api } from "../api/client";

export default function Jobs() {
    const [jobs, setJobs] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchJobs = async () => {
        try {
            const res = await api.get("/api/jobs");
            setJobs(res.data);
        } catch (err) {
            console.error("Failed to fetch jobs:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchJobs();

        // Polling every 3 seconds
        const interval = setInterval(fetchJobs, 3000);
        return () => clearInterval(interval);
    }, []);

    const formatResult = (resultStr) => {
        if (!resultStr) return "Pending...";
        try {
            const data = JSON.parse(resultStr);
            if (data.detected) {
                return data.detected.join(", ");
            }
            return resultStr;
        } catch (e) {
            return resultStr;
        }
    }

    if (loading && jobs.length === 0) {
        return <div className="animate-fade-in">Loading jobs...</div>;
    }

    return (
        <div className="animate-fade-in">
            <h2 style={{ fontSize: '2rem', marginBottom: '2rem' }}>Analysis History</h2>

            {jobs.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '4rem' }}>
                    <p style={{ color: 'var(--text-muted)' }}>No analysis jobs found. Start by uploading an image!</p>
                </div>
            ) : (
                <div className="grid">
                    {jobs.map(job => (
                        <div key={job.id} className="card">
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>JOB ID</div>
                                    <div style={{ fontSize: '0.875rem', fontWeight: '600', color: 'var(--primary)' }}>
                                        {job.id.substring(0, 8)}...
                                    </div>
                                </div>
                                <span className={`status-badge status-${job.status}`}>
                                    {job.status}
                                </span>
                            </div>

                            <div style={{ marginBottom: '1.5rem' }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>RESULT</div>
                                <div style={{ fontSize: '1rem', fontWeight: '500' }}>
                                    {formatResult(job.result)}
                                </div>
                            </div>

                            <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                {new Date(job.created_at).toLocaleString()}
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
