import React from "react";
import Membercard from "components/Cards/Membercard";
import { Box, Typography } from "@mui/material";

import "./Membercards.css";

function Membercards() {
  const handleMoreInfo = (name) => {
    alert(`More info about ${name}`);
  };

  const handleContact = (contact) => {
    const url = contact.includes("@") ? `mailto:${contact}` : contact;
    window.open(url, "_blank");
  };

  const membersByBatch = {
    "2024-2 FDM 1기": [
      {
        name: "유대명",
        role: "팀장",
        image: require("assets/img/members/ydm.png"),
        description: "Gamma Exposure 프로젝트",
        contact: "https://blog.naver.com/slayerzeroa",
      },
      {
        name: "김가영",
        role: "팀원",
        image: require("assets/img/members/kky.png"),
        description: "Gamma Exposure 프로젝트",
        contact: "kayeongkim43@gmail.com",
      },
      {
        name: "이문기",
        role: "팀원",
        image: require("assets/img/members/lmk.png"),
        description: "Gamma Exposure 프로젝트",
        contact: "ansrl23@naver.com",
      },
      {
        name: "장건",
        role: "팀원",
        image: require("assets/img/members/jg.png"),
        description: "Gamma Exposure 프로젝트",
        contact: "geon8074@naver.com",
      },
      {
        name: "정지휴",
        role: "팀원",
        image: require("assets/img/members/jjh.png"),
        description: "Gamma Exposure 프로젝트",
        contact: "jihyujung@yonsei.ac.kr",
      },
    ],
    // "2기": [],
    // "3기": [],
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
                contact={member.contact}
                onMoreInfo={() => handleMoreInfo(member.name)}
                onContact={() => handleContact(member.contact)}
              />
            ))}
          </Box>
        </Box>
      ))}
    </Box>
  );
}

export default Membercards;
