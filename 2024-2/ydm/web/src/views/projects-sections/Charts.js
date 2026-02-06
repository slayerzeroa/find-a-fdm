import React, { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

function Charts() {
  const [activeTab, setActiveTab] = useState("KOSPI"); // "KOSPI" | "KOSDAQ"

  const [kospiData, setKospiData] = useState([]);
  const [kosdaqData, setKosdaqData] = useState([]);

  // 요청별 에러 분리
  const [errors, setErrors] = useState({
    kospi: null,
    kosdaq: null,
  });

  // KOSPI 라인 on/off
  const [showVKOSPI, setShowVKOSPI] = useState(true);
  const [showWVKOSPI, setShowWVKOSPI] = useState(true);

  // KOSDAQ 라인 on/off
  const [showVKOSDAQ, setShowVKOSDAQ] = useState(true);
  const [showWVKOSDAQ, setShowWVKOSDAQ] = useState(true);

  // 기간
  const [period, setPeriod] = useState("6M"); // "1M" | "3M" | "6M" | "1Y" | "ALL" | "CUSTOM"
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

  const formatYYYYMMDD = (v) => {
    const s = String(v ?? "");
    if (s.length !== 8) return s;
    return `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}`;
  };

  const toDate = (yyyyMmDd) => new Date(`${yyyyMmDd}T00:00:00`);

  // 숫자 안전 변환
  const n = (x) => {
    const v = Number(x);
    return Number.isFinite(v) ? v : null;
  };

  useEffect(() => {
    let mounted = true;

    const fetchData = async () => {
      const [resKospi, resKosdaq] = await Promise.allSettled([
        axios.get("http://slayerzeroa.iptime.org:8001/vkospi"),
        axios.get("http://slayerzeroa.iptime.org:8001/vkosdaq"),
      ]);

      if (!mounted) return;

      // KOSPI 처리
      if (resKospi.status === "fulfilled") {
        const p = (resKospi.value.data || [])
          .map((item) => ({
            DATE: formatYYYYMMDD(item.BAS_DD ?? item.DATE),
            VKOSPI: n(item.VKOSPI),
            WVKOSPI: n(item.WVKOSPI),
          }))
          .filter((d) => d.DATE && !Number.isNaN(toDate(d.DATE).getTime()))
          .sort((a, b) => a.DATE.localeCompare(b.DATE));

        setKospiData(p);
        setErrors((prev) => ({ ...prev, kospi: null }));
      } else {
        console.error("KOSPI 데이터 오류:", resKospi.reason);
        setKospiData([]); // 실패해도 다른 탭 영향 없음
        setErrors((prev) => ({ ...prev, kospi: "VKOSPI API 호출 실패" }));
      }

      // KOSDAQ 처리
      if (resKosdaq.status === "fulfilled") {
        const q = (resKosdaq.value.data || [])
          .map((item) => ({
            DATE: formatYYYYMMDD(item.BAS_DD ?? item.DATE),
            VKOSDAQ: n(item.VKOSDAQ),
            WVKOSDAQ: n(item.WVKOSDAQ),
          }))
          .filter((d) => d.DATE && !Number.isNaN(toDate(d.DATE).getTime()))
          .sort((a, b) => a.DATE.localeCompare(b.DATE));

        setKosdaqData(q);
        setErrors((prev) => ({ ...prev, kosdaq: null }));
      } else {
        console.error("KOSDAQ 데이터 오류:", resKosdaq.reason);
        setKosdaqData([]);
        setErrors((prev) => ({ ...prev, kosdaq: "VKOSDAQ API 호출 실패" }));
      }

      // 날짜 초기값: 있는 데이터 우선 세팅
      const pData =
        resKospi.status === "fulfilled"
          ? (resKospi.value.data || [])
              .map((item) => ({
                DATE: formatYYYYMMDD(item.BAS_DD ?? item.DATE),
              }))
              .filter((d) => d.DATE && !Number.isNaN(toDate(d.DATE).getTime()))
              .sort((a, b) => a.DATE.localeCompare(b.DATE))
          : [];

      const qData =
        resKosdaq.status === "fulfilled"
          ? (resKosdaq.value.data || [])
              .map((item) => ({
                DATE: formatYYYYMMDD(item.BAS_DD ?? item.DATE),
              }))
              .filter((d) => d.DATE && !Number.isNaN(toDate(d.DATE).getTime()))
              .sort((a, b) => a.DATE.localeCompare(b.DATE))
          : [];

      const seed = pData.length ? pData : qData;
      if (seed.length) {
        setStartDate(seed[0].DATE);
        setEndDate(seed[seed.length - 1].DATE);
      }
    };

    fetchData();

    return () => {
      mounted = false;
    };
  }, []);

  const activeData = activeTab === "KOSPI" ? kospiData : kosdaqData;
  const activeError = activeTab === "KOSPI" ? errors.kospi : errors.kosdaq;

  const filteredData = useMemo(() => {
    if (!activeData.length) return [];

    if (period === "CUSTOM") {
      if (!startDate || !endDate) return activeData;
      const s = toDate(startDate);
      const e = toDate(endDate);
      return activeData.filter((d) => {
        const t = toDate(d.DATE);
        return t >= s && t <= e;
      });
    }

    if (period === "ALL") return activeData;

    const lastDate = toDate(activeData[activeData.length - 1].DATE);
    const start = new Date(lastDate);

    if (period === "1M") start.setMonth(start.getMonth() - 1);
    if (period === "3M") start.setMonth(start.getMonth() - 3);
    if (period === "6M") start.setMonth(start.getMonth() - 6);
    if (period === "1Y") start.setFullYear(start.getFullYear() - 1);

    return activeData.filter((d) => {
      const t = toDate(d.DATE);
      return t >= start && t <= lastDate;
    });
  }, [activeData, period, startDate, endDate]);

  const tabBtnStyle = (active) => ({
    padding: "7px 12px",
    borderRadius: "8px",
    border: "1px solid #cfd8dc",
    cursor: "pointer",
    background: active ? "#2c3e50" : "#fff",
    color: active ? "#fff" : "#2c3e50",
    fontSize: "13px",
    fontWeight: 700,
  });

  const toggleBtnStyle = (active) => ({
    padding: "6px 12px",
    borderRadius: "6px",
    border: "none",
    cursor: "pointer",
    color: "#fff",
    backgroundColor: active ? "#34495e" : "#95a5a6",
    fontSize: "13px",
  });

  const periodBtnStyle = (active) => ({
    padding: "6px 10px",
    borderRadius: "6px",
    border: "1px solid #cfd8dc",
    cursor: "pointer",
    background: active ? "#34495e" : "#fff",
    color: active ? "#fff" : "#2c3e50",
    fontSize: "12px",
  });

  return (
    <div style={{ width: "100%", padding: "12px" }}>
      <div
        style={{
          width: "min(100%, 1000px)",
          margin: "0 auto",
          border: "1px solid #e5e7eb",
          borderRadius: "10px",
          padding: "16px 18px",
          background: "#fff",
        }}
      >
        <h2
          style={{
            margin: "0 0 12px 0",
            fontFamily: "'Noto Sans', sans-serif",
            fontWeight: 700,
            color: "#2c3e50",
            fontSize: "18px",
          }}
        >
          VOLATILITY DASHBOARD
        </h2>

        {/* 상단 그룹 탭 */}
        <div style={{ display: "flex", gap: "8px", marginBottom: "12px" }}>
          <button
            style={tabBtnStyle(activeTab === "KOSPI")}
            onClick={() => setActiveTab("KOSPI")}
          >
            KOSPI (VKOSPI / WVKOSPI)
          </button>
          <button
            style={tabBtnStyle(activeTab === "KOSDAQ")}
            onClick={() => setActiveTab("KOSDAQ")}
          >
            KOSDAQ (VKOSDAQ / WVKOSDAQ)
          </button>
        </div>

        {/* 탭별 에러 메시지 */}
        {activeError && (
          <div
            style={{
              marginBottom: 10,
              padding: "8px 10px",
              borderRadius: 8,
              background: "#fff4f4",
              color: "#b71c1c",
              fontSize: 13,
              border: "1px solid #ffcdd2",
            }}
          >
            {activeError}
          </div>
        )}

        {/* 라인 표시 토글: 탭별 */}
        {activeTab === "KOSPI" ? (
          <div
            style={{
              display: "flex",
              gap: "8px",
              marginBottom: "10px",
              flexWrap: "wrap",
            }}
          >
            <button
              onClick={() => setShowVKOSPI((v) => !v)}
              style={toggleBtnStyle(showVKOSPI)}
            >
              VKOSPI
            </button>
            <button
              onClick={() => setShowWVKOSPI((v) => !v)}
              style={toggleBtnStyle(showWVKOSPI)}
            >
              WVKOSPI
            </button>
          </div>
        ) : (
          <div
            style={{
              display: "flex",
              gap: "8px",
              marginBottom: "10px",
              flexWrap: "wrap",
            }}
          >
            <button
              onClick={() => setShowVKOSDAQ((v) => !v)}
              style={toggleBtnStyle(showVKOSDAQ)}
            >
              VKOSDAQ
            </button>
            <button
              onClick={() => setShowWVKOSDAQ((v) => !v)}
              style={toggleBtnStyle(showWVKOSDAQ)}
            >
              WVKOSDAQ
            </button>
          </div>
        )}

        {/* 기간 설정 */}
        <div
          style={{
            display: "flex",
            gap: "8px",
            alignItems: "center",
            flexWrap: "wrap",
            marginBottom: "12px",
          }}
        >
          <span style={{ fontSize: 13, color: "#2c3e50", minWidth: 70 }}>
            기간
          </span>
          {["1M", "3M", "6M", "1Y", "ALL", "CUSTOM"].map((p) => (
            <button
              key={p}
              style={periodBtnStyle(period === p)}
              onClick={() => setPeriod(p)}
            >
              {p}
            </button>
          ))}

          {period === "CUSTOM" && (
            <>
              <input
                type="date"
                value={startDate}
                onChange={(e) => setStartDate(e.target.value)}
                style={{
                  padding: "4px 6px",
                  border: "1px solid #cfd8dc",
                  borderRadius: 6,
                }}
              />
              <span style={{ fontSize: 12 }}>~</span>
              <input
                type="date"
                value={endDate}
                onChange={(e) => setEndDate(e.target.value)}
                style={{
                  padding: "4px 6px",
                  border: "1px solid #cfd8dc",
                  borderRadius: 6,
                }}
              />
            </>
          )}
        </div>

        <ResponsiveContainer width="100%" height={500}>
          <LineChart
            data={filteredData}
            margin={{ top: 12, right: 14, left: 6, bottom: 8 }}
          >
            <CartesianGrid stroke="#eee" />
            <XAxis dataKey="DATE" minTickGap={24} />
            <YAxis domain={["auto", "auto"]} width={58} />
            <Tooltip />
            <Legend />

            {activeTab === "KOSPI" && showVKOSPI && (
              <Line
                type="monotone"
                dataKey="VKOSPI"
                stroke="#2ca02c"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 4 }}
                name="VKOSPI"
              />
            )}
            {activeTab === "KOSPI" && showWVKOSPI && (
              <Line
                type="monotone"
                dataKey="WVKOSPI"
                stroke="#ff7f0e"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 4 }}
                name="WVKOSPI"
              />
            )}

            {activeTab === "KOSDAQ" && showVKOSDAQ && (
              <Line
                type="monotone"
                dataKey="VKOSDAQ"
                stroke="#2ca02c"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 4 }}
                name="VKOSDAQ"
              />
            )}
            {activeTab === "KOSDAQ" && showWVKOSDAQ && (
              <Line
                type="monotone"
                dataKey="WVKOSDAQ"
                stroke="#ff7f0e"
                strokeWidth={3}
                dot={false}
                activeDot={{ r: 4 }}
                name="WVKOSDAQ"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Charts;
