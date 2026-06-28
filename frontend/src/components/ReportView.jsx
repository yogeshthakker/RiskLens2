export default function ReportView({ report, loading }) {
  if (loading) return (
    <div style={styles.card}>
      <div style={styles.loading}>
        Generating investigation report — this takes 10 to 20 seconds...
      </div>
    </div>
  );

  if (!report) return null;

  const lines = report.split("\n");

  return (
    <div style={styles.card}>
      <h2 style={styles.title}>Investigation Report</h2>
      <div style={styles.report}>
        {lines.map((line, i) => {
          if (line.startsWith("─") || line.startsWith("---"))
            return <hr key={i} style={styles.divider}/>;
          if (line.startsWith("INVESTIGATION") || line.startsWith("OBSERVATIONS") ||
              line.startsWith("CONNECTED")     || line.startsWith("RECOMMENDATION"))
            return <p key={i} style={styles.section}>{line}</p>;
          if (line.startsWith("Entity") || line.startsWith("Account") || line.startsWith("Risk Score"))
            return <p key={i} style={styles.meta}>{line}</p>;
          if (line.startsWith("•") || line.startsWith("-"))
            return <p key={i} style={styles.bullet}>{line}</p>;
          if (line.trim() === "")
            return <div key={i} style={{ height: "8px" }}/>;
          return <p key={i} style={styles.text}>{line}</p>;
        })}
      </div>
    </div>
  );
}

const styles = {
  card    : { background: "#fff", borderRadius: "12px", padding: "24px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)" },
  title   : { fontSize: "16px", fontWeight: "600", color: "#1e293b", marginBottom: "20px" },
  report  : { fontFamily: "monospace", fontSize: "13px", lineHeight: "1.8" },
  section : { fontWeight: "700", color: "#1e40af", marginTop: "16px", marginBottom: "4px", letterSpacing: "0.05em" },
  meta    : { color: "#334155", margin: "2px 0" },
  bullet  : { color: "#475569", paddingLeft: "8px", margin: "4px 0" },
  text    : { color: "#475569", margin: "2px 0" },
  divider : { border: "none", borderTop: "1px solid #e2e8f0", margin: "12px 0" },
  loading : { color: "#64748b", fontSize: "14px", padding: "40px 0", textAlign: "center" }
};