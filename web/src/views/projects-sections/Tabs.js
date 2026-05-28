import React from "react";

// reactstrap components
import {
  Card,
  CardHeader,
  CardBody,
  NavItem,
  NavLink,
  Nav,
  TabContent,
  TabPane,
  Container,
  Row,
  Col,
} from "reactstrap";

// core components

function Tabs() {
  const [iconPills, setIconPills] = React.useState("1");
  const [pills, setPills] = React.useState("1");
  return (
    <>
      <div className="section section-tabs">
      <Container>
      <h3 className="category">Abilities for Financial Engineering</h3>
      </Container>
        <Container>
          <Row>
            <Col className="ml-auto mr-auto" md="10" xl="6">
              <p className="category">Core Abilities</p>
              <Card>
                <CardHeader>
                  <Nav className="justify-content-center" role="tablist" tabs>
                    <NavItem>
                      <NavLink
                        className={iconPills === "1" ? "active" : ""}
                        href="#pablo"
                        onClick={(e) => {
                          e.preventDefault();
                          setIconPills("1");
                        }}
                      >
                        <img src={require("../../assets/img/mathematics_negative.png")} style={{width:'10%'}}></img>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Mathematics
                      </NavLink>
                    </NavItem>
                    <NavItem>
                      <NavLink
                        className={iconPills === "2" ? "active" : ""}
                        href="#pablo"
                        onClick={(e) => {
                          e.preventDefault();
                          setIconPills("2");
                        }}
                      >
                        <img src={require("../../assets/img/finance_negative.png")} style={{width:'10%'}}></img>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Finance
                      </NavLink>
                    </NavItem>
                    <NavItem>
                      <NavLink
                        className={iconPills === "3" ? "active" : ""}
                        href="#pablo"
                        onClick={(e) => {
                          e.preventDefault();
                          setIconPills("3");
                        }}
                      >
                        <img src={require("../../assets/img/economics_negative.png")} style={{width:'10%'}}></img>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Economics
                      </NavLink>
                    </NavItem>
                    <NavItem>
                      <NavLink
                        className={iconPills === "4" ? "active" : ""}
                        href="#pablo"
                        onClick={(e) => {
                          e.preventDefault();
                          setIconPills("4");
                        }}
                      >
                        <img src={require("../../assets/img/coding_negative.png")} style={{width:'10%'}}></img>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Programmings
                      </NavLink>
                    </NavItem>
                  </Nav>
                </CardHeader>
                <CardBody>
                  <TabContent
                    className="text-center"
                    activeTab={"iconPills" + iconPills}
                  >
                    <TabPane tabId="iconPills1">
                      <p>
                        수학은 금융공학의 핵심적인 역량입니다. 금융공학은 수학적인
                        지식을 기반으로 하고 있으며, 수학적인 지식을 통해
                        금융시장의 동작원리를 이해합니다.
                        금융공학과에서도 미적분학, 고급통계, 선형대수학,
                        미분방정식, 해석학 등 수학 과목을 배웁니다.
                        <br></br><br></br>
                        예시를 들면 옵션의 가격을 결정하는 블랙-숄즈 모형은 확률미분방정식을 기반으로
                        하고 있습니다. 따라서 시장의 옵션 가격을 블랙-숄즈 모형에 넣어 결정되는
                        내재 변동성도 수학적으로 결정됩니다. 수학과 금융이 밀접한 관계를 가지고 있음을
                        알 수 있습니다.
                        <br></br><br></br>
                        그 외에도 미래 가치(FV)를 현재 가치(PV)로 변환하거나,
                        옵션 상품의 현금흐름을 고려할 때, 장단기 금리 차의 부트스트랩을 진행할 때, 등등
                        금융시장의 수많은 상황에서 수학이 이용됩니다.

                      </p>
                    </TabPane>
                    <TabPane tabId="iconPills2">
                      <p>
                        금융에 대한 이해는 금융공학을 더욱 효과적으로 이용할 수 있도록
                        도와줍니다. 금융시장과 금융상품들의 특징을 이해하여 금융공학을
                        어떻게 적용할 수 있을지 생각해볼 수 있습니다. 예를 들면, 금융시장에서
                        발생하는 위험은 어떤 것들이 있을까요?
                        <br></br><br></br>
                        금융시장에서 발생하는 위험은 시장위험, 신용위험, 기업위험, 통화위험, 이자율위험 등이 있습니다.
                        금융공학에서는 이러한 위험들을 어떻게 측정하고 관리할 수 있을지
                        고민합니다.
                        <br></br><br></br>
                        금융공학에서는 위험을 측정하는 방법 중 하나로 VaR(Value at
                        Risk)을 이용합니다. VaR은 특정 기간 동안 신뢰수준에서 발생가능한 최대손실금액을 의미합니다.
                        예를 들어, 99% 신뢰수준의 1일 VaR이 1,000만원이라면
                        1일 동안의 손실이 1,000만원은 넘지 않는데, 그 확률은 99%입니다. 이러한
                        VaR을 이용하여 금융상품의 위험을 측정하고 관리할 수 있습니다.
                      </p>
                    </TabPane>
                    <TabPane tabId="iconPills3">
                      <p>
                        경제학은 금융공학의 기초가 되는 학문입니다. 경제학은
                        생산과 분배, 소비, 국제거래 등을 다루는 학문입니다.
                        수입 수출이 어떻게 국가의 경제에 영향을
                        미치는지, 국가의 경제성장률은 어떻게 측정하는지 등을
                        경제학에서 배울 수 있습니다.
                        <br></br><br></br>
                        금융공학에서는 경제학을 기초로 시장에서 발생하는 다양한 현상들을
                        설명하고 분석합니다. 인플레이션으로 변동하는 금리가 금융시장에 어떻게, 얼마나 영향을
                        미치는지, 정부의 정책이 금융시장에 어떤 영향을 주고, 그곳에서 어떻게 알파를 찾을 수 있을지
                        등을 경제학에서 배운 지식을 바탕으로 분석합니다.
                      </p>
                    </TabPane>
                    <TabPane tabId="iconPills4">
                      <p>
                        프로그래밍은 금융공학의 꽃입니다. 금융공학에서는
                        다양한 금융상품들을 분석하고, 그 상품들을 이용하여
                        수익을 창출하는 것이 목표입니다. 이러한 분석과 수익창출을
                        위해서는 프로그래밍이 필수적입니다. 프로그래밍을 통해
                        자신의 전략을 구현하고, 그 전략을 테스트하고, 그 전략을
                        자동화할 수 있습니다.
                        <br></br><br></br>
                        몬테카를로 시뮬레이션을 통해 주가 시뮬레이션을
                        구현하고, 그 주가 시뮬레이션을 통해 적정 옵션 가격을
                        계산하고, 그 옵션 가격을 통해 옵션 전략을 구현할 수도
                        있습니다.
                        <br></br><br></br>
                        데이터분석을 통해 주가 데이터를 수집하고, 그 데이터를
                        통해 주가의 특성을 파악하고, 특성을 통해 주가의
                        변동성, 기대 수익률을 계산해 적절한 포트폴리오를 구성할 수도 있습니다.
                        <br></br><br></br>
                        금융공학에서는  C++, Python, R 등 다양한 프로그래밍 언어를 사용합니다.
                      </p>
                    </TabPane>
                  </TabContent>
                </CardBody>
              </Card>
            </Col>
            <Col className="ml-auto mr-auto" md="10" xl="6">
              <p className="category">Sub Abilities</p>
              <Card>
                <CardHeader>
                  <Nav
                    className="nav-tabs-neutral justify-content-center"
                    data-background-color="blue"
                    role="tablist"
                    tabs
                  >
                    <NavItem>
                      <NavLink
                        className={pills === "1" ? "active" : ""}
                        href="#pablo"
                        onClick={(e) => {
                          e.preventDefault();
                          setPills("1");
                        }}
                      >
                        <img src={require("../../assets/img/communication_negative.png")} style={{width:'10%'}}></img>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Communication
                      </NavLink>
                    </NavItem>
                    <NavItem>
                      <NavLink
                        className={pills === "2" ? "active" : ""}
                        href="#pablo"
                        onClick={(e) => {
                          e.preventDefault();
                          setPills("2");
                        }}
                      >
                        <img src={require("../../assets/img/logic_negative.png")} style={{width:'10%'}}></img>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Logic
                      </NavLink>
                    </NavItem>
                    <NavItem>
                      <NavLink
                        className={pills === "3" ? "active" : ""}
                        href="#pablo"
                        onClick={(e) => {
                          e.preventDefault();
                          setPills("3");
                        }}
                      >
                        <img src={require("../../assets/img/patience_negative.png")} style={{width:'10%'}}></img>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Patience
                      </NavLink>
                    </NavItem>
                    <NavItem>
                      <NavLink
                        className={pills === "4" ? "active" : ""}
                        href="#pablo"
                        onClick={(e) => {
                          e.preventDefault();
                          setPills("4");
                        }}
                      >
                        <img src={require("../../assets/img/challenge_negative.png")} style={{width:'10%'}}></img>
                        &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;Challenge
                      </NavLink>
                    </NavItem>
                  </Nav>
                </CardHeader>
                <CardBody>
                  <TabContent
                    className="text-center"
                    activeTab={"pills" + pills}
                  >
                    <TabPane tabId="pills1">
                      <p>
                        고독하기만 할 것같은 금융공학이지만, 사실 다른 사람들과의
                        커뮤니케이션 능력은 금융공학을 자신의 업으로써 삼을 때 가장 중요한 능력입니다.
                        <br></br><br></br>
                        결국 금융공학도 비즈니스 속에서 일을 하게 되는데, 그 일을 하기 위해서는
                        다른 사람들과의 커뮤니케이션이 필수적입니다. 자신이 개발한 모델이나
                        알고리즘을 다른 사람들에게 설명하고, 설득하면서 조직의 효율적인 의사결정을
                        도울 수 있어야 합니다.
                        <br></br><br></br>
                        또한, 금융공학은 다양한 분야의 지식을 필요로 하기 때문에
                        다른 사람들과의 커뮤니케이션을 통해 다양한 분야의 지식을 얻어야 합니다.
                        다양한 사람들에게서 다양한 지식을 얻어 새로운 아이디어를 창출할 수 있습니다.
                      </p>
                    </TabPane>
                    <TabPane tabId="pills2">
                      <p>
                        논리적인 사고를 통해 문제를 해결하는 것은 금융공학에서 중요한 능력입니다.
                        의사결정에 앞서 논리적으로 판단할 수 있다면 더욱 효율적이고 정확한 의사결정을
                        할 수 있습니다.
                        <br></br><br></br>
                        논리적인 사고는 금융시장에서 발생하는 다양한 문제를 해결하는 데에도 중요한 능력입니다.
                        문제의 원인을 파악하고, 문제를 해결하기 위한 최선의 방법을 찾아낼 때 논리적인 사고가
                        큰 도움을 줍니다.
                        <br></br><br></br>
                        또한, 다양한 분야의 지식을 논리적으로 연결하는 것은 금융공학에서 중요한 능력입니다.
                        다양한 분야의 지식을 논리적으로 연결하여 새로운 아이디어를 창출할 수 있습니다.

                      </p>
                    </TabPane>
                    <TabPane tabId="pills3">
                      <p>
                        인내심은 금융공학을 위해 필요한 다양하고도 깊은 역량을 기르는데에 중요한 역할을 합니다.
                        금융공학은 다양한 분야의 지식을 필요로 하기 때문에 다양한 분야의 지식을 습득하기 위해서는
                        많은 시간과 노력이 필요합니다.
                        <br></br><br></br>
                        인내심은 이런 과정에서 필요합니다. 자신이 원하는 것을 얻기 위해 오랜시간 끊임없이 노력하고
                        노력한 결과를 기다려야 합니다. 역경을 극복하고, 실패를 극복하는 과정에서 큰 성장을 이룰 수 있습니다.
                        <br></br><br></br>
                        자신이 세운 전략이 잘못되었다면, 그것을 극복하기 위해 노력하고,
                        전략이 옳다면, 그것을 믿고 결과를 기다리는 것이 중요합니다.

                      </p>
                    </TabPane>
                    <TabPane tabId="pills4">
                      <p>
                        금융시장에 대한 도전정신이 필요합니다. 금융시장은 불확실성이 높고, 변화가 빠르기 때문에
                        항상 새로운 환경에 적응하고 해결방안을 모색해야 합니다.
                        <br></br><br></br>
                        다양한 리스크 요소들을 극복하고, 금융시장에서 생존하기 위해서는 새로운 것을 두려워하지 않고
                        직접 부딪힐 수 있는 용기가 필요합니다.
                        <br></br><br></br>
                        새로운 환경에 도전적으로 접근하고, 새로운 것을 시도하고, 새로운 실패를 극복하는 것은 금융공학을 계속 공부하는데 도움이 됩니다.
                      </p>
                    </TabPane>
                  </TabContent>
                </CardBody>
              </Card>
            </Col>
          </Row>
        </Container>
      </div>
    </>
  );
}

export default Tabs;
