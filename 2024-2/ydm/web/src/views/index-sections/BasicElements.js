import React from "react";
// react plugin used to create switch buttons
import Switch from "react-bootstrap-switch";
// plugin that creates slider
import Slider from "nouislider";
import project1 from "../../assets/img/project1.jpg";
import project2_0 from "../../assets/img/project2_0.jpg";
import project2_1 from "../../assets/img/project2_1.jpg";
import project2_2 from "../../assets/img/project2_2.jpg";
import {colors, width, height} from '../../assets/config/globalStyles'; //width,height 받아오기

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
          <h3 className="title">Programming the World, Make Financial Engineers</h3>
          <h5>데이터분석을 통해 퀀트 전략을 검증하고, <br></br>퀀트 전략을 통해 수익을 창출합니다.</h5>
          
          <p className="category">We Cover</p>
          <Row>
            <Col md="10">
              <Button color="primary" type="button">
                Quantitative Trading/Research
              </Button>
              <Button color="danger" type="button">
                Block Chain
              </Button>
              <Button color="success" type="button">
                Web 3.0
              </Button>
              <Button color="warning" type="button">
                Data Analysis
              </Button>
            </Col>
          </Row>
          <p className="category">We Recruit</p>
          <Row>
            <Col md="10">
              <Button color="info" type="button">
                Front-End Developer
              </Button>
              <Button color="info" type="button">
                Block Chain Developer
              </Button>
              <Button color="info" type="button">
                Quantitative Researcher
              </Button>
            </Col>
          </Row>
          <p className="category">Our Goal</p>
          <Row>
            <Col md="20">
              <Button className="btn-neutral" color="default">
                High Performance, High Quality in the Financial Industry
              </Button>
            </Col>
          </Row>
          <p className="category">2023 Projects</p>
          <img src={project2_0} style={{Width:width, display: 'block', marginBottom: 10}}></img>
          <img src={project2_1} style={{Width:width, display: 'block', marginBottom: 10}}></img>
          <img src={project2_2} style={{Width:width, display: 'block', marginBottom: 10}}></img>
        </Container>
      </div>
    </>
  );
}

export default BasicElements;
