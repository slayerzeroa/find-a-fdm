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
  const [chartData, setChartData] = useState([]);

  // 컴포넌트가 마운트될 때 데이터 fetch
  useEffect(() => {
    const fetchData = async () => {
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

        setChartData(processedData); // 가공된 데이터를 상태에 저장
      } catch (error) {
        console.error("데이터 가져오기 오류:", error);
      }
    };

    fetchData(); // 데이터 fetch 함수 호출
  }, []);

  // 차트 렌더링
  return (
    <div style={{ width: "100%", padding: "20px" }}>
      {/* 차트 제목 */}
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
          <LineChart data={chartData}>
            <Line type="monotone" dataKey="NET_GEX" stroke="#8884d8" />
            <CartesianGrid stroke="#ccc" />
            <XAxis dataKey="DATE" />
            <YAxis />
            <Tooltip />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}

export default Charts;
