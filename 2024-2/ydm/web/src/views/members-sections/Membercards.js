import React from "react";
import Membercard from "components/Cards/Membercard";
import { Box, Typography } from "@mui/material";

import "./Membercards.css";

function Membercards() {
  const handleMoreInfo = (name) => {
    alert(`More info about ${name}`);
  };

  const handleContact = (name) => {
    alert(`Contacting ${name}`);
  };

  const membersByBatch = {
    "2024-2 FDM 1기": [
      {
        name: "유대명",
        role: "팀장",
        image: require("assets/img/members/ydm.png"),
        description:
          "데이터분석을 통해 퀀트 전략을 검증하고, 퀀트 전략을 통해 수익을 창출합니다.",
      },
      {
        name: "김가영",
        role: "팀원",
        image: require("assets/img/members/Unknown_person.jpg"),
        description:
          "데이터분석을 통해 퀀트 전략을 검증하고, 퀀트 전략을 통해 수익을 창출합니다.",
      },
      {
        name: "이문기",
        role: "팀원",
        image: require("assets/img/members/lmk.png"),
        description:
          "다양한 투자 포트폴리오를 관리하며 최적의 수익률을 추구합니다.",
      },
      {
        name: "장건",
        role: "팀원",
        image: require("assets/img/members/Unknown_person.jpg"),
        description:
          "데이터 기반으로 투자 성과를 분석하고 개선점을 제시합니다. 합리적인 의사결정 도구 창출.",
      },
      {
        name: "정지휴",
        role: "팀원",
        image: require("assets/img/members/jjh.png"),
        description:
          "투자 전략을 지원하는 소프트웨어 도구를 개발합니다. 전략 개발 및 검증에 활용됩니다.",
      },
    ],
    "2기": [],
    "3기": [],
  };

  return (
    <Box sx={{ padding: { xs: 2, sm: 4, md: 6 } }}>
      {Object.entries(membersByBatch).map(([batch, members], batchIndex) => (
        <Box key={batchIndex} sx={{ marginBottom: 6 }}>
          {/* 기수 제목 */}
          <Typography
            variant="h4"
            component="h2"
            sx={{
              marginTop: 3,
              marginBottom: 4,
              textAlign: "center",
              fontFamily: "'Roboto', sans-serif", // 원하는 글꼴
              fontWeight: "bold", // 굵기 설정
              color: "#333", // 색상
            }}
          >
            {batch}
          </Typography>
          {/* 기수별 멤버 카드 */}
          <Box
            sx={{
              display: "flex",
              flexWrap: "wrap",
              gap: { xs: 2, sm: 3 },
              justifyContent: "center",
            }}
          >
            {members.map((member, memberIndex) => (
              <Membercard
                key={memberIndex}
                name={member.name}
                role={member.role}
                image={member.image}
                description={member.description}
                onMoreInfo={() => handleMoreInfo(member.name)}
                onContact={() => handleContact(member.name)}
              />
            ))}
          </Box>
        </Box>
      ))}
    </Box>
  );
}

export default Membercards;
