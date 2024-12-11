/*eslint-disable*/
import React from "react";

// reactstrap components
import { Container } from "reactstrap";

function DarkFooter() {
  return (
    <footer className="footer" data-background-color="black">
      <Container>
        <nav>
          <ul>
            <li>
              <a href="" target="_blank">
                FIND-A
              </a>
            </li>
            <li>
              <a href="https://find-a-ai.github.io/" target="_blank">
                Github-Blog
              </a>
            </li>
            <li>
              <a href="https://find-a-ai.github.io/" target="_blank">
                Contact Us: admin@finda-group.com
              </a>
            </li>
          </ul>
        </nav>
      </Container>
    </footer>
  );
}

export default DarkFooter;
