import React from "react";
import {
  Container,
  Row,
  Col,
  Input,
  InputGroupAddon,
  InputGroupText,
  InputGroup,
  Button,
} from "reactstrap";

function Contact() {
  const [firstFocus, setFirstFocus] = React.useState(false);
  const [lastFocus, setLastFocus] = React.useState(false);
  return (
    <div className="section section-contact-us text-center">
      <Container>
        <h2 className="title">Want to contact us?</h2>
        <p className="description">FEPSI는 항상 열려있습니다.</p>
        <Row>
          <Col className="text-center ml-auto mr-auto" lg="6" md="8">
            <InputGroup
              className={"input-lg" + (firstFocus ? " input-group-focus" : "")}
            >
              <InputGroupAddon addonType="prepend">
                <InputGroupText>
                  <i className="now-ui-icons users_circle-08"></i>
                </InputGroupText>
              </InputGroupAddon>
              <Input
                placeholder="이름을 작성해주세요"
                type="text"
                onFocus={() => setFirstFocus(true)}
                onBlur={() => setFirstFocus(false)}
              ></Input>
            </InputGroup>
            <InputGroup
              className={"input-lg" + (lastFocus ? " input-group-focus" : "")}
            >
              <InputGroupAddon addonType="prepend">
                <InputGroupText>
                  <i className="now-ui-icons ui-1_email-85"></i>
                </InputGroupText>
              </InputGroupAddon>
              <Input
                placeholder="Email을 작성해주세요"
                type="text"
                onFocus={() => setLastFocus(true)}
                onBlur={() => setLastFocus(false)}
              ></Input>
            </InputGroup>
            <div className="textarea-container">
              <Input
                cols="80"
                name="name"
                placeholder="Type a message..."
                rows="4"
                type="textarea"
              ></Input>
            </div>
            <div className="send-button">
              <Button
                block
                className="btn-round"
                color="info"
                href="#pablo"
                onClick={(e) => e.preventDefault()}
                size="lg"
              >
                Send Message
              </Button>
            </div>
          </Col>
        </Row>
      </Container>
    </div>
  );
}

export default Contact;
