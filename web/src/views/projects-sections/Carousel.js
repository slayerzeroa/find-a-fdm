import React from "react";
import { useTable } from 'react-table';

// reactstrap components
import {
  Container,
  Row,
  Col,
  Carousel,
  CarouselItem,
  CarouselIndicators
} from "reactstrap";

// core components

const items = [
  {
    src: require("assets/img/linka.png"),
    altText: "Linka - A Blockchain based alumni network",
    caption: "Linka - A Blockchain based alumni network",
    alignself: "flex-start"
  },
  {
    src: require("assets/img/FIL.png"),
    altText: "FIL - Curriculum Management System",
    caption: "FIL - Curriculum Management System",
    alignself: "flex-start"
  },
  {
    src: require("assets/img/FIN_BERT.png"),
    altText: "FIN-BERT - Financial Expressions Classification and Relation Extraction",
    caption: "FIN-BERT - Financial Expressions Classification and Relation Extraction",
    alignself: "flex-start"
  }
  ,
  {
    src: require("assets/img/Auto_Trading.png"),
    altText: "Upbit Auto Trading Bot",
    caption: "Upbit Auto Trading Bot",
    alignself: "flex-start"
  }
];

function CarouselSection() {
  const [activeIndex, setActiveIndex] = React.useState(0);
  const [animating, setAnimating] = React.useState(false);
  const onExiting = () => {
    setAnimating(true);
  };
  const onExited = () => {
    setAnimating(false);
  };
  const next = () => {
    if (animating) return;
    const nextIndex = activeIndex === items.length - 1 ? 0 : activeIndex + 1;
    setActiveIndex(nextIndex);
  };
  const previous = () => {
    if (animating) return;
    const nextIndex = activeIndex === 0 ? items.length - 1 : activeIndex - 1;
    setActiveIndex(nextIndex);
  };
  const goToIndex = (newIndex) => {
    if (animating) return;
    setActiveIndex(newIndex);
  };
  return (
    <>
      <div className="section" id="carousel">
        <Container>
          <div className="title">
            <h4>Current Projects</h4>
          </div >
          <Row className="justify-content-center">
            <Col lg="10" md="12">
              <Carousel
                activeIndex={activeIndex}
                next={next}
                previous={previous}
              >
                <CarouselIndicators
                  items={items}
                  activeIndex={activeIndex}
                  onClickHandler={goToIndex}
                />
                {items.map((item) => {
                  return (
                    <CarouselItem
                      onExiting={onExiting}
                      onExited={onExited}
                      key={item.src}
                    >
                      <img src={item.src} alt={item.altText} />
                      <div className="carousel-caption d-none d-md-block">
                        <h5 style={{backgroundColor:'black'}}>{item.caption}</h5>
                      </div>
                    </CarouselItem>
                  );
                })}
                <a
                  className="carousel-control-prev"
                  data-slide="prev"
                  href="#pablo"
                  onClick={(e) => {
                    e.preventDefault();
                    previous();
                  }}
                  role="button"
                >
                  <i className="now-ui-icons arrows-1_minimal-left"></i>
                </a>
                <a
                  className="carousel-control-next"
                  data-slide="next"
                  href="#pablo"
                  onClick={(e) => {
                    e.preventDefault();
                    next();
                  }}
                  role="button"
                >
                  <i className="now-ui-icons arrows-1_minimal-right"></i>
                </a>
              </Carousel>
            </Col>
            <h4>FEPSI는 NLP, Blockchain, Trading Algorithm, Website Design 등
              <br></br>
              다양한 분야에서 장기적인 프로젝트를 진행하고 있습니다.
              <br></br><br></br>
              프로젝트에 참여하며 소학회원들은 자신의 역량을 높이고, 포트폴리오를 구축할 수 있습니다.
              <br></br><br></br>
              FEPSI는 매년 다양한 금융공모전과 해커톤에 참여하며, 성과를 내고 있습니다.
              </h4>
              
          </Row>  
        </Container>
      </div>
    </>
  );
}

export default CarouselSection;
