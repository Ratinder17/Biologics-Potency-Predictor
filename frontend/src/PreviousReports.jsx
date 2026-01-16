import React, { useEffect, useState } from "react";
import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from "react-router-dom";
import { jsPDF } from "jspdf";

function PreviousReports() {
  const { getAccessTokenSilently } = useAuth0();
  const navigate = useNavigate();
  const [reports, setReports] = useState([]);
  const [loading, setLoading] = useState(true);

  // Styles
  const styles = {
    container: {
      padding: "40px",
      fontFamily: "Inter, sans-serif",
      color: "#333",
      maxWidth: "1200px",
      margin: "0 auto",
    },
    backButton: {
      backgroundColor: "transparent",
      border: "1px solid #e2e8f0",
      padding: "8px 16px",
      borderRadius: "6px",
      cursor: "pointer",
      marginBottom: "20px",
      fontWeight: "600",
      color: "#4a5568",
      transition: "all 0.2s",
    },
    title: {
      marginBottom: "30px",
      fontSize: "24px",
      fontWeight: "700",
      color: "#1a202c",
    },
    table: {
      width: "100%",
      borderCollapse: "collapse",
      backgroundColor: "#fff",
      boxShadow: "0 4px 6px rgba(0,0,0,0.05)",
      borderRadius: "12px",
      overflow: "hidden",
    },
    th: {
      backgroundColor: "#f8fafc",
      color: "#64748b",
      textAlign: "left",
      padding: "16px",
      fontSize: "12px",
      textTransform: "uppercase",
      letterSpacing: "0.05em",
    },
    td: {
      padding: "16px",
      borderBottom: "1px solid #f1f5f9",
      fontSize: "14px",
      color: "#1e293b",
    },
    previewBtn: {
      backgroundColor: "#3182ce",
      color: "white",
      border: "none",
      padding: "8px 14px",
      borderRadius: "6px",
      cursor: "pointer",
      fontWeight: "600",
      fontSize: "12px",
      transition: "background 0.2s",
    },
    idBadge: {
      background: "#f1f5f9",
      padding: "2px 6px",
      borderRadius: "4px",
      fontFamily: "monospace",
      fontSize: "12px",
      color: "#475569",
    },
  };

  useEffect(() => {
    fetchReports();
  }, [getAccessTokenSilently]);

  const fetchReports = async () => {
    try {
      const token = await getAccessTokenSilently({
        authorizationParams: { audience: import.meta.env.VITE_AUTH0_AUDIENCE },
      });
      const res = await fetch("http://127.0.0.1:5001/api/reports", {
        headers: { Authorization: `Bearer ${token}` },
      });
      const data = await res.json();
      setReports(data.reports || []);
    } catch (err) {
      console.error("Fetch error:", err);
    } finally {
      setLoading(false);
    }
  };

  // ---------------- ENHANCED METHOD: FETCH & RENDER PDF ----------------
  const viewReportPDF = async (report_id, investigation_id) => {
    try {
      const token = await getAccessTokenSilently({
        authorizationParams: { audience: import.meta.env.VITE_AUTH0_AUDIENCE },
      });

      // Fetch specific content from your new dedicated endpoint
      const res = await fetch(
        `http://127.0.0.1:5001/api/get_report_content?report_id=${report_id}&investigation_id=${investigation_id}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );

      const data = await res.json();
      if (!data.content) throw new Error("Report content is empty");

      // Generate PDF
      const doc = new jsPDF();
      const margin = 20;
      const pageWidth = 170;
      let y = 20;

      // 1. PDF Header
      doc.setFont("helvetica", "bold");
      doc.setFontSize(18);
      doc.setTextColor(26, 32, 44);
      doc.text("BIOLOGICS INVESTIGATION REPORT", margin, y);

      y += 10;
      doc.setFontSize(10);
      doc.setFont("helvetica", "normal");
      doc.setTextColor(100, 116, 139);
      doc.text(`Report ID: ${report_id}`, margin, y);
      doc.text(`Investigation: ${investigation_id}`, margin + 80, y);
      y += 6;
      doc.text(`Generated: ${new Date().toLocaleString()}`, margin, y);

      y += 6;
      doc.setDrawColor(226, 232, 240);
      doc.line(margin, y, 190, y);
      y += 12;

      // 2. Parse and Render Content
      const lines = data.content.split("\n");

      lines.forEach((line) => {
        const cleanLine = line.trim();

        // Auto-pagination
        if (y > 275) {
          doc.addPage();
          y = 20;
        }

        if (cleanLine.startsWith("###")) {
          // Render Headers (e.g., ### 1. EXECUTIVE SUMMARY)
          y += 4;
          doc.setFont("helvetica", "bold");
          doc.setFontSize(12);
          doc.setTextColor(49, 130, 206); // Blue header color
          doc.text(cleanLine.replace("###", "").trim(), margin, y);
          y += 8;
        } else if (cleanLine === "---") {
          // Render Horizontal Rules
          y += 2;
          doc.setDrawColor(226, 232, 240);
          doc.line(margin, y, 190, y);
          y += 8;
        } else if (cleanLine !== "") {
          // Render Standard Text
          doc.setFont("helvetica", "normal");
          doc.setFontSize(10);
          doc.setTextColor(30, 41, 59);
          const splitText = doc.splitTextToSize(cleanLine, pageWidth);
          doc.text(splitText, margin, y);
          y += splitText.length * 5 + 4; // Dynamic spacing based on text wrap
        } else {
          y += 2; // Extra space for empty lines
        }
      });

      // 3. Open in Browser Tab
      const pdfUrl = doc.output("bloburl");
      window.open(pdfUrl, "_blank");
    } catch (err) {
      console.error("PDF Error:", err);
      alert("Error generating PDF preview. Please check your connection.");
    }
  };

  if (loading)
    return (
      <div style={{ padding: "100px", textAlign: "center", color: "#64748b" }}>
        Loading report history...
      </div>
    );

  return (
    <div style={styles.container}>
      <button
        onClick={() => navigate("/")}
        style={styles.backButton}
        onMouseOver={(e) => (e.target.style.backgroundColor = "#f8fafc")}
        onMouseOut={(e) => (e.target.style.backgroundColor = "transparent")}
      >
        ← Back to Dashboard
      </button>

      <h2 style={styles.title}>Investigation History</h2>

      {reports.length === 0 ? (
        <div
          style={{
            padding: "40px",
            textAlign: "center",
            border: "1px dashed #cbd5e0",
            borderRadius: "8px",
            color: "#718096",
          }}
        >
          No previous reports found.
        </div>
      ) : (
        <table style={styles.table}>
          <thead>
            <tr>
              <th style={styles.th}>Report ID</th>
              <th style={styles.th}>Investigation ID</th>
              <th style={styles.th}>Date Created</th>
              <th style={styles.th}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {reports.map((r) => (
              <tr key={r.report_id}>
                <td style={styles.td}>
                  <strong>{r.report_id}</strong>
                </td>
                <td style={styles.td}>
                  <span style={styles.idBadge}>{r.investigation_id}</span>
                </td>
                <td style={styles.td}>
                  {new Date(r.created_at).toLocaleDateString(undefined, {
                    year: "numeric",
                    month: "short",
                    day: "numeric",
                  })}
                </td>
                <td style={styles.td}>
                  <button
                    style={styles.previewBtn}
                    onClick={() =>
                      viewReportPDF(r.report_id, r.investigation_id)
                    }
                    onMouseOver={(e) =>
                      (e.target.style.backgroundColor = "#2b6cb0")
                    }
                    onMouseOut={(e) =>
                      (e.target.style.backgroundColor = "#3182ce")
                    }
                  >
                    View PDF Preview
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}

export default PreviousReports;
