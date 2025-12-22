import React, { useState } from "react";
import { Line } from "react-chartjs-2";
import { Chart as ChartJS, registerables } from "chart.js";

ChartJS.register(...registerables);

function App() {
  const [sensorData, setSensorData] = useState(null);
  const [productData, setProductData] = useState(null);
  const [potencyData, setPotencyData] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateReport = () => {
    setLoading(true);
    fetch("http://localhost:5001/api/forecast")
      .then((res) => res.json())
      .then((data) => {
        const labels = data.map((d) =>
          new Date(d.timestamp).toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })
        );

        const historyLength = data.filter((d) => d.type === "history").length;

        setSensorData({
          labels,
          datasets: [
            {
              label: "Sensor Temp (Air)",
              data: data.map((d) => d.sensor_temp),
              borderColor: "#FF9800",
              backgroundColor: "rgba(255,152,0,0.1)",
              borderWidth: 2,
              pointRadius: 3,
              segment: {
                borderDash: (ctx) =>
                  ctx.p0DataIndex >= historyLength - 1 ? [6, 6] : undefined,
              },
            },
          ],
        });

        setProductData({
          labels,
          datasets: [
            {
              label: "Product Temp (Actual)",
              data: data.map((d) => d.product_temp),
              borderColor: "#2196F3",
              backgroundColor: "rgba(33,150,243,0.1)",
              borderWidth: 3,
              pointRadius: 4,
              segment: {
                borderDash: (ctx) =>
                  ctx.p0DataIndex >= historyLength - 1 ? [6, 6] : undefined,
              },
            },
            {
              label: "Storage Max (8°C)",
              data: new Array(data.length).fill(8),
              borderColor: "#f44336",
              borderWidth: 2,
              borderDash: [10, 5],
              pointRadius: 0,
            },
          ],
        });

        setPotencyData({
          labels,
          datasets: [
            {
              label: "Potency %",
              data: data.map((d) => d.potency),
              borderColor: "#4CAF50",
              backgroundColor: "rgba(76,175,80,0.1)",
              borderWidth: 2,
              pointRadius: 3,
            },
          ],
        });

        setLoading(false);
      })
      .catch((err) => {
        console.error("Error fetching data:", err);
        setLoading(false);
      });
  };

  const chartOptions = (yLabel = "") => ({
    responsive: true,
    interaction: { mode: "index", intersect: false },
    plugins: {
      legend: { position: "top" },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const val = ctx.parsed.y;
            return yLabel === "%"
              ? `${ctx.dataset.label}: ${val.toFixed(2)}%`
              : `${ctx.dataset.label}: ${val.toFixed(2)}°C`;
          },
        },
      },
    },
    scales: {
      y: {
        title: { display: true, text: yLabel ? `${yLabel}` : "" },
      },
    },
  });

  return (
    <div
      style={{
        padding: 40,
        maxWidth: 1200,
        margin: "0 auto",
        fontFamily: "sans-serif",
        textAlign: "center",
      }}
    >
      <h1>🧊 Cold Chain Monitor</h1>
      <p>Tracking product and sensor temperatures with potency analysis</p>

      <button
        onClick={generateReport}
        style={{
          padding: "12px 20px",
          background: "#2196F3",
          color: "white",
          border: "none",
          borderRadius: 6,
          fontSize: 14,
          cursor: "pointer",
          marginBottom: 30,
        }}
      >
        Generate Investigation Report
      </button>

      {loading && <p>Loading data...</p>}

      {sensorData && (
        <div style={{ margin: "40px 0" }}>
          <h3>Sensor Temperature</h3>
          <Line data={sensorData} options={chartOptions("Temperature (°C)")} />
        </div>
      )}

      {productData && (
        <div style={{ margin: "40px 0" }}>
          <h3>Product Temperature</h3>
          <Line data={productData} options={chartOptions("Temperature (°C)")} />
        </div>
      )}

      {potencyData && (
        <div style={{ margin: "40px 0" }}>
          <h3>Potency</h3>
          <Line data={potencyData} options={chartOptions("%")} />
        </div>
      )}
    </div>
  );
}

export default App;
