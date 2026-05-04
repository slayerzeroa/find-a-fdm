// import React from "react";
// import { Link } from "react-router-dom";
// import styled from "styled-components";

// // 스타일 정의
// const Container = styled.div`
//   display: flex;
//   flex-direction: column;
//   align-items: center;
//   padding: 2rem;
//   background-color: #f5f5f5;
// `;

// const Header = styled.h1`
//   font-size: 2.5rem;
//   margin-bottom: 1rem;
//   color: #333;
// `;

// const Description = styled.p`
//   font-size: 1.2rem;
//   margin-bottom: 2rem;
//   text-align: center;
//   color: #555;
// `;

// const ArchiveList = styled.ul`
//   list-style: none;
//   padding: 0;
//   width: 100%;
//   max-width: 600px;
// `;

// const ArchiveItem = styled.li`
//   background: #fff;
//   padding: 1rem;
//   margin-bottom: 1rem;
//   border-radius: 8px;
//   box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
// `;

// const ArchiveLink = styled(Link)`
//   text-decoration: none;
//   color: #007bff;

//   &:hover {
//     text-decoration: underline;
//   }
// `;

// // 활동 아카이빙 리스트
// const activities = [
//   {
//     id: 1,
//     title: "KOSPI Gamma Exposure",
//     description: "코스피 감마 익스포저 검증 프로젝트",
//   },
//   //   {
//   //     id: 2,
//   //     title: "Open Source Contribution",
//   //     description: "오픈 소스 기여 경험",
//   //   },
//   //   {
//   //     id: 3,
//   //     title: "기술 블로그 작성",
//   //     description: "리액트 관련 블로그 포스팅",
//   //   },
// ];

// function ArchiveLanding() {
//   return (
//     <Container>
//       <Header>FDM Archive</Header>
//       <Description>
//         Here are some of our projects and contributions. Click on any item to
//         learn more!
//       </Description>
//       <ArchiveList>
//         {activities.map((activity) => (
//           <ArchiveItem key={activity.id}>
//             <h2>{activity.title}</h2>
//             <p>{activity.description}</p>
//             <ArchiveLink to={`/detail/${activity.id}`}>
//               View Details
//             </ArchiveLink>
//           </ArchiveItem>
//         ))}
//       </ArchiveList>
//     </Container>
//   );
// }

// export default ArchiveLanding;

import React from "react";
import { Link } from "react-router-dom";
import styled from "styled-components";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
`;

const Header = styled.h1`
  font-size: 2.5rem;
  margin-bottom: 1rem;
  color: #333;
`;

const Description = styled.p`
  font-size: 1.2rem;
  margin-bottom: 2rem;
  text-align: center;
  color: #555;
`;

const ArchiveList = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1.5rem;
  width: 100%;
`;

const ArchiveCard = styled.div`
  background: #fff;
  border: 1px solid #ddd;
  border-radius: 10px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  flex: 1 1 calc(43.33% - 2rem); /* 카드 크기 계산 */
  max-width: 600px; /* 최대 너비 */
  min-width: 300px; /* 최소 너비 */
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 6px 10px rgba(0, 0, 0, 0.15);
  }
`;

const CardTitle = styled.h2`
  font-size: 1.5rem;
  color: #333;
  margin-bottom: 0.5rem;
`;

const CardDescription = styled.p`
  font-size: 1rem;
  color: #555;
  margin-bottom: 1rem;
`;

const ArchiveLink = styled(Link)`
  text-decoration: none;
  color: #007bff;
  font-weight: bold;

  &:hover {
    text-decoration: underline;
  }
`;

const activities = [
  {
    id: 1,
    title: "KOSPI Gamma Exposure",
    description: "코스피 감마 익스포저 검증 프로젝트",
  },
];

function ArchiveLanding() {
  return (
    <Container>
      <Header>FDM Archive</Header>
      <Description>
        Here are some of our projects and contributions. Click on any item to
        learn more!
      </Description>
      <ArchiveList>
        {activities.map((activity) => (
          <ArchiveCard key={activity.id}>
            <CardTitle>{activity.title}</CardTitle>
            <CardDescription>{activity.description}</CardDescription>
            <ArchiveLink to={`/archive/${activity.id}`}>
              View Details
            </ArchiveLink>
          </ArchiveCard>
        ))}
      </ArchiveList>
    </Container>
  );
}

export default ArchiveLanding;
