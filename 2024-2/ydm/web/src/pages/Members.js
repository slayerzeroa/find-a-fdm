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

import Membercards from "views/members-sections/Membercards";

function Members() {
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
          <Membercards />
          {/* <Introduce /> */}
          {/* <Executive /> */}
          {/* <Contact /> */}
        </div>
        <DarkFooter />
      </div>
    </>
  );
}

export default Members;
