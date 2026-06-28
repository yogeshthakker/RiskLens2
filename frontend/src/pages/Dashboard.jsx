import { useState } from "react";
import SearchBar   from "../components/SearchBar";
import RiskScore   from "../components/RiskScore";
import GraphView   from "../components/GraphView";
import ReportView  from "../components/ReportView";
import { getRisk, getGraph, generateReport } from "../services/api";

export default function Dashboard() {
  const [riskData,   setRiskData]   = useState(null);
  const [graphData,  setGraphData]  = useState(null);
  const [report,     setReport]     = useState(null);
  const [loading,    setLoading]    = useState(false);
  const [reporting,  setReporting]  = useState(false);
  const [accountId,  setAccountId]  = useState("");
  const [error,      setError]      = useState("");

  async function handleSearch(id) {
    if (!id.trim()) return;
    setAccountId(id);
    setLoading(true);
    setError("");
    setReport(null);

    try {
      const [risk, graph] = await Promise.all([
        getRisk(id),
        getGraph(id)
      ]);
      setRiskData(risk.data);
      setGraphData(graph.data);
    } catch (e) {
      setError("Account not found or backend error. Check the account ID.");
    } finally {
      setLoading(false);
    }
  }

  async function handleReport() {
    setReporting(true);
    setReport(null);
    try {
      const res = await generateReport(accountId);
      setReport(res.data.report);
    } catch (e) {
      setError("Report generation failed.");
    } finally {
      setReporting(false);
    }
  }

  return (
    <div style={styles.page}>

      {/* header */}
      <div style={styles.header}>
        <div>
          <h1 style={styles.logo}>RiskLens</h1>
          <p style={styles.sub}>AI Copilot for Banking Risk Investigation</p>
        </div>
        <span style={styles.badge}>Deutsche Bank — Prototype</span>
      </div>

      <div style={styles.body}>

        {/* search */}
        <SearchBar onSearch={handleSearch} loading={loading}/>

        {error && <p style={styles.error}>{error}</p>}

        {loading && <p style={styles.loading}>Loading risk data...</p>}

        {/* results grid */}
        {riskData && !loading && (
          <>
            <div style={styles.grid}>
              <RiskScore data={riskData}/>
              <GraphView data={graphData}/>
            </div>

            {/* generate report button */}
            {!report && !reporting && (
              <button style={styles.reportBtn} onClick={handleReport}>
                Generate Investigation Report
              </button>
            )}

            <ReportView report={report} loading={reporting}/>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  page      : { minHeight: "100vh", background: "#f1f5f9", fontFamily: "system-ui, sans-serif" },
  header    : { background: "#1e293b", padding: "20px 40px", display: "flex", alignItems: "center", justifyContent: "space-between" },
  logo      : { color: "#fff", fontSize: "22px", fontWeight: "700", margin: 0 },
  sub       : { color: "#94a3b8", fontSize: "13px", margin: "4px 0 0" },
  badge     : { background: "#1e40af", color: "#fff", padding: "6px 14px", borderRadius: "6px", fontSize: "12px", fontWeight: "600" },
  body      : { maxWidth: "1100px", margin: "0 auto", padding: "40px 24px" },
  grid      : { display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px", marginBottom: "20px" },
  reportBtn : { width: "100%", padding: "14px", background: "#1e40af", color: "#fff", border: "none", borderRadius: "8px", fontSize: "15px", fontWeight: "600", cursor: "pointer", marginBottom: "20px" },
  error     : { color: "#dc2626", fontSize: "14px", marginBottom: "16px" },
  loading   : { color: "#64748b", fontSize: "14px" }
};