import "./App.css";
import { Navbar, Container, Button } from "react-bootstrap";
import Table from "./Table";
import { useEffect, useState, useRef } from "react";
import results from "./marker-results.json";
import { keyToNameMapping, mergeTables } from "./keyToName";
import Info from "./Info";

import { Spinner } from "react-bootstrap";

import axios from "axios";
import Papa from "papaparse";
import { useStateWithCallbackLazy } from 'use-state-with-callback'
import { json_data_url, customer_data_url, download_url, generate_url, generate_report_url } from "./ApiPaths";


function App() {
  // Added
  const inpVal = useRef();
  const [loading, setLoading] = useState(true);
  const [customerData, setCustomerData] = useStateWithCallbackLazy(null);
  const [selectValue, setSelectValue] = useState("dog");
  const [marker_results, setMarkerResults] = useState();
  const [inputValue, setInputValue] = useState();
  const [customerFileExists, setCustomerFileExists] = useState(false);

  const [matrix_cols, setMatrixCols] = useState([]);
  const [matrix_data, setMatrixData] = useState([]);
  const [csv_uploaded_data, setCsvJsonData] = useStateWithCallbackLazy([]);
  const [reportingAndInterpretation, setReportingAndInterpretation] = useState(
    {}
  );
  const [selectedRows, setSelectedRows] = useState([]);

  const handleChange = (event) => {
    setCsvJsonData(event.target.files[0]);
    setInputValue(event.target.files[0].name);
  };

  const changeSetSelectedRows = (rowDetails) => {
    setSelectedRows(rowDetails);
  };

  const parseCsv = (data) => {
    setCustomerFileExists(true)

    Papa.parse(data, {
      complete: (res) => setTable(marker_results, res.data),
      header: true,
    })
  }

  // hook methods
  useEffect(() => {
    const list = results[Object.keys(results)];
    setReportingAndInterpretation(list[0].reportingAndInterpretation);
  }, [reportingAndInterpretation]);

  // Http Get
  const fetchCustomerDataFromApi = () => {
    // console.log("fetchCustomerDataFromApi")
    setLoading(true);
    let response = fetch(customer_data_url)
      .then((res) => res.json())
      .then((data) => {
        data = JSON.parse(data);

        setCustomerData(data);
      })
      .catch((err) => console.log("Refresh Error Occured"));
  };


  useEffect(() => {
    const fetchJsonDataFromApi = () => {
      console.log("fetchJsonDataFromApi")
      setLoading(true);
      let res = axios.get(json_data_url)
        .then((res) => {
          const data = JSON.parse(res.data)["sampleList"]

          console.log(data)

          setMarkerResults(data)
          setTable(data, []);
        })
        .catch((err) => console.log("Refresh Error Occured"));
    };

    fetchJsonDataFromApi();
    fetchCustomerDataFromApi();


  }, []);
  // Setting Table After getting data from api
  const setTable = (data, uploaded_data) => {
    const mergedData = mergeTables(data, uploaded_data);

    setReportingAndInterpretation(data.reportingAndInterpretation);
    setMatrixData(mergedData);
    setMatrixCols(Object.keys(keyToNameMapping));

    setLoading(false)
  };

  // Select Option Value Change Funciton
  const handleSelectChange = (e) => {
    setSelectValue(e.target.value);
  };

  const rerunButtonClicked = (e) => {
    e.preventDefault()
    setLoading(true);
    // console.log("rerunButtonClicked")
    axios
      .post(
        json_data_url,
        {
          file_number: selectValue === "dog" ? "1" : "2",
        },
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      )
      .then((res) => {
        const marker_results = [];
        const data = JSON.parse(res.data);

        data["sampleList"].forEach((i) => {
          marker_results.unshift(i);
        });

        setTable(marker_results, []);
      });
  };

  const customerDataUpload = (e) => {
    e.preventDefault();
    setLoading(true);

    var formData = new FormData();

    if (csv_uploaded_data.length === 0 || inpVal === undefined) {
      alert("These Fields are required");
      setLoading(false)
    } else {
      formData.append("note", inpVal.current);
      formData.append("customer_file", csv_uploaded_data);

      if (csv_uploaded_data.name.split(".")[1] === "csv") {
        axios
          .post(customer_data_url, formData, {
            headers: {
              'Content-Type': 'application/json',
              'Accept': 'application/json'
            },
          })
          .then((res) => {
            fetchCustomerDataFromApi();
            setInputValue("");

            parseCsv(csv_uploaded_data)
          });
      } else {
        alert("Please Upload a .csv file");
        setInputValue("");
        setLoading(false);

      }
    }
  };

  //custom methods
  const generateSelectedData = (sampleID, refrenceID) => {
    let filenumber = 1;
    let res = axios.post(generate_report_url, { filenumber,sampleID }, {
      headers: {
        'Content-Type': 'application/json; charset=utf-8'
      }
    })
      .then((res) => {
        console.log(res);
        alert("Report Generated Successfully!")
      })
      .catch((err) => console.log("Refresh Error Occured"));
  };

  const downloadData = () => {
    // console.log(selectedRows);

  };

  const generateReport = () => {
    // console.log(selectedRows);
    let filenumber = 1;
    let res = axios.post(generate_report_url, { filenumber }, {
      headers: {
        'Content-Type': 'application/json; charset=utf-8'
      }
    })
      .then((res) => {
        console.log(res)
        alert("Report Generated Successfully!")
      })
      .catch((err) => console.log("Refresh Error Occured"));
  };

  return loading === true ? (
    <div
      style={{
        height: "100vh",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
      }}
    >
      <Spinner animation="border" />{" "}
    </div>
  ) : (

    <div>
      <div className="page-title-wrapper">
        <div className="left-title">
          ION Torrent - AgriSeq Reporting and Interpretation Plugin
        </div>
        <div>
          <div className="thermo-fisher">ThermoFisher</div>
          <div className="scientific-title">SCIENTIFIC</div>
        </div>
      </div>
      <div className="summary-report-wrapper">
        <div className="summary">Select run instances to view summary</div>
        <div className="cover-analysis-wrapper" style={{ width: "60%" }}>
          <div className="textheading">
            <span className="textheading">Coverage Analysis: </span>

            <select name="pets" id="pet-select" style={{ width: "30%" }}>
              <option value="dog">#538</option>
              <option value="cat">#515</option>
              <option value="hamster">#511</option>
            </select>
          </div>
          <div className="textheading">
            <span className="textheading">Variant Caller: </span>

            <select name="pets" id="pet-select" style={{ width: "36%" }}>
              <option value="dog">#538</option>
              <option value="cat">#515</option>
              <option value="hamster">#511</option>
            </select>
          </div>
          <div className="textheading">
            <span className="textheading">AgriSum Toolkit: </span>

            <select
              onChange={handleSelectChange}
              value={selectValue}
              name="pets"
              id="pet-select"
              style={{ width: "33%" }}
            >
              {/* Use Other Files Here */}
              <option value="dog">
                Canine_Genotype matrix file_run07012022-2.xls
              </option>
              <option value="cat">
                693-R_2021_01_15_09_35_30_user_S5XL-0237-63-Genomia-Pilsen-canine-PITD-Matrix.xls
              </option>
            </select>
          </div>
          <button
            onClick={rerunButtonClicked}
            className="re-run-plugin-button"
          >
            Rerun Plugin
          </button>
        </div>
      </div>
      <div className="margins">
        <div className="agri-seq-wrapper">
          <div className="agri-seq-left-side-container">
            <h2>AgriSeq</h2>
            <h1>Reporting and Interpretation</h1>
            <div className="info-container">
              <Info reportingAndInterpretation={reportingAndInterpretation} />
            </div>
          </div>
          <div className="file-reader-wrapper">
            <div className="csv-upload-container">
              <h5>Upload Customer Data</h5>
              <div className="csv-file-wrapper">
                <b>CSV File: </b>

                <input
                  type="text"
                  id="file_name"
                  disabled={true}
                  style={{ width: "45%" }}
                  defaultValue={inputValue}
                />
                <input
                  className="csv-input"
                  type="file"
                  // ref={(input) => {
                  //   this.filesInput = input;
                  // }}
                  name="file"
                  placeholder={null}
                  style={{ display: "none" }}
                  onChange={handleChange}
                  id="getFile"
                />
                <button
                  className="csv-browse-button"
                  onClick={() => {
                    document.getElementById("getFile").click();
                  }}
                >
                  Browse...
                </button>
              </div>
              <div className="notes-wrapper">
                <b>Notes:</b>
                <input
                  type="text"
                  style={{ width: "76%" }}
                  // onChange={handleInpChange}
                  ref={inpVal}
                />
              </div>
              <button
                className="upload-file-button"
                onClick={customerDataUpload}

              >
                {" "}
                Upload File!
              </button>

              <h6>
                Files Uploaded{" "}
                <span style={{ color: "red" }}>
                  (Only last three displayed)
                </span>
              </h6>

              {customerData !== null ? customerData.map((e, index) => {
                return (
                  <p key={index}>
                    <i>
                      {e.fields.date_created.split("T")[0]}
                      &nbsp;&nbsp;
                      {e.fields.customer_file.split("/")[1]}
                    </i>
                  </p>
                );
              }) : ""}
            </div>
          </div>
        </div>

        <div className="pull-apart-max">
          <div className="">
            <div className="buttonswrapper">
              <div>
                <Button
                  className="faateh-button"
                  onClick={() => generateReport()}
                >
                  Generate Report
                </Button>
              </div>
              <div>
                <Button
                  className="faateh-button"
                  disabled={selectedRows.length === 0}
                >
                  Generate Selected
                </Button>
              </div>
              <div>
                <a
                  disabled={selectedRows.length === 0}
                >
                  <Button
                    className="faateh-button"
                    disabled={selectedRows.length === 0}
                  >
                    Download
                  </Button>
                </a>
              </div>
              <div>
                <Button
                  className="faateh-button"
                  disabled={selectedRows.length === 0}
                >
                  Email
                </Button>
              </div>
            </div>
          </div>
          <div className="filter-wrapper">
            <div>
              <label htmlFor="customer">
                <b>Customer:</b>
              </label>
              <select name="customer" id="customer">
                <option value="urban">Urban Animals</option>
                <option value="baif">BAIF</option>
              </select>
            </div>
            <div>
              <label htmlFor="panel">
                <b>Panel:</b>
              </label>
              <select name="panel" id="panel">
                <option value="canine">CanineTDv1</option>
                <option value="bovine">BovineTDv1</option>
              </select>
            </div>
          </div>
        </div>
        <Table
          name="DNA Table"
          data={matrix_data}
          columns={matrix_cols}
          changeSetSelectedRows={changeSetSelectedRows}
          filenumber={selectValue === "dog" ? 1 : 2}
          btnAvailable={!customerFileExists}

        />
      </div>
    </div>
  );
}

export default App;
