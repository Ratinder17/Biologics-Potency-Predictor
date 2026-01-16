import React, { useState, useEffect } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, registerables } from "chart.js";
import annotationPlugin from "chartjs-plugin-annotation";
import { useAuth0 } from "@auth0/auth0-react";
import { useNavigate } from "react-router-dom";
import ReactMarkdown from "react-markdown";

ChartJS.register(...registerables, annotationPlugin);

function App() {
  const navigate = useNavigate();

  // ---------------- AUTH ----------------
  const {
    loginWithRedirect,
    logout,
    isAuthenticated,
    user,
    isLoading,
    getAccessTokenSilently,
  } = useAuth0();

  // ---------------- STATE ----------------
  const [sensorData, setSensorData] = useState(null);
  const [productData, setProductData] = useState(null);
  const [potencyData, setPotencyData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [reportLoading, setReportLoading] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [timeColumn, setTimeColumn] = useState("");
  const [tempColumn, setTempColumn] = useState("");
  const [tempUnit, setTempUnit] = useState("C");
  const [stabilityProfiles, setStabilityProfiles] = useState([]);
  const [stabilityProfilesData, setStabilityProfilesData] = useState({});
  const [selectedProfile, setSelectedProfile] = useState("");
  const [storageMin, setStorageMin] = useState(null);
  const [storageMax, setStorageMax] = useState(null);
  const [currentInvestigationId, setCurrentInvestigationId] = useState(null);
  const [aiReport, setAiReport] = useState("");
  const [ttsLoading, setTtsLoading] = useState(false);
  const [ttsAudioUrl, setTtsAudioUrl] = useState(null);

  // ---------------- MODERN STYLES ----------------
  const styles = {
    container: {
      padding: "40px",
      maxWidth: "900px",
      margin: "0 auto",
      fontFamily: "Inter, sans-serif",
      color: "#333",
      backgroundColor: "#fff",
    },
    header: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      marginBottom: "40px",
    },
    title: {
      fontSize: "28px",
      fontWeight: "700",
      color: "#1a202c",
      margin: "0 0 10px 0",
    },
    subtitle: { color: "#718096", marginBottom: "30px" },
    card: {
      background: "#ffffff",
      padding: "24px",
      borderRadius: "12px",
      boxShadow: "0 4px 6px rgba(0,0,0,0.05)",
      border: "1px solid #e2e8f0",
      marginBottom: "20px",
      textAlign: "left",
    },
    input: {
      width: "100%",
      padding: "12px",
      marginBottom: "15px",
      borderRadius: "6px",
      border: "1px solid #cbd5e0",
      fontSize: "14px",
      boxSizing: "border-box",
    },
    primaryBtn: {
      backgroundColor: "#2b6cb0",
      color: "white",
      padding: "14px 24px",
      border: "none",
      borderRadius: "8px",
      fontWeight: "600",
      cursor: "pointer",
      width: "100%",
      transition: "background 0.2s",
    },
    secondaryBtn: {
      backgroundColor: "#edf2f7",
      color: "#4a5568",
      padding: "8px 16px",
      border: "1px solid #e2e8f0",
      borderRadius: "6px",
      fontWeight: "600",
      cursor: "pointer",
    },
    navBtn: {
      backgroundColor: "#FF9800",
      color: "white",
      padding: "8px 16px",
      border: "none",
      borderRadius: "6px",
      cursor: "pointer",
      fontWeight: "600",
    },
    statsLabel: {
      marginTop: "12px",
      fontSize: "13px",
      color: "#4a5568",
      fontWeight: "500",
      textAlign: "center",
    },
    chartTitle: {
      fontSize: "18px",
      color: "#2d3748",
      marginTop: "10px",
      marginBottom: "10px",
      fontWeight: "600",
    },
    reportBox: {
      marginTop: "30px",
      padding: "30px",
      backgroundColor: "#fdfdfd",
      borderRadius: "12px",
      border: "1px solid #e2e8f0",
      textAlign: "left",
      boxShadow: "inset 0 2px 4px rgba(0,0,0,0.02)",
    },
  };

  // ---------------- EFFECTS ----------------
  useEffect(() => {
    fetch("http://127.0.0.1:5001/api/stability_profiles")
      .then((res) => res.json())
      .then((data) => {
        const keys = Object.keys(data.profiles);
        setStabilityProfiles(keys);
        setStabilityProfilesData(data.profiles);
        if (keys.length > 0) {
          const firstProfile = keys[0];
          setSelectedProfile(firstProfile);
          setStorageMin(data.profiles[firstProfile].storage_min);
          setStorageMax(data.profiles[firstProfile].storage_max);
        }
      })
      .catch((err) => console.error("Error fetching stability profiles:", err));
  }, []);

  // ---------------- HELPERS ----------------
  function calculateStats(dataArray) {
    if (!dataArray || dataArray.length === 0) return null;
    const numbers = dataArray.map(Number);
    return {
      max: Math.max(...numbers).toFixed(2),
      min: Math.min(...numbers).toFixed(2),
      mean: (numbers.reduce((a, b) => a + b, 0) / numbers.length).toFixed(2),
    };
  }

  const chartOptions = (
    yLabel,
    maxLimit,
    minLimit,
    maxRecorded,
    minRecorded,
    potencyEnd = null
  ) => ({
    responsive: true,
    scales: { y: { title: { display: true, text: yLabel } } },
    plugins: {
      annotation: {
        annotations: {
          // RED LINES: Allowed Range
          ...(maxLimit !== null && {
            maxLimitLine: {
              type: "line",
              yMin: maxLimit,
              yMax: maxLimit,
              borderColor: "red",
              borderWidth: 2,
              label: {
                content: "Max Limit",
                enabled: true,
                position: "end",
                color: "red",
              },
            },
          }),
          ...(minLimit !== null && {
            minLimitLine: {
              type: "line",
              yMin: minLimit,
              yMax: minLimit,
              borderColor: "red",
              borderWidth: 2,
              label: { content: "Min Limit", enabled: true, position: "end" },
            },
          }),

          // GREEN LINES: Recorded Excursion Extremes
          ...(maxRecorded !== null && {
            maxRecordedLine: {
              type: "line",
              yMin: maxRecorded,
              yMax: maxRecorded,
              borderColor: "green",
              borderWidth: 2,
              label: {
                content: "Max Recorded",
                enabled: true,
                position: "start",
              },
            },
          }),
          ...(minRecorded !== null && {
            minRecordedLine: {
              type: "line",
              yMin: minRecorded,
              yMax: minRecorded,
              borderColor: "green",
              borderWidth: 2,
              label: {
                content: "Min Recorded",
                enabled: true,
                position: "start",
              },
            },
          }),

          // BLUE LINE: Potency Baseline and Final
          ...(potencyEnd !== null && {
            potencyLine: {
              type: "line",
              yMin: potencyEnd,
              yMax: potencyEnd,
              borderColor: "blue",
              borderWidth: 2,
              label: {
                content: "Final Potency",
                enabled: true,
                position: "end",
              },
            },
            baseline100: {
              type: "line",
              yMin: 100,
              yMax: 100,
              borderColor: "#cbd5e0",
              borderWidth: 1,
              borderDash: [5, 5],
              label: { content: "100%", enabled: true, position: "end" },
            },
          }),
        },
      },
    },
  });

  // ---------------- HANDLERS ----------------
  const generateReport = async () => {
    if (!csvFile || !timeColumn || !tempColumn || !selectedProfile) {
      alert("All fields are required.");
      return;
    }
    setLoading(true);
    try {
      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: import.meta.env.VITE_AUTH0_AUDIENCE,
          scope: "openid profile email",
          prompt: "consent",
        },
      });

      const formData = new FormData();
      formData.append("file", csvFile);
      formData.append("time_column", timeColumn);
      formData.append("temperature_column", tempColumn);
      formData.append("temperature_unit", tempUnit);
      formData.append("stability_profile", selectedProfile);

      const res = await fetch("http://127.0.0.1:5001/api/forecast", {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      const data = await res.json();
      if (!data.results) throw new Error("No results returned");

      setCurrentInvestigationId(data.investigation_id);
      const labels = data.results.map((d) =>
        new Date(d.timestamp).toLocaleTimeString([], {
          hour: "2-digit",
          minute: "2-digit",
        })
      );
      const sensorTemps = data.results.map((d) => d.sensor_temp);
      const productTemps = data.results.map((d) => d.product_temp);
      const potencies = data.results.map((d) => d.potency);

      setSensorData({
        labels,
        datasets: [
          {
            label: "Sensor Temp",
            data: sensorTemps,
            borderColor: "#3182ce",
            backgroundColor: "rgba(49, 130, 206, 0.1)",
            fill: true,
          },
        ],
        options: chartOptions(
          "°C",
          storageMax,
          storageMin,
          Math.max(...sensorTemps),
          Math.min(...sensorTemps)
        ),
      });

      setProductData({
        labels,
        datasets: [
          { label: "Product Temp", data: productTemps, borderColor: "#2b6cb0" },
        ],
        options: chartOptions(
          "°C",
          storageMax,
          storageMin,
          Math.max(...productTemps),
          Math.min(...productTemps)
        ),
      });

      setPotencyData({
        labels,
        datasets: [
          { label: "Potency %", data: potencies, borderColor: "#38a169" },
        ],
        options: chartOptions(
          "%",
          null,
          null,
          null,
          null,
          potencies.slice(-1)[0]
        ),
      });
    } catch (err) {
      console.error(err);
      if (err.error === "consent_required" || err.error === "login_required") {
        loginWithRedirect({
          authorizationParams: {
            prompt: "consent",
            audience: import.meta.env.VITE_AUTH0_AUDIENCE,
          },
        });
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchAIReport = async () => {
    setReportLoading(true);
    try {
      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: import.meta.env.VITE_AUTH0_AUDIENCE,
          prompt: "consent",
        },
      });
      const res = await fetch(
        `http://127.0.0.1:5001/api/investigation_report/${currentInvestigationId}`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const data = await res.json();
      setAiReport(data.report || data.error);
    } catch (err) {
      console.error(err);
    } finally {
      setReportLoading(false);
    }
  };

  const generateTTS = async () => {
    setTtsLoading(true);
    try {
      const token = await getAccessTokenSilently({
        authorizationParams: {
          audience: import.meta.env.VITE_AUTH0_AUDIENCE,
          prompt: "consent",
        },
      });
      const res = await fetch("http://127.0.0.1:5001/api/tts-report", {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ investigation_id: currentInvestigationId }),
      });
      const audioBlob = await res.blob();
      setTtsAudioUrl(URL.createObjectURL(audioBlob));
    } catch (err) {
      alert("Failed to generate audio.");
    } finally {
      setTtsLoading(false);
    }
  };

  // ---------------- RENDER ----------------
  return (
    <div style={styles.container}>
      {!isLoading && (
        <div style={styles.header}>
          <button
            onClick={() => navigate("/previous-reports")}
            style={styles.navBtn}
          >
            Previous Reports
          </button>
          <div style={{ display: "flex", gap: 12, alignItems: "center" }}>
            {!isAuthenticated ? (
              <button
                onClick={() => loginWithRedirect()}
                style={styles.primaryBtn}
              >
                Log in
              </button>
            ) : (
              <>
                <span style={{ fontSize: "14px", fontWeight: "600" }}>
                  {user?.email}
                </span>
                <button onClick={() => logout()} style={styles.secondaryBtn}>
                  Log out
                </button>
              </>
            )}
          </div>
        </div>
      )}

      <h1 style={styles.title}>AEGIS</h1>

      {/* Input Card */}
      <div style={styles.card}>
        <label
          style={{
            display: "block",
            fontSize: "13px",
            marginBottom: "5px",
            fontWeight: "600",
          }}
        >
          Upload Data
        </label>
        <input
          type="file"
          onChange={(e) => setCsvFile(e.target.files[0])}
          style={styles.input}
        />
        <div style={{ display: "flex", gap: "15px" }}>
          <input
            placeholder="Time column"
            value={timeColumn}
            onChange={(e) => setTimeColumn(e.target.value)}
            style={styles.input}
          />
          <input
            placeholder="Temperature column"
            value={tempColumn}
            onChange={(e) => setTempColumn(e.target.value)}
            style={styles.input}
          />
        </div>
        <div style={{ display: "flex", gap: "15px" }}>
          <select
            value={tempUnit}
            onChange={(e) => setTempUnit(e.target.value)}
            style={styles.input}
          >
            <option value="C">Celsius (°C)</option>
            <option value="F">Fahrenheit (°F)</option>
          </select>
          <select
            value={selectedProfile}
            onChange={(e) => {
              const p = e.target.value;
              setSelectedProfile(p);
              setStorageMin(stabilityProfilesData[p].storage_min);
              setStorageMax(stabilityProfilesData[p].storage_max);
            }}
            style={styles.input}
          >
            {stabilityProfiles.map((p) => (
              <option key={p} value={p}>
                {p}
              </option>
            ))}
          </select>
        </div>
        <button onClick={generateReport} style={styles.primaryBtn}>
          {loading ? "Processing..." : "Generate Investigation Report"}
        </button>
      </div>

      {/* Sensor Chart */}
      {sensorData && (
        <div style={styles.card}>
          <h3 style={styles.chartTitle}>Sensor Temperature</h3>
          <Line data={sensorData} options={sensorData.options} />
          {(() => {
            const stats = calculateStats(sensorData.datasets[0].data);
            return (
              stats && (
                <div style={styles.statsLabel}>
                  Max: {stats.max}°C | Min: {stats.min}°C | Mean: {stats.mean}°C
                </div>
              )
            );
          })()}
        </div>
      )}

      {/* Product Chart */}
      {productData && (
        <div style={styles.card}>
          <h3 style={styles.chartTitle}>Product Temperature</h3>
          <Line data={productData} options={productData.options} />
          {(() => {
            const stats = calculateStats(productData.datasets[0].data);
            return (
              stats && (
                <div style={styles.statsLabel}>
                  Max: {stats.max}°C | Min: {stats.min}°C | Mean: {stats.mean}°C
                </div>
              )
            );
          })()}
        </div>
      )}

      {/* Potency Chart */}
      {potencyData && (
        <div style={styles.card}>
          <h3 style={styles.chartTitle}>Potency Projection</h3>
          <Line data={potencyData} options={potencyData.options} />
          {(() => {
            const lastPotency = potencyData.datasets[0].data.slice(-1)[0];
            return (
              <div
                style={{
                  ...styles.statsLabel,
                  color: "#2f855a",
                  fontSize: "16px",
                }}
              >
                Potency Remaining: {lastPotency.toFixed(2)}%
              </div>
            );
          })()}
        </div>
      )}

      {/* AI Report Logic */}
      {isAuthenticated && currentInvestigationId && !aiReport && (
        <button
          onClick={fetchAIReport}
          style={{
            ...styles.primaryBtn,
            backgroundColor: "#38a169",
            marginTop: "20px",
          }}
        >
          {reportLoading
            ? "Generating Analysis..."
            : "Generate Detailed AI Report"}
        </button>
      )}

      {aiReport && (
        <div style={styles.reportBox}>
          <div
            style={{
              display: "flex",
              justifyContent: "space-between",
              borderBottom: "1px solid #eee",
              paddingBottom: "10px",
              marginBottom: "20px",
            }}
          >
            <h3 style={{ margin: 0 }}>Detailed Investigation Report</h3>
            <button
              onClick={generateTTS}
              disabled={ttsLoading}
              style={{
                ...styles.secondaryBtn,
                backgroundColor: "#6b46c1",
                color: "white",
                border: "none",
              }}
            >
              {ttsLoading ? "..." : "Play Audio"}
            </button>
          </div>
          <div
            style={{ fontSize: "15px", color: "#4a5568", lineHeight: "1.7" }}
          >
            <ReactMarkdown
              components={{
                h3: ({ node, ...props }) => (
                  <h3
                    style={{
                      color: "#2d3748",
                      marginTop: "24px",
                      borderBottom: "1px solid #f0f0f0",
                    }}
                    {...props}
                  />
                ),
                p: ({ node, ...props }) => (
                  <p style={{ marginBottom: "14px" }} {...props} />
                ),
                li: ({ node, ...props }) => (
                  <li style={{ marginBottom: "8px" }} {...props} />
                ),
              }}
            >
              {aiReport}
            </ReactMarkdown>
          </div>
          {ttsAudioUrl && (
            <audio
              controls
              src={ttsAudioUrl}
              style={{ width: "100%", marginTop: "20px" }}
            />
          )}
        </div>
      )}
    </div>
  );
}

export default App;
