// 필요한 모듈 임포트
import React, { useState, useEffect } from "react";
import axios from "axios";
import {
  LineChart,
  Line,
  CartesianGrid,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

function Charts() {
  // 차트 데이터를 저장할 상태 변수 선언
  const [gexData, setgexData] = useState([]);
  const [vkospiData, setvkospiData] = useState([]);
  const [wvkospiData, setwvkospiData] = useState([]);

  // **현재 어떤 탭을 보여줄지** 관리하는 state
  const [activeTab, setActiveTab] = useState("gex");
  // 'gex' | 'wvkospi' | 'vkospi' 중 하나를 저장

  // ------------------------------
  // 1) GEX 데이터 fetch
  // ------------------------------
  useEffect(() => {
    const fetchGexData = async () => {
      try {
        // API로부터 데이터 가져오기
        const response = await axios.get(
          "http://slayerzeroa.iptime.org:8001/gex"
        );

        // DATE 형식을 변환하여 새로운 데이터 생성
        const processedData = response.data.map((item) => {
          const dateString = item.DATE;
          const year = dateString.substring(0, 4);
          const month = dateString.substring(4, 6);
          const day = dateString.substring(6, 8);
          const formattedDate = `${year}-${month}-${day}`;

          return {
            ...item,
            DATE: formattedDate,
          };
        });

        setgexData(processedData); // 가공된 데이터를 상태에 저장
      } catch (error) {
        console.error("데이터 가져오기 오류:", error);
      }
    };

    fetchGexData(); // 데이터 fetch 함수 호출
  }, []);

  // ------------------------------
  // 2) VKOSPI / WVKOSPI 데이터 fetch
  // ------------------------------
  useEffect(() => {
    const fetchVkospiData = async () => {
      try {
        // API 요청
        const response = await axios.get(
          "http://slayerzeroa.iptime.org:8001/vkospi"
        );

        // 1) BAS_DD & VKOSPI만 뽑아서 날짜 변환 후 배열 생성
        const extractedVkospi = response.data.map((item) => {
          // 날짜 가공(YYYYMMDD → YYYY-MM-DD)
          const dateString = item.BAS_DD;
          const year = dateString.substring(0, 4);
          const month = dateString.substring(4, 6);
          const day = dateString.substring(6, 8);
          const formattedDate = `${year}-${month}-${day}`;

          return {
            DATE: formattedDate,
            VKOSPI: item.VKOSPI,
          };
        });

        // 2) BAS_DD & WVKOSPI만 뽑아서 날짜 변환 후 배열 생성
        const extractedWvkospi = response.data.map((item) => {
          // 날짜 가공(YYYYMMDD → YYYY-MM-DD)
          const dateString = item.BAS_DD;
          const year = dateString.substring(0, 4);
          const month = dateString.substring(4, 6);
          const day = dateString.substring(6, 8);
          const formattedDate = `${year}-${month}-${day}`;

          return {
            DATE: formattedDate,
            WVKOSPI: item.WVKOSPI,
          };
        });

        // 3) 각각의 state에 저장
        setvkospiData(extractedVkospi);
        setwvkospiData(extractedWvkospi);
      } catch (error) {
        console.error("데이터 가져오기 오류:", error);
      }
    };

    fetchVkospiData();
  }, []);

  // ------------------------------
  // 렌더링 파트
  // ------------------------------
  return (
    <div style={{ width: "100%", padding: "20px" }}>
      {/* ---- 탭 버튼 영역 ---- */}
      <div style={{ display: "flex", gap: "10px", marginBottom: "20px" }}>
        <button
          onClick={() => setActiveTab("gex")}
          style={{
            padding: "8px 16px",
            cursor: "pointer",
            backgroundColor: activeTab === "gex" ? "#34495e" : "#bdc3c7",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
          }}
        >
          GAMMA EXPOSURE
        </button>

        <button
          onClick={() => setActiveTab("wvkospi")}
          style={{
            padding: "8px 16px",
            cursor: "pointer",
            backgroundColor: activeTab === "wvkospi" ? "#34495e" : "#bdc3c7",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
          }}
        >
          WVKOSPI
        </button>

        <button
          onClick={() => setActiveTab("vkospi")}
          style={{
            padding: "8px 16px",
            cursor: "pointer",
            backgroundColor: activeTab === "vkospi" ? "#34495e" : "#bdc3c7",
            color: "#fff",
            border: "none",
            borderRadius: "4px",
          }}
        >
          VKOSPI
        </button>
      </div>

      {/* ---- GEX 그래프 ---- */}
      {activeTab === "gex" && (
        <>
          <h2
            style={{
              textAlign: "left",
              marginBottom: "3%",
              marginLeft: "5%",
              marginTop: "5%",
              fontFamily: "'Noto Sans', sans-serif",
              fontWeight: "700",
              color: "#2c3e50",
              fontSize: "150%",
            }}
          >
            KOSPI 200 GAMMA EXPOSURE HISTORY
          </h2>
          <div style={{ paddingRight: "5%" }}>
            <ResponsiveContainer width="100%" aspect={16 / 9}>
              <LineChart data={gexData}>
                <Line type="monotone" dataKey="NET_GEX" stroke="#8884d8" />
                <CartesianGrid stroke="#ccc" />
                <XAxis dataKey="DATE" />
                <YAxis />
                <Tooltip />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}

      {/* ---- WVKOSPI 그래프 ---- */}
      {activeTab === "wvkospi" && (
        <>
          <h2
            style={{
              textAlign: "left",
              marginBottom: "3%",
              marginLeft: "5%",
              marginTop: "5%",
              fontFamily: "'Noto Sans', sans-serif",
              fontWeight: "700",
              color: "#2c3e50",
              fontSize: "150%",
            }}
          >
            KOSPI 200 WVKOSPI HISTORY
          </h2>
          <div style={{ paddingRight: "5%" }}>
            <ResponsiveContainer width="100%" aspect={16 / 9}>
              <LineChart data={wvkospiData}>
                <Line type="monotone" dataKey="WVKOSPI" stroke="#8884d8" />
                <CartesianGrid stroke="#ccc" />
                <XAxis dataKey="DATE" />
                <YAxis domain={["dataMin", "dataMax"]} />
                <Tooltip />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}

      {/* ---- VKOSPI 그래프 ---- */}
      {activeTab === "vkospi" && (
        <>
          <h2
            style={{
              textAlign: "left",
              marginBottom: "3%",
              marginLeft: "5%",
              marginTop: "5%",
              fontFamily: "'Noto Sans', sans-serif",
              fontWeight: "700",
              color: "#2c3e50",
              fontSize: "150%",
            }}
          >
            KOSPI 200 VKOSPI HISTORY
          </h2>
          <div style={{ paddingRight: "5%" }}>
            <ResponsiveContainer width="100%" aspect={16 / 9}>
              <LineChart data={vkospiData}>
                <Line type="monotone" dataKey="VKOSPI" stroke="#8884d8" />
                <CartesianGrid stroke="#ccc" />
                <XAxis dataKey="DATE" />
                <YAxis domain={["dataMin", "dataMax"]} />
                <Tooltip />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </>
      )}
    </div>
  );
}

export default Charts;
