const express = require("express");
const dotenv = require("dotenv");
const mariadb = require("mariadb");
const cors = require("cors");
const path = require("path");
const helmet = require("helmet");
const rateLimit = require("express-rate-limit");
const jwt = require("jsonwebtoken");
const cookieParser = require("cookie-parser");
const crypto = require("crypto");
const { ChartJSNodeCanvas } = require("chartjs-node-canvas");

// .env 파일 + 컨테이너 환경변수 함께 사용
dotenv.config({ path: path.resolve(__dirname, "./env/.env") });
dotenv.config();

const app = express();
app.disable("x-powered-by");

// 프론트/백엔드 origin 분리 시 이미지 로드 차단 방지 위해 CORP 비활성화
app.use(
  helmet({
    crossOriginResourcePolicy: false,
  }),
);

app.use(express.json({ limit: "50kb" }));
app.use(cookieParser());

// 프록시(Cloudflare/Nginx) 뒤라면 활성화
app.set("trust proxy", 1);

// ===== ENV =====
const db_host = process.env.DB_HOST;
const db_user = process.env.DB_USER;
const db_password = process.env.DB_PASSWORD;
const db_database = process.env.DB_NAME;

const PORT = Number(process.env.PORT || 8001);

const REQUIRE_AUTH = String(process.env.REQUIRE_AUTH || "true") === "true";
const JWT_SECRET = process.env.JWT_SECRET || "";
const REFRESH_SECRET = process.env.REFRESH_SECRET || "";
const JWT_ISSUER = process.env.JWT_ISSUER || "slayerzeroa.click";
const JWT_AUDIENCE = process.env.JWT_AUDIENCE || "market-api";

const ACCESS_TTL = process.env.ACCESS_TTL || "10m";
const REFRESH_TTL = process.env.REFRESH_TTL || "7d";
const AUTH_CLIENT_KEY = process.env.AUTH_CLIENT_KEY || "";
const COOKIE_SECURE = String(process.env.COOKIE_SECURE || "true") === "true";
// cross-site 프론트(예: github.io)면 none 권장 + HTTPS 필수
const COOKIE_SAMESITE = process.env.COOKIE_SAMESITE || "lax"; // "lax" | "none" | "strict"

// raw 데이터 API 차단 스위치
const DISABLE_RAW_DATA_API =
  String(process.env.DISABLE_RAW_DATA_API || "false") === "true";

// chart 렌더 옵션
const CHART_WIDTH = Number(process.env.CHART_WIDTH || 1200);
const CHART_HEIGHT = Number(process.env.CHART_HEIGHT || 420);
const CHART_CACHE_MS = Number(process.env.CHART_CACHE_MS || 10000); // 10초

// ✅ 허용 Origin
const allowedOrigins = (process.env.CORS_ORIGINS || "")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);

const corsOptions = {
  origin: (origin, cb) => {
    // 서버-서버 호출/헬스체크는 origin 없을 수 있음
    if (!origin) return cb(null, true);
    if (allowedOrigins.length === 0) return cb(new Error("CORS blocked"));
    return allowedOrigins.includes(origin)
      ? cb(null, true)
      : cb(new Error("CORS blocked"));
  },
  credentials: true,
};

app.use(cors(corsOptions));
app.options("*", cors(corsOptions));

// DB Pool
const pool = mariadb.createPool({
  host: db_host,
  user: db_user,
  password: db_password,
  database: db_database,
  connectionLimit: 10,
  idleTimeout: 30000,
  acquireTimeout: 10000,
  evictInterval: 15000,
  timeout: 30000,
});

// 공통 Rate Limit
const apiLimiter = rateLimit({
  windowMs: 60 * 1000, // 1분
  limit: 60, // 분당 60회
  standardHeaders: true,
  legacyHeaders: false,
  keyGenerator: (req) => {
    // 인증 유저 우선, 없으면 ip
    const auth = req.headers.authorization || "";
    if (auth.startsWith("Bearer ")) {
      return `tk:${auth.slice(7, 20)}`; // 토큰 일부
    }
    return `ip:${req.ip}`;
  },
});

const authLimiter = rateLimit({
  windowMs: 60 * 1000,
  limit: 20,
  standardHeaders: true,
  legacyHeaders: false,
});

// ===== Refresh Token 저장소 =====
// 단일 인스턴스 기준(메모리 저장). 재시작 시 초기화됨.
// 멀티 인스턴스/영속 필요하면 Redis로 교체.
const refreshJtiStore = new Set();

