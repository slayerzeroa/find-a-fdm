const express = require("express");
const dotenv = require("dotenv");
const mariadb = require("mariadb");
const cors = require("cors");
const path = require("path");

dotenv.config({ path: path.resolve(__dirname, "./env/.env") });

const db_host = process.env.DB_HOST;
const db_user = process.env.DB_USER;
const db_password = process.env.DB_PASSWORD;
const db_database = process.env.DB_NAME;

const pool = mariadb.createPool({
  host: db_host,
  user: db_user,
  password: db_password,
  database: db_database,
  connectionLimit: 10, // 최대 연결 수 제한
  idleTimeout: 30000, // 유휴 연결 해제 시간 (밀리초)
  acquireTimeout: 10000, // 연결 획득 대기 시간 (밀리초)
  evictInterval: 15000, // 정리 주기 (밀리초)
  timeout: 30000, // 연결 시간 초과 (밀리초)
});

const app = express();
app.use(cors());

// Root endpoint
app.get("/", (req, res) => {
  console.log("Root endpoint accessed");
  res.send("Welcome to the server!!");
});

// Fetch all data about GEX(KOSPI 200 Gamma Exposure)
app.get("/gex", (req, res) => {
  pool
    .getConnection()
    .then((conn) => {
      return (
        conn
          .query(
            "SELECT * FROM (SELECT * FROM gamma_exposure ORDER BY `ID` DESC LIMIT 10) AS subquery ORDER BY `ID` ASC;"
          )
          // .query("SELECT * FROM gamma_exposure LIMIT 10;")
          .then((rows) => res.json(rows))
          .catch((err) => {
            console.error("Query error:", err);
            res
              .status(500)
              .json({ error: "Database query failed", details: err.message });
          })
          .finally(() => conn.release())
      ); // 연결 해제
    })
    .catch((err) => {
      console.error("Database connection error:", err);
      res
        .status(500)
        .json({ error: "Failed to connect to database", details: err.message });
    });
});

// Fetch all data
app.get("/vkospi", (req, res) => {
  pool
    .getConnection()
    .then((conn) => {
      return (
        conn
          .query(
            "SELECT * FROM (SELECT * FROM wvkospi ORDER BY `ID` DESC LIMIT 10) AS subquery ORDER BY `ID` ASC;"
          )
          // .query("SELECT * FROM gamma_exposure LIMIT 10;")
          .then((rows) => res.json(rows))
          .catch((err) => {
            console.error("Query error:", err);
            res
              .status(500)
              .json({ error: "Database query failed", details: err.message });
          })
          .finally(() => conn.release())
      ); // 연결 해제
    })
    .catch((err) => {
      console.error("Database connection error:", err);
      res
        .status(500)
        .json({ error: "Failed to connect to database", details: err.message });
    });
});

// Graceful Shutdown: 서버 종료 시 MariaDB 풀 종료
function gracefulShutdown() {
  console.log("Shutting down server...");
  pool
    .end() // 연결 풀 닫기
    .then(() => {
      console.log("MariaDB pool closed.");
      process.exit(0); // 정상 종료
    })
    .catch((err) => {
      console.error("Error while closing MariaDB pool:", err);
      process.exit(1); // 강제 종료
    });
}

// 종료 시그널 처리
process.on("SIGINT", gracefulShutdown); // Ctrl+C
process.on("SIGTERM", gracefulShutdown); // Docker Stop

const PORT = process.env.PORT || 8001;
app.listen(PORT, () => {
  console.log(`Server is running on http://localhost:${PORT}`);
});
