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

    const formatResult = (job) => {
        if (job.status === "queued") return <span style={{ color: 'var(--text-muted)' }}>Waiting in queue...</span>;
        if (job.status === "processing") return <span style={{ color: 'var(--warning)' }}>Running YOLO inference...</span>;
        if (job.status === "failed") return <span style={{ color: 'var(--error)' }}>Analysis failed</span>;

        if (!job.result) return "Pending...";

        try {
            const data = JSON.parse(job.result);
            if (data.detected && data.detected.length > 0) {
                return (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                        {data.detected.map((item, i) => (
                            <span key={i} style={{
                                background: 'rgba(99, 102, 241, 0.1)',
                                color: 'var(--primary)',
                                padding: '0.2rem 0.6rem',
                                borderRadius: '0.5rem',
                                fontSize: '0.875rem',
                                border: '1px solid rgba(99, 102, 241, 0.2)'
                            }}>
                                {item}
                            </span>
                        ))}
                    </div>
                );
            }
            return data.detected?.length === 0 ? "No objects detected" : job.result;
        } catch (e) {
            return job.result;
        }
    }

    if (loading && jobs.length === 0) {
        return (
            <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '50vh' }}>
                <div className="animate-spin" style={{ width: '40px', height: '40px', border: '4px solid var(--border)', borderTopColor: 'var(--primary)', borderRadius: '50%' }}></div>
            </div>
        );
    }

    return (
        <div className="animate-fade-in">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '3rem' }}>
                <h2 style={{ fontSize: '2.5rem', margin: 0 }}>Analysis History</h2>
                <div style={{ fontSize: '0.875rem', color: 'var(--text-muted)' }}>
                    Auto-refreshes every 3s
                </div>
            </div>

            {jobs.length === 0 ? (
                <div className="card" style={{ textAlign: 'center', padding: '5rem' }}>
                    <div style={{ fontSize: '4rem', marginBottom: '1.5rem' }}>📊</div>
                    <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>No analysis jobs found. Start by uploading an image!</p>
                </div>
            ) : (
                <div className="grid">
                    {jobs.map(job => (
                        <div key={job.id} className="card" style={{ display: 'flex', flexDirection: 'column' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
                                <div>
                                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.25rem', letterSpacing: '0.05em' }}>JOB ID</div>
                                    <div style={{ fontSize: '0.875rem', fontWeight: '700', color: 'var(--primary)' }}>
                                        {job.id.substring(0, 13).toUpperCase()}...
                                    </div>
                                </div>
                                <span className={`status-badge status-${job.status}`}>
                                    {job.status}
                                </span>
                            </div>

                            <div style={{ flex: 1, marginBottom: '1.5rem' }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: '0.5rem', letterSpacing: '0.05em' }}>DETECTION RESULTS</div>
                                <div style={{ fontSize: '1rem', fontWeight: '500', minHeight: '3rem' }}>
                                    {formatResult(job)}
                                </div>
                            </div>

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                    {new Date(job.created_at).toLocaleDateString()}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                                    {new Date(job.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}

