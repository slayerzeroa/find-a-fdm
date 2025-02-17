// import React from "react";

// // reactstrap components
// // import {
// // } from "reactstrap";

// // core components
// import IndexNavbar from "components/Navbars/IndexNavbar.js";
// import ArchiveHeader from "components/Headers/ArchiveHeader.js";
// import DarkFooter from "components/Footers/DarkFooter.js";

// // sections for this page
// import BasicElements from "views/fe-sections/BasicElements.js";
// import Navbars from "views/fe-sections/Navbars.js";
// import Tabs from "views/fe-sections/Tabs.js";
// import Pagination from "views/fe-sections/Pagination.js";
// import Notifications from "views/fe-sections/Notifications.js";
// import Typography from "views/fe-sections/Typography.js";
// import Javascript from "views/fe-sections/Javascript.js";
// import Carousel from "views/fe-sections/Carousel.js";
// import NucleoIcons from "views/fe-sections/NucleoIcons.js";
// import CompleteExamples from "views/fe-sections/CompleteExamples.js";
// import SignUp from "views/fe-sections/SignUp.js";
// import Examples from "views/fe-sections/Examples.js";
// import Download from "views/fe-sections/Download.js";
// import Recruit from "views/fe-sections/recruit.js";
// import ArchiveLanding from "views/archive-sections/ArchiveLanding";

// function Archive() {
//   React.useEffect(() => {
//     document.body.classList.add("index-page");
//     document.body.classList.add("sidebar-collapse");
//     document.documentElement.classList.remove("nav-open");
//     window.scrollTo(0, 0);
//     document.body.scrollTop = 0;
//     return function cleanup() {
//       document.body.classList.remove("index-page");
//       document.body.classList.remove("sidebar-collapse");
//     };
//   });
//   return (
//     <>
//       <IndexNavbar />
//       <div className="wrapper">
//         <ArchiveHeader />
//         <div className="main">
//           <ArchiveLanding />
//           {/* <BasicElements /> */}
//           {/* <Typography /> */}
//           {/* <Recruit /> */}
//           {/* <Navbars /> */}
//           {/* <Tabs /> */}
//           {/* <Pagination />
//           <Notifications />
//           <Javascript />
//           <Carousel />
//           <NucleoIcons />
//           <CompleteExamples />
//           <SignUp />
//           <Examples />
//           <Download /> */}
//         </div>
//         <DarkFooter />
//       </div>
//     </>
//   );
// }

// export default Archive;

// import React from "react";
// import { Routes, Route } from "react-router-dom";

// // core components
// import IndexNavbar from "components/Navbars/IndexNavbar.js";
// import ArchiveHeader from "components/Headers/ArchiveHeader.js";
// import DarkFooter from "components/Footers/DarkFooter.js";

// // views
// import ArchiveLanding from "views/archive-sections/ArchiveLanding";
// import ArchiveDetails from "views/archive-sections/ArchiveDetails";

// function Archive() {
//   React.useEffect(() => {
//     document.body.classList.add("index-page");
//     document.body.classList.add("sidebar-collapse");
//     document.documentElement.classList.remove("nav-open");
//     window.scrollTo(0, 0);
//     document.body.scrollTop = 0;
//     return function cleanup() {
//       document.body.classList.remove("index-page");
//       document.body.classList.remove("sidebar-collapse");
//     };
//   }, []);

//   return (
//     <>
//       <IndexNavbar />
//       <div className="wrapper">
//         <ArchiveHeader />
//         <div className="main">
//           {/* React Router를 사용해 ArchiveLanding과 ArchiveDetail을 조건적으로 렌더링 */}
//           <Routes>
//             <Route path="/" element={<ArchiveLanding />} />
//             <Route path="/:id" element={<ArchiveDetails />} />
//           </Routes>
//         </div>
//         <DarkFooter />
//       </div>
//     </>
//   );
// }

// export default Archive;

import React from "react";
import { Routes, Route } from "react-router-dom";

// core components
import IndexNavbar from "components/Navbars/IndexNavbar.js";
import ArchiveHeader from "components/Headers/ArchiveHeader.js";
import DarkFooter from "components/Footers/DarkFooter.js";

// views
import ArchiveLanding from "views/archive-sections/ArchiveLanding";
// import ArchiveDetails from "views/archive-sections/ArchiveDetails";

function Archive() {
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
      {/* Navbar와 Header는 항상 표시 */}
      <IndexNavbar />
      <div className="wrapper">
        <ArchiveHeader />
        <div className="main">
          {/* Routes로 ArchiveLanding과 ArchiveDetail을 전환 */}
          <Routes>
            <Route path="/" element={<ArchiveLanding />} />
            {/* <Route path="/:id" element={<ArchiveDetails />} /> */}
          </Routes>
        </div>
        {/* Footer는 항상 표시 */}
        <DarkFooter />
      </div>
    </>
  );
}

export default Archive;
