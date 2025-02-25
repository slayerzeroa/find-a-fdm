// /*!

// =========================================================
// * Black Dashboard React v1.2.2
// =========================================================

// * Product Page: https://www.creative-tim.com/product/black-dashboard-react
// * Copyright 2023 Creative Tim (https://www.creative-tim.com)
// * Licensed under MIT (https://github.com/creativetimofficial/black-dashboard-react/blob/master/LICENSE.md)

// * Coded by Creative Tim

// =========================================================

// * The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

// */
// import React, { useEffect, useState } from "react";
// import axios from "axios";

// // nodejs library that concatenates classes
// import classNames from "classnames";
// // react plugin used to create charts
// import { Line, Bar } from "react-chartjs-2";

// // reactstrap components
// import {
//   Button,
//   ButtonGroup,
//   Card,
//   CardHeader,
//   CardBody,
//   CardTitle,
//   DropdownToggle,
//   DropdownMenu,
//   DropdownItem,
//   UncontrolledDropdown,
//   Label,
//   FormGroup,
//   Input,
//   Table,
//   Row,
//   Col,
//   UncontrolledTooltip,
// } from "reactstrap";

// // core components
// import {
//   chartExample1,
//   chartExample2,
//   chartExample3,
//   chartExample4,
// } from "variables/charts.js";

// function Dashboard(props) {
//   const [bigChartData, setbigChartData] = React.useState("data1");
//   const [chartData, setChartData] = useState([]);

//   const setBgChartData = (name) => {
//     setbigChartData(name);
//   };

//   // Fetch data from API
//   useEffect(() => {
//     const fetchData = async () => {
//       try {
//         const response = await axios.get("http://localhost:3000/gex");
//         setChartData(response.data); // API 데이터 저장
//       } catch (error) {
//         console.error("Error fetching data:", error);
//       }
//     };

//     fetchData();
//   }, []);

