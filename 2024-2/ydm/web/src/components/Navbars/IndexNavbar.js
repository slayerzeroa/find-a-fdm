import React from "react";
import { Link } from "react-router-dom";
import { Tooltip } from "react-tooltip";
// reactstrap components
import {
  Button,
  Collapse,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
  UncontrolledDropdown,
  NavbarBrand,
  Navbar,
  NavItem,
  NavLink,
  Nav,
  Container,
  UncontrolledTooltip,
} from "reactstrap";

function IndexNavbar() {
  const [navbarColor, setNavbarColor] = React.useState("navbar-transparent");
  const [collapseOpen, setCollapseOpen] = React.useState(false);
  React.useEffect(() => {
    const updateNavbarColor = () => {
      if (
        document.documentElement.scrollTop > 399 ||
        document.body.scrollTop > 399
      ) {
        setNavbarColor("");
      } else if (
        document.documentElement.scrollTop < 400 ||
        document.body.scrollTop < 400
      ) {
        setNavbarColor("navbar-transparent");
      }
    };
    window.addEventListener("scroll", updateNavbarColor);
    return function cleanup() {
      window.removeEventListener("scroll", updateNavbarColor);
    };
  });
  return (
    <>
      {collapseOpen ? (
        <div
          id="bodyClick"
          onClick={() => {
            document.documentElement.classList.toggle("nav-open");
            setCollapseOpen(false);
          }}
        />
      ) : null}
      <Navbar className={"fixed-top " + navbarColor} expand="lg" color="info">
        <Container>
          <div className="navbar-translate">
            <NavLink
              to="/index"
              tag={Link}
              id="navbar-brand"
              style={{ fontSize: "250%" }}
            >
              FIND-A
            </NavLink>
            <UncontrolledTooltip target="#navbar-brand">
              금융데이터분석학회 FIND-A
            </UncontrolledTooltip>
            <button
              className="navbar-toggler navbar-toggler"
              onClick={() => {
                document.documentElement.classList.toggle("nav-open");
                setCollapseOpen(!collapseOpen);
              }}
              aria-expanded={collapseOpen}
              type="button"
            >
              <span className="navbar-toggler-bar top-bar"></span>
              <span className="navbar-toggler-bar middle-bar"></span>
              <span className="navbar-toggler-bar bottom-bar"></span>
            </button>
          </div>
          <Collapse
            className="justify-content-end"
            isOpen={collapseOpen}
            navbar
          >
            <Nav navbar>
              <NavItem>
                <NavLink to="/about" tag={Link}>
                  About FIND-A
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink to="/fdm" tag={Link}>
                  About FDM
                </NavLink>
              </NavItem>
              <NavItem>
                <NavLink to="/projects" tag={Link}>
                  Projects
                </NavLink>
              </NavItem>

              <NavItem
                data-tooltip-content="개발중입니다.. 뚠뚠.."
                id="activities"
              >
                <Tooltip
                  anchorId="activities"
                  place="top"
                  style={{ fontSize: "50%" }}
                />
                {/* <NavLink to="/activities" tag={Link}> */}
                <NavLink>Activities</NavLink>
              </NavItem>
              <NavItem>
                <NavLink to="/members" tag={Link}>
                  Members
                </NavLink>
              </NavItem>

              <NavItem
                data-tooltip-content="개발중입니다.. 뚠뚠.."
                id="contact"
              >
                <Tooltip
                  anchorId="contact"
                  place="top"
                  style={{ fontSize: "50%" }}
                />
                {/* <NavLink to="/contact" tag={Link}> */}
                <NavLink>Contact & Support</NavLink>
              </NavItem>
            </Nav>
          </Collapse>
        </Container>
      </Navbar>
    </>
  );
}

export default IndexNavbar;
