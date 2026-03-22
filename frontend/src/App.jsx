import React, { useState, useEffect } from 'react';
import { Briefcase, Building2, MapPin, Award, BookOpen, Star, DollarSign, Loader2, UploadCloud, BarChart3, TrendingUp, CheckCircle, AlertCircle } from 'lucide-react';

const API_BASE = 'http://localhost:8000/api';

function App() {
  const [activeTab, setActiveTab] = useState('predict');
  const [options, setOptions] = useState(null);
  const [status, setStatus] = useState({ loading: true, error: null, initialized: false });

  // Single prediction state
  const [formData, setFormData] = useState({
    Age: 28,
    Gender: "Male",
    Education_Level: "Bachelor",
    Years_of_Experience: 5,
    Job_Role: "",
    Department: "",
    Location: "",
    Performance_Rating: 3,
    Skills: "",
    Company_Tier: "Mid-Size",
    Certifications: "None",
    Past_Companies: 1
  });

  const [prediction, setPrediction] = useState(null);
  const [predicting, setPredicting] = useState(false);

  useEffect(() => {
    fetchOptions();
  }, []);

  const fetchOptions = async () => {
    try {
      const res = await fetch(`${API_BASE}/options`);
      if (!res.ok) throw new Error("Could not fetch options. Backend might be down.");
      const data = await res.json();
      setOptions(data);

      // Init defaults based on fetched data
      setFormData(prev => ({
        ...prev,
        Job_Role: data.job_roles?.[0] || "",
        Department: data.departments?.[0] || "",
        Location: data.locations?.[0] || "",
        Skills: data.skills?.[0] || "",
        Company_Tier: data.company_tiers?.[0] || "Mid-Size",
        Certifications: data.certifications?.[0] || "None",
      }));

      setStatus({ loading: false, error: null, initialized: true });
    } catch (err) {
      setStatus({ loading: false, error: err.message, initialized: false });
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' ? Number(value) : value
    }));
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    setPredicting(true);
    try {
      const res = await fetch(`${API_BASE}/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(formData)
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Prediction failed");
      setPrediction(data);
    } catch (err) {
      alert("Error predicting: " + err.message);
    } finally {
      setPredicting(false);
    }
  };

  if (status.loading) {
    return (
      <div className="app-wrapper flex-center" style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', flexDirection: 'column' }}>
        <Loader2 className="spin" size={48} color="var(--accent-color)" />
        <h2 style={{ marginTop: '1rem' }}>Initializing AI Engine...</h2>
      </div>
    );
  }

  if (status.error) {
    return (
      <div className="app-wrapper">
        <div className="glass-container" style={{ textAlign: 'center', borderColor: 'var(--error-color)' }}>
          <AlertCircle size={48} color="var(--error-color)" />
          <h2>Critical System Failure</h2>
          <p>{status.error}</p>
          <button className="btn-secondary" onClick={fetchOptions} style={{ marginTop: '1rem' }}>Retry Connection</button>
        </div>
      </div>
    );
  }

  return (
    <div className="app-wrapper">
      <header>
        <h1>Workforce Salary Predictor</h1>
        <p className="subtitle">AI-Driven Compensation Analytics & Forecasting</p>
        <div className="status-badge">
          <CheckCircle size={16} /> Data & Model Available
        </div>
      </header>

      <div className="tabs">
        <div className={`tab ${activeTab === 'predict' ? 'active' : ''}`} onClick={() => setActiveTab('predict')}>
          <Briefcase size={18} style={{ display: 'inline', marginRight: '6px' }} /> Single Prediction
        </div>
        <div className={`tab ${activeTab === 'batch' ? 'active' : ''}`} onClick={() => setActiveTab('batch')}>
          <UploadCloud size={18} style={{ display: 'inline', marginRight: '6px' }} /> Batch Processing
        </div>
        <div className={`tab ${activeTab === 'resume' ? 'active' : ''}`} onClick={() => setActiveTab('resume')}>
          <BookOpen size={18} style={{ display: 'inline', marginRight: '6px' }} /> Resume AI
        </div>
      </div>

      {activeTab === 'predict' && (
        <div className="main-grid">
          <div className="glass-container">
            <h2><Briefcase size={22} color="var(--accent-color)" /> Employee Profile</h2>
            <form onSubmit={handlePredict}>
              <div className="form-grid">
                <div className="input-group">
                  <label>Age</label>
                  <input type="number" name="Age" min="18" max="65" value={formData.Age} onChange={handleInputChange} />
                </div>

                <div className="input-group">
                  <label>Gender</label>
                  <select name="Gender" value={formData.Gender} onChange={handleInputChange}>
                    {options.genders.map(g => <option key={g} value={g}>{g}</option>)}
                  </select>
                </div>

                <div className="input-group">
                  <label>Education Level</label>
                  <select name="Education_Level" value={formData.Education_Level} onChange={handleInputChange}>
                    {options.education_levels.map(e => <option key={e} value={e}>{e}</option>)}
                  </select>
                </div>

                <div className="input-group">
                  <label>Experience (Years)</label>
                  <input type="number" name="Years_of_Experience" min="0" max="45" value={formData.Years_of_Experience} onChange={handleInputChange} />
                </div>

                <div className="input-group" style={{ gridColumn: '1 / -1' }}>
                  <label>Job Role</label>
                  <select name="Job_Role" value={formData.Job_Role} onChange={handleInputChange}>
                    {options.job_roles.map(r => <option key={r} value={r}>{r}</option>)}
                  </select>
                </div>

                <div className="input-group">
                  <label>Department</label>
                  <select name="Department" value={formData.Department} onChange={handleInputChange}>
                    {options.departments.map(d => <option key={d} value={d}>{d}</option>)}
                  </select>
                </div>

                <div className="input-group">
                  <label>Location</label>
                  <select name="Location" value={formData.Location} onChange={handleInputChange}>
                    {options.locations.map(l => <option key={l} value={l}>{l}</option>)}
                  </select>
                </div>

                <div className="input-group">
                  <label>Primary Skill</label>
                  <select name="Skills" value={formData.Skills} onChange={handleInputChange}>
                    {options.skills.map(s => <option key={s} value={s}>{s}</option>)}
                  </select>
                </div>

                <div className="input-group">
                  <label>Performance (1-5)</label>
                  <input type="number" name="Performance_Rating" min="1" max="5" value={formData.Performance_Rating} onChange={handleInputChange} />
                </div>

                <div className="input-group">
                  <label>Company Tier</label>
                  <select name="Company_Tier" value={formData.Company_Tier} onChange={handleInputChange}>
                    {options.company_tiers.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>

                <div className="input-group">
                  <label>Certifications</label>
                  <select name="Certifications" value={formData.Certifications} onChange={handleInputChange}>
                    {options.certifications.map(c => <option key={c} value={c}>{c}</option>)}
                  </select>
                </div>

                <div className="input-group">
                  <label>Past Companies</label>
                  <input type="number" name="Past_Companies" min="0" max="20" value={formData.Past_Companies} onChange={handleInputChange} />
                </div>
              </div>

              <button type="submit" className="btn-primary" disabled={predicting}>
                {predicting ? <Loader2 className="spin" size={18} /> : <TrendingUp size={18} />}
                {predicting ? 'Computing...' : 'Predict Expected Salary'}
              </button>
            </form>
          </div>

          <div className="glass-container result-card">
            <h2><DollarSign size={24} color="var(--accent-color)" /> Predicted Compensation</h2>
            {prediction ? (
              <>
                <div className="predicted-amount">
                  {new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(prediction.predicted_salary)}
                </div>

                {prediction.real_time_insight && (
                  <div className="real-time-insight" style={{ marginTop: '1.5rem', padding: '1rem', background: 'rgba(59, 130, 246, 0.05)', borderLeft: '4px solid var(--accent-color)', borderRadius: '4px', textAlign: 'left' }}>
                    <h4 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem', color: 'var(--accent-color)', fontSize: '1rem' }}>
                      <Star size={16} /> Real-Time AI Insight
                    </h4>
                    <p style={{ fontSize: '0.95rem', lineHeight: '1.5', color: 'var(--text-main)' }}>{prediction.real_time_insight}</p>
                  </div>
                )}

                <p style={{ marginTop: '1.5rem', color: 'var(--text-secondary)' }}>
                  Market aligned estimate based on advanced machine learning algorithms.
                </p>
                <button className="btn-secondary" onClick={() => setPrediction(null)} style={{ marginTop: '2rem' }}>Clear Result</button>
              </>
            ) : (
              <p style={{ color: 'var(--text-secondary)' }}>
                Fill out the profile and run the prediction to see the expected salary package.
              </p>
            )}
          </div>
        </div>
      )}

      {activeTab === 'batch' && (
        <BatchPrediction />
      )}

      {activeTab === 'resume' && (
        <ResumeAnalysis />
      )}

    </div>
  );
}

function ResumeAnalysis() {
  const [file, setFile] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [results, setResults] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const uploadFile = async () => {
    if (!file) return;
    setAnalyzing(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/predict_resume`, {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Analysis failed");
      setResults(data);
    } catch (err) {
      alert("Error processing resume: " + err.message);
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div className="glass-container">
      <h2><Briefcase size={24} color="var(--accent-color)" /> AI Resume Analysis & Valuation</h2>
      <p style={{ marginBottom: '2rem', color: 'var(--text-secondary)' }}>
        Upload a candidate's resume (PDF or TXT) to instantly extract their professional profile and calculate their market value.
      </p>

      {!results ? (
        <>
          <label className="file-upload">
            <UploadCloud size={48} color={file ? "var(--success-color)" : "var(--accent-color)"} />
            <input type="file" accept=".pdf,.txt" onChange={handleFileChange} style={{ display: 'none' }} />
            <p>{file ? `Selected: ${file.name}` : "Click or drag to upload Resume (PDF/TXT)"}</p>
          </label>
          <button
            className="btn-primary"
            style={{ marginTop: '2rem' }}
            onClick={uploadFile}
            disabled={!file || analyzing}
          >
            {analyzing ? <Loader2 className="spin" size={18} /> : 'Analyze & Predict Compensation'}
          </button>
        </>
      ) : (
        <div>
          <div className="main-grid" style={{ gridTemplateColumns: 'minmax(0, 1fr) minmax(0, 1fr)', gap: '2rem', marginTop: '1rem', textAlign: 'left' }}>
            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)' }}>
              <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1rem', color: 'var(--accent-color)' }}>
                <Award size={20} /> Extracted Profile
              </h3>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '0.75rem', color: 'var(--text-main)' }}>
                <li><strong>Expected Role:</strong> {results.extracted_profile?.Job_Role || "N/A"}</li>
                <li><strong>Location:</strong> {results.extracted_profile?.Location || "N/A"}</li>
                <li><strong>Education:</strong> {results.extracted_profile?.Education_Level || "N/A"}</li>
                <li><strong>Skills:</strong> {results.extracted_profile?.Skills || "N/A"}</li>
              </ul>
            </div>

            <div style={{ background: 'rgba(255,255,255,0.02)', padding: '1.5rem', borderRadius: '12px', border: '1px solid rgba(255,255,255,0.05)', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', textAlign: 'center' }}>
              <h3 style={{ color: 'var(--text-secondary)', marginBottom: '0.5rem' }}>AI Valuated Salary</h3>
              <div style={{ fontSize: '2.5rem', fontWeight: 'bold', color: 'var(--accent-color)', marginBottom: '1rem' }}>
                {new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(results.predicted_salary || 0)}
              </div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-main)', borderTop: '1px solid rgba(255,255,255,0.1)', paddingTop: '1rem', fontStyle: 'italic' }}>
                "{results.insight}"
              </div>
            </div>
          </div>

          <div style={{ textAlign: 'center', marginTop: '2rem' }}>
            <button className="btn-secondary" onClick={() => setResults(null)}>Analyze Another Resume</button>
          </div>
        </div>
      )}
    </div>
  );
}

