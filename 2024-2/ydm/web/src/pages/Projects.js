import React from "react";

// reactstrap components
// import {
// } from "reactstrap";

// core components
import IndexNavbar from "components/Navbars/IndexNavbar.js";
import ProjectsHeader from "components/Headers/ProjectsHeader.js";
import DarkFooter from "components/Footers/DarkFooter.js";

// sections for this page
import BasicElements from "views/projects-sections/BasicElements.js";
import Navbars from "views/projects-sections/Navbars.js";
import Tabs from "views/projects-sections/Tabs.js";
import Pagination from "views/projects-sections/Pagination.js";
import Notifications from "views/projects-sections/Notifications.js";
import Typography from "views/projects-sections/Typography.js";
import Javascript from "views/projects-sections/Javascript.js";
import Carousel from "views/projects-sections/Carousel.js";
import NucleoIcons from "views/projects-sections/NucleoIcons.js";
import CompleteExamples from "views/projects-sections/CompleteExamples.js";
import SignUp from "views/projects-sections/SignUp.js";
import Examples from "views/projects-sections/Examples.js";
import Download from "views/projects-sections/Download.js";
import Recruit from "views/projects-sections/recruit.js";
import Charts from "views/projects-sections/Charts.js";

function Projects() {
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
        <ProjectsHeader />
        <div className="main">
          <Charts />
          {/* <BasicElements /> */}
          {/* <Typography /> */}
          {/* <Recruit /> */}
          {/* <Navbars /> */}
          {/* <Tabs />
          <Pagination />
          <Notifications />
          <Javascript /> */}
          {/* <Carousel /> */}
          {/* <NucleoIcons />
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

export default Projects;
