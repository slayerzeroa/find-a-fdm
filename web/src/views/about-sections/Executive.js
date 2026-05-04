import React from "react";
import { Container, Row, Col, Button } from "reactstrap";
import Tistory from "../../assets/img/tistory.svg";

function Executive() {
  return (
    <div className="section section-team text-center">
      <Container>
        <h2 className="title">Here is our Executives</h2>
        <div className="team">
          <Row>
            <Col md="4">
              <div className="team-player">
                <img
                  alt="..."
                  className="rounded-circle img-fluid img-raised"
                  src={require("assets/img/KKM.png")}
                ></img>
                <h4 className="title">김강민</h4>
                <p className="category text-info">부회장</p>
                <p className="description">
                  안녕하세요:) 저는 FEPSI 부회장을 맡고 있는 김강민입니다.
                  여러분과 잊지 못할 추억을 만들고 싶습니다. 잘 부탁드립니다 😆{" "}
                </p>
              </div>
            </Col>
            <Col md="4">
              <div className="team-player">
                <img
                  alt="..."
                  className="rounded-circle img-fluid img-raised"
                  src={require("assets/img/YDM.gif")}
                ></img>
                <h4 className="title">유대명</h4>
                <p className="category text-info">회장</p>
                <p className="description">
                  되면 한다<br></br>
                  즐길 수 없으면 피해라<br></br>
                  몸이 나쁘면 머리가 고생한다<br></br>{" "}
                </p>
                <a href="https://github.com/slayerzeroa">
                  <Button className="btn-icon btn-round" color="">
                    <img
                      src={require("../../assets/img/github.png")}
                      width="100%"
                      height="100%"
                    />
                  </Button>
                </a>
                <a href="https://www.linkedin.com/in/%EB%8C%80%EB%AA%85-%EC%9C%A0-625084183/">
                  <Button className="btn-icon btn-round" color="">
                    <img
                      src={require("../../assets/img/linkedin.png")}
                      width="100%"
                      height="100%"
                    />
                  </Button>
                </a>
                <a href="https://blog.naver.com/slayerzeroa">
                  <Button className="btn-icon btn-round" color="">
                    <img
                      src={require("../../assets/img/naver.png")}
                      width="100%"
                      height="100%"
                    />
                  </Button>
                </a>
                <a href="https://stockduck.tistory.com/">
                  <Button className="btn-icon btn-round" color="">
                    <img src={Tistory} width="100%" />
                  </Button>
                </a>
              </div>
            </Col>
            <Col md="4">
              <div className="team-player">
                <img
                  alt="..."
                  className="rounded-circle img-fluid img-raised"
                  src={require("assets/img/LGC.png")}
                ></img>
                <h4 className="title">이건창</h4>
                <p className="category text-info">총무</p>
                <p className="description">
                  안녕하세요.<br></br>
                  금융공학도 이건창입니다.<br></br>
                  반갑습니다.<br></br>
                </p>
              </div>
            </Col>
          </Row>
        </div>
      </Container>
    </div>
  );
}

export default Executive;