function signAccessToken(sub = "frontend") {
  return jwt.sign(
    {
      sub,
      scope: ["vkospi:read", "vkosdaq:read", "gex:read", "krxgex:read"],
    },
    JWT_SECRET,
    {
      expiresIn: ACCESS_TTL,
      issuer: JWT_ISSUER,
      audience: JWT_AUDIENCE,
    },
  );
}

function signRefreshToken(sub = "frontend", jti) {
  return jwt.sign({ sub, jti, typ: "refresh" }, REFRESH_SECRET, {
    expiresIn: REFRESH_TTL,
    issuer: JWT_ISSUER,
    audience: JWT_AUDIENCE,
  });
}

// 인증 미들웨어
function requireScope(scope) {
  return (req, res, next) => {
    if (!REQUIRE_AUTH) return next(); // 개발용 우회

    if (!JWT_SECRET) {
      return res.status(500).json({ error: "Server auth not configured" });
    }

    const auth = req.headers.authorization || "";
    const token = auth.startsWith("Bearer ") ? auth.slice(7) : null;
    if (!token) return res.status(401).json({ error: "Unauthorized" });

    try {
      const payload = jwt.verify(token, JWT_SECRET, {
        issuer: JWT_ISSUER,
        audience: JWT_AUDIENCE,
      });

      const scopes = Array.isArray(payload.scope) ? payload.scope : [];
      if (!scopes.includes(scope)) {
        return res.status(403).json({ error: "Forbidden" });
      }

      req.user = payload;
      return next();
    } catch (e) {
      return res.status(401).json({ error: "Invalid or expired token" });
    }
  };
}

// 공통 DB 실행 함수
async function runQuery(sql, params = []) {
  let conn;
  try {
    conn = await pool.getConnection();
    const rows = await conn.query(sql, params);
    return rows;
  } finally {
    if (conn) conn.release();
  }
}

// LIMIT 파라미터 방어
function parseLimit(req, defaultValue = 300, maxValue = 2000) {
  const n = Number(req.query.limit ?? defaultValue);
  if (!Number.isFinite(n) || n <= 0) return defaultValue;
  return Math.min(Math.floor(n), maxValue);
}

function denyRawIfDisabled(req, res, next) {
  if (DISABLE_RAW_DATA_API) {
    return res.status(404).json({ error: "Not found" });
  }
  return next();
}

function toNumOrNull(v, digits = 2) {
  const n = Number(v);
  if (!Number.isFinite(n)) return null;
  return Number(n.toFixed(digits));
}

// ===== Chart renderer (singleton) =====
const chartJSNodeCanvas = new ChartJSNodeCanvas({
  width: CHART_WIDTH,
  height: CHART_HEIGHT,
  backgroundColour: "white",
  chartCallback: (ChartJS) => {
    ChartJS.defaults.responsive = false;
    ChartJS.defaults.animation = false;
    ChartJS.defaults.color = "#2b2b2b";
    ChartJS.defaults.font.family = "Arial";
  },
});

// 간단 메모리 캐시
const chartCache = new Map(); // key -> { buffer, expiresAt }

function getChartCache(key) {
  const hit = chartCache.get(key);
  if (!hit) return null;
  if (Date.now() > hit.expiresAt) {
    chartCache.delete(key);
    return null;
  }
  return hit.buffer;
}

function setChartCache(key, buffer, ttlMs = CHART_CACHE_MS) {
  chartCache.set(key, { buffer, expiresAt: Date.now() + ttlMs });
}

function setPngNoStoreHeaders(res, filename) {
  res.type("png");
  res.set({
    "Cache-Control": "private, no-store, max-age=0",
    Pragma: "no-cache",
    Expires: "0",
    "X-Content-Type-Options": "nosniff",
    "Content-Disposition": `inline; filename="${filename}"`,
  });
}

function makeLineConfig(title, labels, datasets) {
  return {
    type: "line",
    data: {
      labels,
      datasets,
    },
    options: {
      responsive: false,
      plugins: {
        legend: { display: true },
        title: { display: true, text: title },
      },
      scales: {
        x: { ticks: { maxTicksLimit: 10 } },
        y: { beginAtZero: false },
      },
    },
  };
}

async function renderPngBuffer({ title, labels, datasets }) {
  const config = makeLineConfig(title, labels, datasets);
  return chartJSNodeCanvas.renderToBuffer(config, "image/png");
}