//   return (
//     <>
//       <div className="content">
//         <Row>
//           <Col xs="12">
//             <Card className="card-chart">
//               <CardHeader>
//                 <Row>
//                   <Col className="text-left" sm="6">
//                     <h5 className="card-category">Total Shipments</h5>
//                     <CardTitle tag="h2">Performance</CardTitle>
//                   </Col>
//                   <Col sm="6">
//                     <ButtonGroup
//                       className="btn-group-toggle float-right"
//                       data-toggle="buttons"
//                     >
//                       <Button
//                         tag="label"
//                         className={classNames("btn-simple", {
//                           active: bigChartData === "data1",
//                         })}
//                         color="info"
//                         id="0"
//                         size="sm"
//                         onClick={() => setBgChartData("data1")}
//                       >
//                         <span className="d-none d-sm-block d-md-block d-lg-block d-xl-block">
//                           Accounts
//                         </span>
//                         <span className="d-block d-sm-none">
//                           <i className="tim-icons icon-single-02" />
//                         </span>
//                       </Button>
//                       <Button
//                         color="info"
//                         id="1"
//                         size="sm"
//                         tag="label"
//                         className={classNames("btn-simple", {
//                           active: bigChartData === "data2",
//                         })}
//                         onClick={() => setBgChartData("data2")}
//                       >
//                         <span className="d-none d-sm-block d-md-block d-lg-block d-xl-block">
//                           Purchases
//                         </span>
//                         <span className="d-block d-sm-none">
//                           <i className="tim-icons icon-gift-2" />
//                         </span>
//                       </Button>
//                       <Button
//                         color="info"
//                         id="2"
//                         size="sm"
//                         tag="label"
//                         className={classNames("btn-simple", {
//                           active: bigChartData === "data3",
//                         })}
//                         onClick={() => setBgChartData("data3")}
//                       >
//                         <span className="d-none d-sm-block d-md-block d-lg-block d-xl-block">
//                           Sessions
//                         </span>
//                         <span className="d-block d-sm-none">
//                           <i className="tim-icons icon-tap-02" />
//                         </span>
//                       </Button>
//                     </ButtonGroup>
//                   </Col>
//                 </Row>
//               </CardHeader>
//               <CardBody>
//                 <div className="chart-area">
//                   <Line
//                     data={chartExample1[bigChartData]}
//                     options={chartExample1.options}
//                   />
//                 </div>
//               </CardBody>
//             </Card>
//           </Col>
//         </Row>
//         <Row>
//           <Col lg="4">
//             <Card className="card-chart">
//               <CardHeader>
//                 <h5 className="card-category">Total Shipments</h5>
//                 <CardTitle tag="h3">
//                   <i className="tim-icons icon-bell-55 text-info" /> 763,215
//                 </CardTitle>
//               </CardHeader>
//               <CardBody>
//                 <div className="chart-area">
//                   <Line
//                     data={chartExample2.data}
//                     options={chartExample2.options}
//                   />
//                 </div>
//               </CardBody>
//             </Card>
//           </Col>
//           <Col lg="4">
//             <Card className="card-chart">
//               <CardHeader>
//                 <h5 className="card-category">Daily Sales</h5>
//                 <CardTitle tag="h3">
//                   <i className="tim-icons icon-delivery-fast text-primary" />{" "}
//                   3,500€
//                 </CardTitle>
//               </CardHeader>
//               <CardBody>
//                 <div className="chart-area">
//                   <Bar
//                     data={chartExample3.data}
//                     options={chartExample3.options}
//                   />
//                 </div>
//               </CardBody>
//             </Card>
//           </Col>
//           <Col lg="4">
//             <Card className="card-chart">
//               <CardHeader>
//                 <h5 className="card-category">Completed Tasks</h5>
//                 <CardTitle tag="h3">
//                   <i className="tim-icons icon-send text-success" /> 12,100K
//                 </CardTitle>
//               </CardHeader>
//               <CardBody>
//                 <div className="chart-area">
//                   <Line
//                     data={chartExample4.data}
//                     options={chartExample4.options}
//                   />
//                 </div>
//               </CardBody>
//             </Card>
//           </Col>
//         </Row>
//         <Row>
//           <Col lg="6" md="12">
//             <Card className="card-tasks">
//               <CardHeader>
//                 <h6 className="title d-inline">Tasks(5)</h6>
//                 <p className="card-category d-inline"> today</p>
//                 <UncontrolledDropdown>
//                   <DropdownToggle
//                     caret
//                     className="btn-icon"
//                     color="link"
//                     data-toggle="dropdown"
//                     type="button"
//                   >
//                     <i className="tim-icons icon-settings-gear-63" />
//                   </DropdownToggle>
//                   <DropdownMenu aria-labelledby="dropdownMenuLink" right>
//                     <DropdownItem
//                       href="#pablo"
//                       onClick={(e) => e.preventDefault()}
//                     >
//                       Action
//                     </DropdownItem>
//                     <DropdownItem
//                       href="#pablo"
//                       onClick={(e) => e.preventDefault()}
//                     >
//                       Another action
//                     </DropdownItem>
//                     <DropdownItem
//                       href="#pablo"
//                       onClick={(e) => e.preventDefault()}
//                     >
//                       Something else
//                     </DropdownItem>
//                   </DropdownMenu>
//                 </UncontrolledDropdown>
//               </CardHeader>
//               <CardBody>
//                 <div className="table-full-width table-responsive">
//                   <Table>
//                     <tbody>
//                       <tr>
//                         <td>
//                           <FormGroup check>
//                             <Label check>
//                               <Input defaultValue="" type="checkbox" />
//                               <span className="form-check-sign">
//                                 <span className="check" />
//                               </span>
//                             </Label>
//                           </FormGroup>
//                         </td>
//                         <td>
//                           <p className="title">Update the Documentation</p>
//                           <p className="text-muted">
//                             Dwuamish Head, Seattle, WA 8:47 AM
//                           </p>
//                         </td>
//                         <td className="td-actions text-right">
//                           <Button
//                             color="link"
//                             id="tooltip636901683"
//                             title=""
//                             type="button"
//                           >
//                             <i className="tim-icons icon-pencil" />
//                           </Button>
//                           <UncontrolledTooltip
//                             delay={0}
//                             target="tooltip636901683"
//                             placement="right"
//                           >
//                             Edit Task
//                           </UncontrolledTooltip>
//                         </td>
//                       </tr>
//                       <tr>
//                         <td>
//                           <FormGroup check>
//                             <Label check>
//                               <Input
//                                 defaultChecked
//                                 defaultValue=""
//                                 type="checkbox"
//                               />
//                               <span className="form-check-sign">
//                                 <span className="check" />
//                               </span>
//                             </Label>
//                           </FormGroup>
//                         </td>
//                         <td>
//                           <p className="title">GDPR Compliance</p>
//                           <p className="text-muted">
//                             The GDPR is a regulation that requires businesses to
//                             protect the personal data and privacy of Europe
//                             citizens for transactions that occur within EU
//                             member states.
//                           </p>
//                         </td>
//                         <td className="td-actions text-right">
//                           <Button
//                             color="link"
//                             id="tooltip457194718"
//                             title=""
//                             type="button"
//                           >
//                             <i className="tim-icons icon-pencil" />
//                           </Button>
//                           <UncontrolledTooltip
//                             delay={0}
//                             target="tooltip457194718"
//                             placement="right"
//                           >
//                             Edit Task
//                           </UncontrolledTooltip>
//                         </td>
//                       </tr>
//                       <tr>
//                         <td>
//                           <FormGroup check>
//                             <Label check>
//                               <Input defaultValue="" type="checkbox" />
//                               <span className="form-check-sign">
//                                 <span className="check" />
//                               </span>
//                             </Label>
//                           </FormGroup>
//                         </td>
//                         <td>
//                           <p className="title">Solve the issues</p>
//                           <p className="text-muted">
//                             Fifty percent of all respondents said they would be
//                             more likely to shop at a company
//                           </p>
//                         </td>
//                         <td className="td-actions text-right">
//                           <Button
//                             color="link"
//                             id="tooltip362404923"
//                             title=""
//                             type="button"
//                           >
//                             <i className="tim-icons icon-pencil" />
//                           </Button>
//                           <UncontrolledTooltip
//                             delay={0}
//                             target="tooltip362404923"
//                             placement="right"
//                           >
//                             Edit Task
//                           </UncontrolledTooltip>
//                         </td>
//                       </tr>
//                       <tr>
//                         <td>
//                           <FormGroup check>
//                             <Label check>
//                               <Input defaultValue="" type="checkbox" />
//                               <span className="form-check-sign">
//                                 <span className="check" />
//                               </span>
//                             </Label>
//                           </FormGroup>
//                         </td>
//                         <td>
//                           <p className="title">Release v2.0.0</p>
//                           <p className="text-muted">
//                             Ra Ave SW, Seattle, WA 98116, SUA 11:19 AM
//                           </p>
//                         </td>
//                         <td className="td-actions text-right">
//                           <Button
//                             color="link"
//                             id="tooltip818217463"
//                             title=""
//                             type="button"
//                           >
//                             <i className="tim-icons icon-pencil" />
//                           </Button>
//                           <UncontrolledTooltip
//                             delay={0}
//                             target="tooltip818217463"
//                             placement="right"
//                           >
//                             Edit Task
//                           </UncontrolledTooltip>
//                         </td>
//                       </tr>
//                       <tr>
//                         <td>
//                           <FormGroup check>
//                             <Label check>
//                               <Input defaultValue="" type="checkbox" />
//                               <span className="form-check-sign">
//                                 <span className="check" />
//                               </span>
//                             </Label>
//                           </FormGroup>
//                         </td>
//                         <td>
//                           <p className="title">Export the processed files</p>
//                           <p className="text-muted">
//                             The report also shows that consumers will not easily
//                             forgive a company once a breach exposing their
//                             personal data occurs.
//                           </p>
//                         </td>
//                         <td className="td-actions text-right">
//                           <Button
//                             color="link"
//                             id="tooltip831835125"
//                             title=""
//                             type="button"
//                           >
//                             <i className="tim-icons icon-pencil" />
//                           </Button>
//                           <UncontrolledTooltip
//                             delay={0}
//                             target="tooltip831835125"
//                             placement="right"
//                           >
//                             Edit Task
//                           </UncontrolledTooltip>
//                         </td>
//                       </tr>
//                       <tr>
//                         <td>
//                           <FormGroup check>
//                             <Label check>
//                               <Input defaultValue="" type="checkbox" />
//                               <span className="form-check-sign">
//                                 <span className="check" />
//                               </span>
//                             </Label>
//                           </FormGroup>
//                         </td>
//                         <td>
//                           <p className="title">Arival at export process</p>
//                           <p className="text-muted">
//                             Capitol Hill, Seattle, WA 12:34 AM
//                           </p>
//                         </td>
//                         <td className="td-actions text-right">
//                           <Button
//                             color="link"
//                             id="tooltip217595172"
//                             title=""
//                             type="button"
//                           >
//                             <i className="tim-icons icon-pencil" />
//                           </Button>
//                           <UncontrolledTooltip
//                             delay={0}
//                             target="tooltip217595172"
//                             placement="right"
//                           >
//                             Edit Task
//                           </UncontrolledTooltip>
//                         </td>
//                       </tr>
//                     </tbody>
//                   </Table>
//                 </div>
//               </CardBody>
//             </Card>
//           </Col>
//           <Col lg="6" md="12">
//             <Card>
//               <CardHeader>
//                 <CardTitle tag="h4">Simple Table</CardTitle>
//               </CardHeader>
//               <CardBody>
//                 <Table className="tablesorter" responsive>
//                   <thead className="text-primary">
//                     <tr>
//                       <th>Name</th>
//                       <th>Country</th>
//                       <th>City</th>
//                       <th className="text-center">Salary</th>
//                     </tr>
//                   </thead>
//                   <tbody>
//                     <tr>
//                       <td>Dakota Rice</td>
//                       <td>Niger</td>
//                       <td>Oud-Turnhout</td>
//                       <td className="text-center">$36,738</td>
//                     </tr>
//                     <tr>
//                       <td>Minerva Hooper</td>
//                       <td>Curaçao</td>
//                       <td>Sinaai-Waas</td>
//                       <td className="text-center">$23,789</td>
//                     </tr>
//                     <tr>
//                       <td>Sage Rodriguez</td>
//                       <td>Netherlands</td>
//                       <td>Baileux</td>
//                       <td className="text-center">$56,142</td>
//                     </tr>
//                     <tr>
//                       <td>Philip Chaney</td>
//                       <td>Korea, South</td>
//                       <td>Overland Park</td>
//                       <td className="text-center">$38,735</td>
//                     </tr>
//                     <tr>
//                       <td>Doris Greene</td>
//                       <td>Malawi</td>
//                       <td>Feldkirchen in Kärnten</td>
//                       <td className="text-center">$63,542</td>
//                     </tr>
//                     <tr>
//                       <td>Mason Porter</td>
//                       <td>Chile</td>
//                       <td>Gloucester</td>
//                       <td className="text-center">$78,615</td>
//                     </tr>
//                     <tr>
//                       <td>Jon Porter</td>
//                       <td>Portugal</td>
//                       <td>Gloucester</td>
//                       <td className="text-center">$98,615</td>
//                     </tr>
//                   </tbody>
//                 </Table>
//               </CardBody>
//             </Card>
//           </Col>
//         </Row>
//       </div>
//     </>
//   );
// }