function BatchPrediction() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState(null);

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const uploadFile = async () => {
    if (!file) return;
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_BASE}/predict_batch`, {
        method: "POST",
        body: formData
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.detail || "Upload failed");
      setResults(data.results);
    } catch (err) {
      alert("Error processing file: " + err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="glass-container">
      <h2><UploadCloud size={24} color="var(--accent-color)" /> Bulk Assessment</h2>
      <p style={{ marginBottom: '2rem', color: 'var(--text-secondary)' }}>
        Upload a CSV dataset of workforce profiles to predict salaries at scale.
      </p>

      {!results ? (
        <>
          <label className="file-upload">
            <UploadCloud size={48} color={file ? "var(--success-color)" : "var(--accent-color)"} />
            <input type="file" accept=".csv" onChange={handleFileChange} style={{ display: 'none' }} />
            <p>{file ? `Selected: ${file.name}` : "Click or drag to upload CSV"}</p>
          </label>
          <button
            className="btn-primary"
            style={{ marginTop: '2rem' }}
            onClick={uploadFile}
            disabled={!file || uploading}
          >
            {uploading ? <Loader2 className="spin" size={18} /> : 'Process CSV Dataset'}
          </button>
        </>
      ) : (
        <div>
          <div className="status-badge" style={{ marginBottom: '1rem' }}>
            <CheckCircle size={16} /> Processed {results.length} Profiles
          </div>
          <div style={{ overflowX: 'auto', marginTop: '1rem', background: 'rgba(0,0,0,0.2)', borderRadius: '10px' }}>
            <table style={{ minWidth: '100%', borderCollapse: 'collapse', textAlign: 'left' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <th style={{ padding: '1rem' }}>Role</th>
                  <th style={{ padding: '1rem' }}>Experience</th>
                  <th style={{ padding: '1rem' }}>Predicted Salary</th>
                </tr>
              </thead>
              <tbody>
                {results.slice(0, 10).map((r, i) => (
                  <tr key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)' }}>
                    <td style={{ padding: '0.75rem 1rem' }}>{r['Job Role']}</td>
                    <td style={{ padding: '0.75rem 1rem' }}>{r['Years of Experience']} yrs</td>
                    <td style={{ padding: '0.75rem 1rem', color: 'var(--accent-color)', fontWeight: 'bold' }}>{r['Predicted Salary (₹)']}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p style={{ textAlign: 'center', marginTop: '1rem', color: 'var(--text-secondary)' }}>
            Showing top 10 results. Download to view the entire dataset.
          </p>
          <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
            <button className="btn-secondary" onClick={() => setResults(null)}>New Upload</button>
            {/* Note: Real CSV generation requires blob creation in JS, skipped for simplicity, but easily addable */}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