// Root / Health
app.get("/", (req, res) => {
  res.send("Welcome to the secured server");
});

app.get("/health", async (req, res) => {
  try {
    await runQuery("SELECT 1 AS ok");
    res.json({ ok: true });
  } catch {
    res.status(500).json({ ok: false });
  }
});

// ===== Auth APIs =====

// 초기 access token 발급
// 프론트는 헤더 X-Client-Key: <AUTH_CLIENT_KEY> 넣어서 요청
app.post("/auth/token", authLimiter, (req, res) => {
  try {
    if (!JWT_SECRET || !REFRESH_SECRET) {
      return res.status(500).json({ error: "Auth secrets not configured" });
    }

    if (!AUTH_CLIENT_KEY) {
      return res.status(500).json({ error: "AUTH_CLIENT_KEY not configured" });
    }

    const clientKey = req.headers["x-client-key"];
    if (!clientKey || clientKey !== AUTH_CLIENT_KEY) {
      return res.status(401).json({ error: "Unauthorized client" });
    }

    const sub = "frontend";
    const jti = crypto.randomUUID();
    refreshJtiStore.add(jti);

    const accessToken = signAccessToken(sub);
    const refreshToken = signRefreshToken(sub, jti);

    res.cookie("rt", refreshToken, {
      httpOnly: true,
      secure: COOKIE_SECURE,
      sameSite: COOKIE_SAMESITE,
      path: "/auth",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    return res.json({ accessToken });
  } catch (e) {
    console.error("auth/token error:", e.message);
    return res.status(500).json({ error: "Token issue failed" });
  }
});

// access token 재발급 (refresh cookie 기반)
app.post("/auth/refresh", authLimiter, (req, res) => {
  try {
    if (!JWT_SECRET || !REFRESH_SECRET) {
      return res.status(500).json({ error: "Auth secrets not configured" });
    }

    const rt = req.cookies?.rt;
    if (!rt) return res.status(401).json({ error: "No refresh token" });

    const payload = jwt.verify(rt, REFRESH_SECRET, {
      issuer: JWT_ISSUER,
      audience: JWT_AUDIENCE,
    });

    if (payload.typ !== "refresh" || !payload.jti) {
      return res.status(401).json({ error: "Invalid refresh token" });
    }

    if (!refreshJtiStore.has(payload.jti)) {
      return res.status(401).json({ error: "Refresh token revoked" });
    }

    // rotate refresh token
    refreshJtiStore.delete(payload.jti);
    const newJti = crypto.randomUUID();
    refreshJtiStore.add(newJti);

    const accessToken = signAccessToken(payload.sub);
    const newRefreshToken = signRefreshToken(payload.sub, newJti);

    res.cookie("rt", newRefreshToken, {
      httpOnly: true,
      secure: COOKIE_SECURE,
      sameSite: COOKIE_SAMESITE,
      path: "/auth",
      maxAge: 7 * 24 * 60 * 60 * 1000,
    });

    return res.json({ accessToken });
  } catch (e) {
    console.error("auth/refresh error:", e.message);
    return res.status(401).json({ error: "Refresh failed" });
  }
});

// 로그아웃 (refresh token 무효화)
app.post("/auth/logout", authLimiter, (req, res) => {
  try {
    const rt = req.cookies?.rt;
    if (rt && REFRESH_SECRET) {
      try {
        const payload = jwt.verify(rt, REFRESH_SECRET, {
          issuer: JWT_ISSUER,
          audience: JWT_AUDIENCE,
        });
        if (payload?.jti) refreshJtiStore.delete(payload.jti);
      } catch (_) {
        // ignore
      }
    }

    res.clearCookie("rt", {
      httpOnly: true,
      secure: COOKIE_SECURE,
      sameSite: COOKIE_SAMESITE,
      path: "/auth",
    });

    return res.json({ ok: true });
  } catch (e) {
    console.error("auth/logout error:", e.message);
    return res.status(500).json({ error: "Logout failed" });
  }
});

// ===== Image Chart APIs (권장) =====
// 원시 데이터 대신 이미지 렌더 결과만 전달

app.get(
  "/chart/vkospi.png",
  apiLimiter,
  requireScope("vkospi:read"),
  async (req, res) => {
    try {
      const limit = parseLimit(req, 500, 3000);
      const key = `chart:vkospi:${limit}`;
      const cached = getChartCache(key);

      if (cached) {
        setPngNoStoreHeaders(res, "vkospi.png");
        return res.send(cached);
      }

      const rows = await runQuery(
        `SELECT BAS_DD, VKOSPI, WVKOSPI
         FROM wvkospi
         ORDER BY ID DESC
         LIMIT ?`,
        [limit],
      );

      rows.reverse();

      const labels = rows.map((r) => String(r.BAS_DD));
      const datasets = [
        {
          label: "VKOSPI",
          data: rows.map((r) => toNumOrNull(r.VKOSPI, 2)),
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.15,
        },
        {
          label: "WVKOSPI",
          data: rows.map((r) => toNumOrNull(r.WVKOSPI, 2)),
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.15,
        },
      ];

      const png = await renderPngBuffer({
        title: "VKOSPI (Server Rendered)",
        labels,
        datasets,
      });

      setChartCache(key, png);
      setPngNoStoreHeaders(res, "vkospi.png");
      return res.send(png);
    } catch (err) {
      console.error("chart/vkospi.png error:", err.message);
      return res.status(500).json({ error: "Chart render failed" });
    }
  },
);

app.get(
  "/chart/vkosdaq.png",
  apiLimiter,
  requireScope("vkosdaq:read"),
  async (req, res) => {
    try {
      const limit = parseLimit(req, 500, 3000);
      const key = `chart:vkosdaq:${limit}`;
      const cached = getChartCache(key);

      if (cached) {
        setPngNoStoreHeaders(res, "vkosdaq.png");
        return res.send(cached);
      }

      const rows = await runQuery(
        `SELECT BAS_DD, KOSDAQ, WVKOSDAQ
         FROM wvkosdaq
         ORDER BY ID DESC
         LIMIT ?`,
        [limit],
      );

      rows.reverse();

      const labels = rows.map((r) => String(r.BAS_DD));
      const datasets = [
        {
          label: "KOSDAQ",
          data: rows.map((r) => toNumOrNull(r.KOSDAQ, 2)),
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.15,
        },
        {
          label: "WVKOSDAQ",
          data: rows.map((r) => toNumOrNull(r.WVKOSDAQ, 2)),
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.15,
        },
      ];

      const png = await renderPngBuffer({
        title: "VKOSDAQ (Server Rendered)",
        labels,
        datasets,
      });

      setChartCache(key, png);
      setPngNoStoreHeaders(res, "vkosdaq.png");
      return res.send(png);
    } catch (err) {
      console.error("chart/vkosdaq.png error:", err.message);
      return res.status(500).json({ error: "Chart render failed" });
    }
  },
);

app.get(
  "/chart/gex.png",
  apiLimiter,
  requireScope("gex:read"),
  async (req, res) => {
    try {
      const limit = parseLimit(req, 500, 3000);
      const key = `chart:gex:${limit}`;
      const cached = getChartCache(key);

      if (cached) {
        setPngNoStoreHeaders(res, "gex.png");
        return res.send(cached);
      }

      const rows = await runQuery(
        `SELECT BAS_DD, GAMMA_EXPOSURE
         FROM gamma_exposure
         ORDER BY ID DESC
         LIMIT ?`,
        [limit],
      );

      rows.reverse();

      const labels = rows.map((r) => String(r.BAS_DD));
      const datasets = [
        {
          label: "Gamma Exposure",
          data: rows.map((r) => toNumOrNull(r.GAMMA_EXPOSURE, 2)),
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.15,
        },
      ];

      const png = await renderPngBuffer({
        title: "KOSPI200 Gamma Exposure (Server Rendered)",
        labels,
        datasets,
      });

      setChartCache(key, png);
      setPngNoStoreHeaders(res, "gex.png");
      return res.send(png);
    } catch (err) {
      console.error("chart/gex.png error:", err.message);
      return res.status(500).json({ error: "Chart render failed" });
    }
  },
);

app.get(
  "/chart/krxgex.png",
  apiLimiter,
  requireScope("krxgex:read"),
  async (req, res) => {
    try {
      const limit = parseLimit(req, 500, 3000);
      const key = `chart:krxgex:${limit}`;
      const cached = getChartCache(key);

      if (cached) {
        setPngNoStoreHeaders(res, "krxgex.png");
        return res.send(cached);
      }

      const rows = await runQuery(
        `SELECT BAS_DD, GAMMA_EXPOSURE
         FROM krx_gamma_exposure
         ORDER BY ID DESC
         LIMIT ?`,
        [limit],
      );

      rows.reverse();

      const labels = rows.map((r) => String(r.BAS_DD));
      const datasets = [
        {
          label: "KRX Gamma Exposure",
          data: rows.map((r) => toNumOrNull(r.GAMMA_EXPOSURE, 2)),
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.15,
        },
      ];

      const png = await renderPngBuffer({
        title: "KRX Gamma Exposure (Server Rendered)",
        labels,
        datasets,
      });

      setChartCache(key, png);
      setPngNoStoreHeaders(res, "krxgex.png");
      return res.send(png);
    } catch (err) {
      console.error("chart/krxgex.png error:", err.message);
      return res.status(500).json({ error: "Chart render failed" });
    }
  },
);

// ===== Protected Raw APIs (선택적으로 비활성화) =====
// raw 전체 dump를 막기 위해:
// 1) 필요한 컬럼만
// 2) 최신 N건만 (limit)
// 3) ASC 정렬 원하면 reverse

app.get(
  "/gex",
  denyRawIfDisabled,
  apiLimiter,
  requireScope("gex:read"),
  async (req, res) => {
    try {
      const limit = parseLimit(req, 500, 3000);
      const rows = await runQuery(
        `SELECT ID, BAS_DD, KOSPI200, GAMMA_EXPOSURE
         FROM gamma_exposure
         ORDER BY ID DESC
         LIMIT ?`,
        [limit],
      );
      rows.reverse();
      res.set("Cache-Control", "public, max-age=10");
      res.json(rows);
    } catch (err) {
      console.error("gex query error:", err.message);
      res.status(500).json({ error: "Database query failed" });
    }
  },
);

app.get(
  "/vkospi",
  denyRawIfDisabled,
  apiLimiter,
  requireScope("vkospi:read"),
  async (req, res) => {
    try {
      const limit = parseLimit(req, 500, 3000);
      const rows = await runQuery(
        `SELECT ID, BAS_DD, KOSPI, WVKOSPI, VKOSPI
         FROM wvkospi
         ORDER BY ID DESC
         LIMIT ?`,
        [limit],
      );
      rows.reverse();
      res.set("Cache-Control", "public, max-age=10");
      res.json(rows);
    } catch (err) {
      console.error("vkospi query error:", err.message);
      res.status(500).json({ error: "Database query failed" });
    }
  },
);

app.get(
  "/vkosdaq",
  denyRawIfDisabled,
  apiLimiter,
  requireScope("vkosdaq:read"),
  async (req, res) => {
    try {
      const limit = parseLimit(req, 500, 3000);
      const rows = await runQuery(
        `SELECT ID, BAS_DD, KOSDAQ, WVKOSDAQ
         FROM wvkosdaq
         ORDER BY ID DESC
         LIMIT ?`,
        [limit],
      );
      rows.reverse();
      res.set("Cache-Control", "public, max-age=10");
      res.json(rows);
    } catch (err) {
      console.error("vkosdaq query error:", err.message);
      res.status(500).json({ error: "Database query failed" });
    }
  },
);

app.get(
  "/krxgex",
  denyRawIfDisabled,
  apiLimiter,
  requireScope("krxgex:read"),
  async (req, res) => {
    try {
      const limit = parseLimit(req, 500, 3000);
      const rows = await runQuery(
        `SELECT ID, BAS_DD, KRX200, GAMMA_EXPOSURE
         FROM krx_gamma_exposure
         ORDER BY ID DESC
         LIMIT ?`,
        [limit],
      );
      rows.reverse();
      res.set("Cache-Control", "public, max-age=10");
      res.json(rows);
    } catch (err) {
      console.error("krxgex query error:", err.message);
      res.status(500).json({ error: "Database query failed" });
    }
  },
);

// CORS 에러 처리(명시)
app.use((err, req, res, next) => {
  if (err && err.message === "CORS blocked") {
    return res.status(403).json({ error: "CORS blocked" });
  }
  return next(err);
});

// 최종 에러 핸들러
app.use((err, req, res, next) => {
  console.error("Unhandled error:", err.message);
  res.status(500).json({ error: "Internal Server Error" });
});

// Graceful Shutdown
async function gracefulShutdown() {
  console.log("Shutting down server...");
  try {
    await pool.end();
    console.log("MariaDB pool closed.");
    process.exit(0);
  } catch (err) {
    console.error("Error while closing MariaDB pool:", err);
    process.exit(1);
  }
}

process.on("SIGINT", gracefulShutdown);
process.on("SIGTERM", gracefulShutdown);

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
