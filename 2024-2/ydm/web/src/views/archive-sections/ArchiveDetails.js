import React, { useState, useEffect } from "react";
import styled from "styled-components";
import { useParams, useNavigate } from "react-router-dom"; // useNavigate 추가
import Lightbox from "react-image-lightbox";
import "react-image-lightbox/style.css"; // Lightbox 스타일 적용

// core components
import IndexNavbar from "components/Navbars/IndexNavbar.js";
import ArchiveHeader from "components/Headers/ArchiveHeader.js";
import DarkFooter from "components/Footers/DarkFooter.js";

const Container = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
`;

const Header = styled.h1`
  font-size: 2rem;
  margin-bottom: 1rem;
`;

const BackButton = styled.button`
  margin-bottom: 1.5rem;
  padding: 0.5rem 1rem;
  background-color: rgb(140, 140, 140);
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 1rem;

  &:hover {
    background-color: rgb(140, 140, 140);
  }
`;

const ImageGallery = styled.div`
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  width: 100%;
`;

const Image = styled.img`
  width: 200px;
  height: auto;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: pointer;
`;

function importAllImages(requireContext) {
  const allImages = requireContext.keys().map(requireContext);
  // 중복 제거
  const uniqueImages = [...new Set(allImages)];
  return uniqueImages.sort((a, b) => {
    const nameA = a.split("/").pop().toLowerCase();
    const nameB = b.split("/").pop().toLowerCase();
    return nameA.localeCompare(nameB);
  });
}

// 이미지 동적 로드
const kospi_gex_contents = importAllImages(
  require.context("assets/archive/kospi_gex", false, /\.(png|jpe?g|svg)$/)
);

const activities = {
  1: {
    title: "KOSPI Gamma Exposure",
    description: "Details about KOSPI Gamma Exposure project.",
    images: kospi_gex_contents,
  },
};

function ArchiveDetails() {
  React.useEffect(() => {
    document.body.classList.add("index-page");
    document.body.classList.add("sidebar-collapse");
    document.documentElement.classList.remove("nav-open");
    window.scrollTo(0, 0);
    document.body.scrollTop = 0;
    return function cleanup() {
      document.body.classList.remove("index-page");
      document.body.classList.remove("sidebar-collapse");
    };
  }, []);

  const { id } = useParams();
  const navigate = useNavigate(); // useNavigate 훅 사용
  const activity = activities[id];

  // Lightbox 상태 관리
  const [isOpen, setIsOpen] = useState(false);
  const [photoIndex, setPhotoIndex] = useState(0);

  // 모달 열릴 때 스크롤 최상단으로 이동
  useEffect(() => {
    if (isOpen) {
      window.scrollTo(0, 0); // 스크롤 최상단으로 이동
    }
  }, [isOpen]);

  if (!activity) {
    return <p>Activity not found.</p>;
  }

  return (
    <>
      <IndexNavbar />
      <div className="wrapper">
        <ArchiveHeader />
        <div className="main">
          <Container>
            {/* 이전으로 돌아가기 버튼 */}
            <BackButton onClick={() => navigate(-1)}></BackButton>
            <Header>{activity.title}</Header>
            <p>{activity.description}</p>
            <ImageGallery>
              {activity.images.map((image, index) => (
                <Image
                  key={index}
                  src={image}
                  alt={`Activity ${id} - ${index + 1}`}
                  onClick={() => {
                    setPhotoIndex(index); // 클릭한 이미지의 인덱스 저장
                    setIsOpen(true); // Lightbox 열기
                  }}
                />
              ))}
            </ImageGallery>
          </Container>
        </div>
        <DarkFooter />
      </div>

      {/* Lightbox 모달 */}
      {isOpen && (
        <Lightbox
          mainSrc={activity.images[photoIndex]} // 현재 이미지
          nextSrc={activity.images[(photoIndex + 1) % activity.images.length]} // 다음 이미지
          prevSrc={
            activity.images[
              (photoIndex + activity.images.length - 1) % activity.images.length
            ]
          } // 이전 이미지
          onCloseRequest={() => setIsOpen(false)} // 모달 닫기
          onMovePrevRequest={() =>
            setPhotoIndex(
              (photoIndex + activity.images.length - 1) % activity.images.length
            )
          } // 이전 이미지로 이동
          onMoveNextRequest={() =>
            setPhotoIndex((photoIndex + 1) % activity.images.length)
          } // 다음 이미지로 이동
        />
      )}
    </>
  );
}

export default ArchiveDetails;
