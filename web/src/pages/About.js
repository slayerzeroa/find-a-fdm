import React from "react";
import { Route, Link } from "react-router-dom";

// reactstrap components
import {
  Button,
  Input,
  InputGroupAddon,
  InputGroupText,
  InputGroup,
  Container,
  Row,
  Col,
} from "reactstrap";

// core components
import IndexNavbar from "components/Navbars/IndexNavbar.js";
import AboutHeader from "components/Headers/AboutHeader.js";
import DefaultFooter from "components/Footers/DefaultFooter.js";
import DarkFooter from "components/Footers/DarkFooter";
import { ReactComponent as TistoryIcon } from "../assets/img/tistory.svg";

// views components
import Introduce from "../views/about-sections/Introduce.js";
import Executive from "../views/about-sections/Executive.js";
import Contact from "../views/about-sections/Contact.js";

function About() {
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
  return (
    <>
      <IndexNavbar />
      <div className="wrapper">
        <AboutHeader />
        <div className="main">
          {/* <Introduce /> */}
          {/* <Executive /> */}
          {/* <Contact /> */}
        </div>
        <DarkFooter />
      </div>
    </>
  );
}

export default About;
