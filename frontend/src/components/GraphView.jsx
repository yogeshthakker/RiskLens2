export default function GraphView({ data }) {
  if (!data) return null;

  const grouped = {};
  (data.connections || []).forEach(c => {
    const type = (c.type || ["Unknown"])[0];
    if (!grouped[type]) grouped[type] = [];
    grouped[type].push(c);
  });

  const colors = {
    Customer : "#3b82f6",
    Company  : "#8b5cf6",
    Account  : "#0891b2",
    Alert    : "#dc2626",
    Unknown  : "#94a3b8"
  };

  return (
    <div style={styles.card}>
      <h2 style={styles.title}>
        Connected Entities
        <span style={styles.count}>{data.total_found} found</span>
      </h2>

      {Object.keys(grouped).map(type => (
        <div key={type} style={styles.group}>
          <p style={{ ...styles.groupLabel, color: colors[type] || "#94a3b8" }}>
            {type}s ({grouped[type].length})
          </p>
          <div style={styles.chips}>
            {grouped[type].map((c, i) => (
              <span key={i} style={{
                ...styles.chip,
                borderColor : colors[type] || "#94a3b8",
                color       : colors[type] || "#94a3b8"
              }}>
                {c.name || c.account_id || c.company_id || c.customer_id || "—"}
              </span>
            ))}
          </div>
        </div>
      ))}

      {data.total_found === 0 && (
        <p style={styles.empty}>No connections found</p>
      )}
    </div>
  );
}

const styles = {
  card       : { background: "#fff", borderRadius: "12px", padding: "24px", boxShadow: "0 1px 4px rgba(0,0,0,0.08)", marginBottom: "20px" },
  title      : { fontSize: "16px", fontWeight: "600", color: "#1e293b", marginBottom: "16px", display: "flex", alignItems: "center", gap: "12px" },
  count      : { fontSize: "13px", fontWeight: "400", background: "#f1f5f9", padding: "2px 10px", borderRadius: "20px", color: "#64748b" },
  group      : { marginBottom: "16px" },
  groupLabel : { fontSize: "12px", fontWeight: "600", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "8px" },
  chips      : { display: "flex", flexWrap: "wrap", gap: "8px" },
  chip       : { fontSize: "12px", padding: "4px 12px", borderRadius: "20px", border: "1px solid", background: "#f8fafc" },
  empty      : { color: "#94a3b8", fontSize: "14px" }
};