// export default Dashboard;

// 코드 리팩토링

import React, { useEffect, useState } from "react";
import axios from "axios";
import classNames from "classnames";
import { Line, Bar } from "react-chartjs-2";
import {
  Button,
  ButtonGroup,
  Card,
  CardHeader,
  CardBody,
  CardTitle,
  Row,
  Col,
  Table,
  FormGroup,
  Label,
  Input,
  UncontrolledDropdown,
  DropdownToggle,
  DropdownMenu,
  DropdownItem,
} from "reactstrap";
import {
  chartExample1,
  chartExample2,
  chartExample3,
  chartExample4,
} from "variables/charts.js";

const Dashboard = (props) => {
  const [bigChartData, setbigChartData] = useState("data1");
  const [chartData, setChartData] = useState([]);

  const setBgChartData = (name) => setbigChartData(name);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get("http://localhost:8001/gex");
        setChartData(response.data);
      } catch (error) {
        console.error("Error fetching data:", error);
      }
    };

    fetchData();
  }, []);

  return (
    <div className="content">
      <Row>
        <Col xs="12">
          <Card className="card-chart">
            <CardHeader>
              <Row>
                <Col className="text-left" sm="6">
                  <h5 className="card-category">Total Shipments</h5>
                  <CardTitle tag="h2">Performance</CardTitle>
                </Col>
                <Col sm="6" className="d-flex justify-content-end">
                  <ButtonGroup
                    className="btn-group-toggle float-right"
                    data-toggle="buttons"
                  >
                    <Button
                      tag="label"
                      className={classNames("btn-simple", {
                        active: bigChartData === "data1",
                      })}
                      color="info"
                      id="0"
                      size="sm"
                      onClick={() => setBgChartData("data1")}
                    >
                      <span className="d-none d-sm-block d-md-block d-lg-block d-xl-block">
                        Accounts
                      </span>
                      <span className="d-block d-sm-none">
                        <i className="tim-icons icon-single-02" />
                      </span>
                    </Button>
                    <Button
                      color="info"
                      id="1"
                      size="sm"
                      tag="label"
                      className={classNames("btn-simple", {
                        active: bigChartData === "data2",
                      })}
                      onClick={() => setBgChartData("data2")}
                    >
                      <span className="d-none d-sm-block d-md-block d-lg-block d-xl-block">
                        Purchases
                      </span>
                      <span className="d-block d-sm-none">
                        <i className="tim-icons icon-gift-2" />
                      </span>
                    </Button>
                    <Button
                      color="info"
                      id="2"
                      size="sm"
                      tag="label"
                      className={classNames("btn-simple", {
                        active: bigChartData === "data3",
                      })}
                      onClick={() => setBgChartData("data3")}
                    >
                      <span className="d-none d-sm-block d-md-block d-lg-block d-xl-block">
                        Sessions
                      </span>
                      <span className="d-block d-sm-none">
                        <i className="tim-icons icon-tap-02" />
                      </span>
                    </Button>
                  </ButtonGroup>
                </Col>
              </Row>
            </CardHeader>
            <CardBody>
              <div className="chart-area">
                <Line
                  data={chartExample1[bigChartData]}
                  options={chartExample1.options}
                />
              </div>
            </CardBody>
          </Card>
        </Col>
      </Row>
      <Row>
        <Col lg="4">
          <Card className="card-chart">
            <CardHeader>
              <h5 className="card-category">GEX</h5>
              <CardTitle tag="h3">
                <i className="tim-icons icon-bell-55 text-info" /> 763,215
              </CardTitle>
            </CardHeader>
            <CardBody>
              <div className="chart-area">
                <Line
                  data={{
                    labels: chartData.map((item) => item.DATE), // x축 레이블로 DATE 사용
                    datasets: [
                      {
                        label: "NET_GEX",
                        data: chartData.map((item) => item.NET_GEX), // y축 데이터로 NET_GEX 사용
                        borderColor: "#1f8ef1",
                        backgroundColor: "rgba(29,140,248,0.2)",
                        pointBackgroundColor: "#1f8ef1",
                        fill: true,
                      },
                    ],
                  }}
                  options={chartExample2.options}
                />
              </div>
            </CardBody>
          </Card>
        </Col>
        <Col lg="4">
          <Card className="card-chart">
            <CardHeader>
              <h5 className="card-category">Daily Sales</h5>
              <CardTitle tag="h3">
                <i className="tim-icons icon-delivery-fast text-primary" />{" "}
                $3,500
              </CardTitle>
            </CardHeader>
            <CardBody>
              <div className="chart-area">
                <Bar
                  data={chartExample3.data}
                  options={chartExample3.options}
                />
              </div>
            </CardBody>
          </Card>
        </Col>
        <Col lg="4">
          <Card className="card-chart">
            <CardHeader>
              <h5 className="card-category">Completed Tasks</h5>
              <CardTitle tag="h3">
                <i className="tim-icons icon-send text-success" /> 12,100K
              </CardTitle>
            </CardHeader>
            <CardBody>
              <div className="chart-area">
                <Line
                  data={chartExample4.data}
                  options={chartExample4.options}
                />
              </div>
            </CardBody>
          </Card>
        </Col>
      </Row>
      <Row>
        <Col lg="6" md="12">
          <Card className="card-tasks">
            <CardHeader>
              <h6 className="title d-inline">Tasks(5)</h6>
              <p className="card-category d-inline"> today</p>
              <UncontrolledDropdown>
                <DropdownToggle
                  caret
                  className="btn-icon"
                  color="link"
                  data-toggle="dropdown"
                >
                  <i className="tim-icons icon-settings-gear-63" />
                </DropdownToggle>
                <DropdownMenu right>
                  <DropdownItem onClick={(e) => e.preventDefault()}>
                    Action
                  </DropdownItem>
                  <DropdownItem onClick={(e) => e.preventDefault()}>
                    Another action
                  </DropdownItem>
                  <DropdownItem onClick={(e) => e.preventDefault()}>
                    Something else
                  </DropdownItem>
                </DropdownMenu>
              </UncontrolledDropdown>
            </CardHeader>
            <CardBody>
              <div className="table-full-width table-responsive">
                <Table>
                  <tbody>
                    {Array.from({ length: 5 }, (_, idx) => (
                      <tr key={idx}>
                        <td>
                          <FormGroup check>
                            <Label check>
                              <Input type="checkbox" />
                              <span className="form-check-sign">
                                <span className="check" />
                              </span>
                            </Label>
                          </FormGroup>
                        </td>
                        <td>
                          <p className="title">Task {idx + 1}</p>
                          <p className="text-muted">
                            Description of task {idx + 1}
                          </p>
                        </td>
                        <td className="td-actions text-right">
                          <Button color="link">
                            <i className="tim-icons icon-pencil" />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              </div>
            </CardBody>
          </Card>
        </Col>
        <Col lg="6" md="12">
          <Card>
            <CardHeader>
              <CardTitle tag="h4">Simple Table</CardTitle>
            </CardHeader>
            <CardBody>
              <Table className="tablesorter" responsive>
                <thead className="text-primary">
                  <tr>
                    <th>Name</th>
                    <th>Country</th>
                    <th>City</th>
                    <th className="text-center">Salary</th>
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td>Dakota Rice</td>
                    <td>Niger</td>
                    <td>Oud-Turnhout</td>
                    <td className="text-center">$36,738</td>
                  </tr>
                  <tr>
                    <td>Minerva Hooper</td>
                    <td>Curaçao</td>
                    <td>Sinaai-Waas</td>
                    <td className="text-center">$23,789</td>
                  </tr>
                  <tr>
                    <td>Sage Rodriguez</td>
                    <td>Netherlands</td>
                    <td>Baileux</td>
                    <td className="text-center">$56,142</td>
                  </tr>
                </tbody>
              </Table>
            </CardBody>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
