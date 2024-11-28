import React from "react";

// reactstrap components
// import {
// } from "reactstrap";

// core components
import IndexNavbar from "components/Navbars/IndexNavbar.js";
import FdmHeader from "components/Headers/FdmHeader.js";
import DarkFooter from "components/Footers/DarkFooter.js";

// sections for this page
import BasicElements from "views/fe-sections/BasicElements.js";
import Navbars from "views/fe-sections/Navbars.js";
import Tabs from "views/fe-sections/Tabs.js";
import Pagination from "views/fe-sections/Pagination.js";
import Notifications from "views/fe-sections/Notifications.js";
import Typography from "views/fe-sections/Typography.js";
import Javascript from "views/fe-sections/Javascript.js";
import Carousel from "views/fe-sections/Carousel.js";
import NucleoIcons from "views/fe-sections/NucleoIcons.js";
import CompleteExamples from "views/fe-sections/CompleteExamples.js";
import SignUp from "views/fe-sections/SignUp.js";
import Examples from "views/fe-sections/Examples.js";
import Download from "views/fe-sections/Download.js";
import Recruit from "views/fe-sections/recruit.js";

function Fdm() {
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
  });
  return (
    <>
      <IndexNavbar />
      <div className="wrapper">
        <FdmHeader />
        <div className="main">
          {/* <BasicElements /> */}
          {/* <Typography /> */}
          {/* <Recruit /> */}
          {/* <Navbars /> */}
          {/* <Tabs /> */}
          {/* <Pagination />
          <Notifications />
          <Javascript />
          <Carousel />
          <NucleoIcons />
          <CompleteExamples />
          <SignUp />
          <Examples />
          <Download /> */}
        </div>
        <DarkFooter />
      </div>
    </>
  );
}

export default Fdm;
