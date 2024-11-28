import React from "react";

// reactstrap components
import { Container, Row, Col } from "reactstrap";

// core components

function Typography() {
  return (
    <>
      <Container>
        <h3 className="title">Fistory</h3>
        <div id="history">
          <Row>
            <Col md="12">
              <div className="history-line">
              <span>2022</span>
                <h5>
                  경영대학 학술제 금상<br></br>(Option Pricing Method using FFNN)<br></br><br></br>
                  제 8회 DB GAPS 투자대회 <br></br> 금융동아리 부문 5위<br></br>
                  수익률 부문 TOP 20
                </h5>
              </div>
              <div className="history-line">
              <span>2021</span>
                <h5>
                  제 7회 DB GAPS 투자대회 본선 진출
                </h5>
              </div>
              <div className="history-line">
              <span>2018</span>
                <h5>
                  경영대학 학술제 대상 <br></br>(한반도 이슈에 따른 주가예측모델설계)
                </h5>
              </div>
              <div className="history-line">
              <span>2017</span>
                <h5>
                  제 3회 DB GAPS 투자대회<br></br>금융동아리 부문 5위<br></br>
                  수익률 부문 4위<br></br><br></br>
                  경영대학 학술제 은상<br></br><br></br>
                  따뜻한 시민금융아이디어 공모전 우수상
                </h5>
              </div>
              <div className="history-line">
              <span>2016</span>
                <h5>
                  경영대학 학술제 은상 수상
                </h5>
              </div>
              <div className="history-line">
              <span>2015</span>
                <h5>
                  경영대학 학술제 대상 <br></br>(내부자거래정보를 이용한 투자전략)
                </h5>
              </div>
              <div className="history-line">
              <span>2013</span>
                <h5>
                  FEPSI 창립
                </h5>
              </div>
            </Col>
          </Row>
        </div>
      </Container>
    </>
  );
}

export default Typography;
