import React from "react";
// react plugin used to create switch buttons
import Switch from "react-bootstrap-switch";
// plugin that creates slider
import Slider from "nouislider";

// reactstrap components
import {
  Button,
  Label,
  FormGroup,
  Input,
  InputGroupAddon,
  InputGroupText,
  InputGroup,
  Container,
  Row,
  Col,
} from "reactstrap";

// core components

function BasicElements() {
  const [leftFocus, setLeftFocus] = React.useState(false);
  const [rightFocus, setRightFocus] = React.useState(false);
  // React.useEffect(() => {
  //   if (
  //     !document
  //       .getElementById("sliderRegular")
  //       .classList.contains("noUi-target")
  //   ) {
  //     Slider.create(document.getElementById("sliderRegular"), {
  //       start: [50],
  //       connect: [true, false],
  //       step: 0.5,
  //       range: { min: 0, max: 100 },
  //     });
  //   }
  //   if (
  //     !document.getElementById("sliderDouble").classList.contains("noUi-target")
  //   ) {
  //     Slider.create(document.getElementById("sliderDouble"), {
  //       start: [20, 80],
  //       connect: [false, true, false],
  //       step: 1,
  //       range: { min: 0, max: 100 },
  //     });
  //   }
  // });
  return (
    <>
      <div className="section section-basic" id="basic-elements">
        <Container>
        <br></br>
          <Button className="btn-neutral" color="default"  type="button" size="lg" style={{fontSize:"150%"}}>
            What is Financial Engineering?
          </Button>
          <br></br>
          <Button color="info" type="button" size="lg">
            Abstract
          </Button>
          <h5>금융공학은 일반적인 금융이론과 경제학, 미적분학, 통계학,
            프로그래밍 등을 기반으로 한 융합적인 학문입니다.
            금융공학은 금융시장의 특성을 파악하고, 이를 통해 합리적인 투자전략을
            수립하고, 이를 구현하는 것을 목표로 하거나
            논리적으로 금융상품을 개발하고, 리스크를 관리하는 것을 목표로 합니다.
            <br></br><br></br>
            금융공학은 금융세계로의 모험입니다. 금융시장을 수학적으로 모델링하고,
            새로운 투자 상품을 제시하거나 기존의 상품을 개선시킵니다.
            금융시장의 특성을 수학적으로 파악하고, 이를 통해 합리적인 투자전략을 제시하여 투자자의
            이익을 증대시킵니다.
            <br></br><br></br>
          </h5>
          <Button color="warning" type="button" size="lg">
          Business
          </Button>
          <h5>
            가장 큰 비즈니스는 파생상품 시장(선물, 옵션, 기타 파생)에서
            이루어집니다. 사실 많은 사람들이 주식시장에서 투자를 하지만, 주식시장은
            금융공학의 커다란 비즈니스는 아닙니다. 파생상품 시장은 금융공학과의
            상품 개발 능력 및 투자전략을 적용할 수 있는 가장 좋은 시장입니다.
            금융공학은 고객에게 알맞은 구조화된 파생상품을 개발하여 판매하고, 수익을 창출합니다.
            <br></br><br></br>
            금융공학은 리스크 관리를 통해 예기치 못한 위기를 최대한 예방하고, 금융시장의 안정성을
            유지하기 위한 노력을 통해 금융시장의 효율성을 높이기도 합니다. 금융감독원에서는 금융공학
            직렬을 매년 채용하고 있으며, 금융시장에서 일어나는 다양한 사건들을 정량적으로 분석하고,
            이를 통해 금융시장의 안정성을 유지하기 위한 노력을 하고 있습니다. 그 외에도 다양한
            금융기관(증권사, 자산운용사, 금융공기업)에서도 퀀트를 채용하고 있습니다.
            <br></br><br></br>
            자동매매 시스템을 개발하여, 자동으로 매매를 하는 퀀트 전략을 개발하는 것도 금융공학의 일부분입니다.
            아직 한국에서는 퀀트 전략을 기반으로 한 자동매매가 많이 쓰이지 않지만, 미국과 유럽에서는
            이미 많이 쓰이고 있습니다. 퀀트 전략을 기반으로 한 자동매매는 투자자의 주관적인 판단을
            배제하고, 수학적인 방법을 통해 매매를 하기 때문에, 투자자의 주관적인 판단에 의한 오류를
            줄여줄 수 있다는 장점이 있습니다. 또한, 퀀트 전략을 기반으로 한 자동매매는 투자자가
            투자를 하는 시간에 상관없이, 투자를 할 수 있기 때문에, 투자자의 투자 시간을 줄여줄 수
            있다는 장점이 있습니다.
            <br></br><br></br>
            블록체인을 이용하여 금융시장의 보안성을 높이는 것도 최근 금융공학에서 다루어지고 있는
            주제입니다. 블록체인은 금융시장에서 거래를 하는 데 있어서 중개인의 개입 없이 거래를
            할 수 있도록 해주는 기술입니다. 블록체인을 이용하여 거래를 할 경우, 거래를 하는 두
            사람이 거래를 하는 데 있어서 중개인의 개입 없이 거래를 할 수 있기 때문에, 수수료를
            절약할 수 있고 보안성을 높일 수 있습니다.
          </h5>
          <br></br>
          <Button color="primary" type="button" size="lg">
          Quant
          </Button>
          <h5>
            Quantitative Analyst(Quant)는 넓은 의미로 수학을 실용적인 분석을 위해 사용하는 모든 사람을 뜻합니다.
            하지만 주로 좁은 의미로 금융시장에서 정량적 분석을 하는 사람들을 의미합니다.
            <br></br><br></br>
            Quant의 종류는 생각보다 다양합니다.
            <br></br>
            직접적으로 투자를 하는 Quant Trader,
            <br></br>
            금융상품을 만드는 Desk Quant,
            <br></br>
            투자의 위험을 관리하는 Risk Quant,
            <br></br>
            금융공학적 지식을 프로그래밍하여 구현하는 Quant Developer 등이 있습니다.
          </h5>
        </Container>
      </div>
    </>
  );
}

export default BasicElements;
