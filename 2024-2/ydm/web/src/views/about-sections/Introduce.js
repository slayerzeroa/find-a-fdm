import React from "react";
import { Container, Row, Col } from "reactstrap";

function Introduce() {
  return (
    <div className="section section-about-us">
      <Container>
        <Row>
          <Col className="ml-auto mr-auto text-center" md="8">
            <h2 className="title">FEPSI</h2>
            <h5 className="description">
              아주대학교 금융공학과 프로그래밍 소학회 FEPSI는 <br></br>
              다양한 분야에서 지식을 쌓고 이를 직접 구현하며, 아이디어를
              도출하고 있습니다.<br></br>
              (Quantitative Research, BlockChain, Machine Learning, Data
              Science)<br></br>
              <br></br>
              <br></br>
              2013년 설립되어, 10년간의 놀라운 성장을 거쳐 <br></br>High
              Performance in Financial Industry를 지향하는 소학회로 나아가고
              있습니다.
            </h5>
          </Col>
        </Row>
        <div className="separator separator-primary"></div>
        <div className="section-story-overview">
          <Row>
            <Col md="6">
              <div
                className="image-container image-left"
                style={{
                  backgroundImage:
                    "url(" + require("assets/img/login.jpg") + ")",
                }}
              >
                <h2>Go High</h2>
                <p className="blockquote blockquote-info">
                  높은 목표는 홀로 오르기 어렵습니다. 팀을 만들어 각자의 역할을
                  다할 때 더 높이 갈 수 있습니다.
                  <br></br>
                  <br></br>FEPSI는 여러분들이 더 높은 곳으로 갈 수 있도록
                  지원하고, 함께 갑니다.<br></br>
                </p>
              </div>
              <div
                className="image-container"
                style={{
                  backgroundImage:
                    "url(" + require("assets/img/skyscrapers.jpg") + ")",
                }}
              >
                <h2 style={{ color: "white" }}>In Financial Industry</h2>
              </div>
            </Col>
            <Col md="5">
              <div
                className="image-container image-right"
                style={{
                  backgroundImage:
                    "url(" + require("assets/img/with_us.jpg") + ")",
                }}
              >
                <h2 style={{ color: "white" }}>With Us</h2>
              </div>

              <h3>
                급변하는 금융시장에서 장기적으로 높은 성과를 내는 것은 쉽지
                않습니다<br></br>
              </h3>
              <p>
                FEPSI는 금융공학과 학우들이 금융시장의 변화에 대응하고, 단단한
                기초를 바탕으로 높은 성과를 내는 것을 목표로 합니다.
                금융공학과의 수업내용을 바탕으로 금융시장의 변화에 대응하고, 더
                나아가 새로운 접근을 탐구하여 높은 성과를 내는 것을 목표로
                합니다. 단순히 수업을 듣고 과제를 제출하는 것이 아닌, 자신만의
                아이디어를 토대로 금융시장에 대한 연구를 진행하고, 프로젝트를
                진행하여 실제로 적용할 수 있는 결과물을 만들어냅니다.
              </p>
              <p>
                Python, R, C++, JavaScript 등 다양한 언어를 활용하여 퀀트 분석,
                블록체인, 머신러닝, 데이터 사이언스 등 다양한 분야에 대한 연구를
                진행하고 있습니다. 교내 활동에 더하여 다양한 금융 공모전,
                해커톤에 참여할 수 있도록 지원합니다. 매주 소학회원들과 함께
                프로젝트, 알고리즘에 대한 토론을 진행하여 자신의 의견을
                논리적으로 주장하는 능력을 기르고, 서로의 아이디어를 공유합니다.
              </p>
              <p>
                삼성전자, 카카오, LG 등 이미 개발자로서의 커리어를 시작한
                선배님들과 증권사, 자산운용사, 대학원에서 금융인으로서의
                커리어를 시작하신 선배님들의 끈끈한 아주대 금융공학 네트워크를
                통해 취업에 대한 도움을 받을 수 있습니다.
              </p>
            </Col>
          </Row>
        </div>
      </Container>
    </div>
  );
}

export default Introduce;
