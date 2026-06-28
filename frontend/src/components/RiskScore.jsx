export default function RiskScore({ data }) {
  if (!data) return null;

  const color = data.risk_level === "High"   ? "#dc2626"
              : data.risk_level === "Medium" ? "#d97706"
              : "#16a34a";

  return (
    <div style={styles.card}>
      <h2 style={styles.title}>Risk Score</h2>

      <div style={styles.scoreRow}>
        <span style={{ ...styles.score, color }}>{data.risk_score}</span>
        <span style={styles.outof}>/100</span>
        <span style={{ ...styles.badge, background: color }}>
          {data.risk_level}
        </span>
      </div>

      <div style={styles.bar}>
        <div style={{
          ...styles.fill,
          width     : `${data.risk_score}%`,
          background: color
        }}/>
      </div>

      {data.risk_factors && data.risk_factors.length > 0 && (
        <div style={styles.section}>
          <p style={styles.label}>What is pushing risk up</p>
          {data.risk_factors.map((r, i) => (
            <div key={i} style={styles.reason}>
              <span style={styles.dot}>▲</span>
              {r.feature} = {r.value} (impact {r.impact})
            </div>
          ))}
        </div>
      )}

      {data.protective_factors && data.protective_factors.length > 0 && (
        <div style={styles.section}>
          <p style={styles.label}>What is reducing risk</p>
          {data.protective_factors.map((r, i) => (
            <div key={i} style={styles.reason}>
              <span style={{ ...styles.dot, color: "#16a34a" }}>▼</span>
              {r.feature} = {r.value} (impact {r.impact})
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

const styles = {
  card      : { background: "#fff", borderRadius: "12px", padding: "24px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)", marginBottom: "20px" },
  title     : { fontSize: "16px", fontWeight: "600", color: "#1e293b", marginBottom: "16px" },
  scoreRow  : { display: "flex", alignItems: "baseline", gap: "8px", marginBottom: "12px" },
  score     : { fontSize: "52px", fontWeight: "700" },
  outof     : { fontSize: "20px", color: "#94a3b8" },
  badge     : { marginLeft: "12px", padding: "4px 12px", borderRadius: "20px", color: "#fff", fontSize: "13px", fontWeight: "600" },
  bar       : { height: "8px", background: "#f1f5f9", borderRadius: "4px", marginBottom: "20px" },
  fill      : { height: "8px", borderRadius: "4px", transition: "width 0.6s ease" },
  section   : { marginTop: "16px" },
  label     : { fontSize: "12px", fontWeight: "600", color: "#64748b", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "8px" },
  reason    : { fontSize: "13px", color: "#334155", padding: "6px 0", borderBottom: "1px solid #f1f5f9" },
  dot       : { color: "#dc2626", marginRight: "8px" }
};