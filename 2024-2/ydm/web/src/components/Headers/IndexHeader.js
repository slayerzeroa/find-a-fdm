/*eslint-disable*/
import React from "react";

// reactstrap components
import { Container } from "reactstrap";

// core components
import { StyleSheet, View, TouchableOpacity, Text } from "react-native";
import { colors, width, height } from "../../assets/config/globalStyles"; //width,height 받아오기

function IndexHeader() {
  let pageHeader = React.createRef();

  React.useEffect(() => {
    if (window.innerWidth > 991) {
      const updateScroll = () => {
        let windowScrollTop = window.pageYOffset / 3;
        pageHeader.current.style.transform =
          "translate3d(0," + windowScrollTop + "px,0)";
      };
      window.addEventListener("scroll", updateScroll);
      return function cleanup() {
        window.removeEventListener("scroll", updateScroll);
      };
    }
  });

  return (
    <>
      <div className="page-header clear-filter" filter-color="">
        <div
          className="page-header-image"
          style={{
            backgroundImage:
              "url(" + require("assets/img/index_header.jpg") + ")",
          }}
          ref={pageHeader}
        ></div>
        <Container>
          <div className="content-center brand" style={styles.header}>
            <p className="title">FIND-A</p>
          </div>
          <h6 className="category category-absolute">
            Designed by{" YDM"}. Coded by{" YDM"}.
          </h6>
        </Container>
      </div>
    </>
  );
}

export default IndexHeader;

const styles = StyleSheet.create({
  header: {
    fontSize: width * 11,
  },
});
