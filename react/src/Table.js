// import { Table, Button } from 'react-bootstrap';
import { useState, useEffect } from "react";
import "./App.css";
import { styled } from "@mui/material/styles";
import Table from "@mui/material/Table";
import TableBody from "@mui/material/TableBody";
import TableCell, { tableCellClasses } from "@mui/material/TableCell";
import TableContainer from "@mui/material/TableContainer";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import Paper from "@mui/material/Paper";
import { Button } from "@mui/material";
import axios from "axios";
import { download_url, generate_url,generate_specific_report_url } from "./ApiPaths";


const StyledTableRow = styled(TableRow)(({ theme }) => ({
  "&:nth-of-type(even)": {
    backgroundColor: theme.palette.action.hover,
  },
  // hide last border
  "&:last-child td, &:last-child th": {
    border: 0,
  },
}));
const StyledTableCell = styled(TableCell)(({ theme }) => ({
  [`&.${tableCellClasses.head}`]: {
    backgroundColor: theme.palette.action.hover,
    color: theme.palette.common.white,
  },
  [`&.${tableCellClasses.body}`]: {
    fontSize: 14,
  },
}));

function AttributesTable(props) {
  const gunnarStyle = { height: "35px", padding: "0px 10px" };
  const { data, columns, changeSetSelectedRows, filenumber, btnAvailable } = props;

  const [buttonClickInfo, setButtonClickInfo] = useState({ "clicked": false, "index": -1 });

  const [show, setShow] = useState(false);
  const [rowInfo, setCurrentRowInfo] = useState({});
  const [activeParent, setActiveParent] = useState(false);
  const [active, setActive] = useState(null);

  useEffect(() => {
    let a = [];
    for (var i = 0; i < data?.length; i++) {
      a.push(false);
    }
    setActive(a);
    // console.log("data", data);
  }, []);

  useEffect(() => {
    if (activeParent) {
      changeSetSelectedRows(data);
    } else {
      changeSetSelectedRows([]);
    }
  }, [activeParent]);

  useEffect(() => {
    if (active) {
      let res = [];
      Object.values(active).forEach((state, index) => {
        if (state) {
          res.push(data[index]);
        }
      });
      changeSetSelectedRows(res);
    }
  }, [active]);

  const handleClose = () => {
    setCurrentRowInfo({});
    setShow(false);
  };

  const handleShow = (rowInfo) => {
    setCurrentRowInfo(rowInfo);
    setShow(true);
  };

  const handleChange = (index) => {
    const activeTemp = Object.assign({}, active);
    activeTemp[index] = !active[index];
    setActive(activeTemp);
    setActiveParent(false);
  };

  const handleChangeParent = () => {
    let a = [];
    for (var i = 0; i < data?.length; i++) {
      a.push(!activeParent);
    }
    setActive(a);
    setActiveParent(!activeParent);
  };

  const onClickGenerate = (e, sampleID, refrenceID) => {
    e.stopPropagation();
    let filenumber = 1;
    let res = axios.post(generate_specific_report_url, { filenumber,sampleID }, {
      headers: {
        'Content-Type': 'application/json; charset=utf-8'
      }
    })
      .then((res) => {
        console.log(res)
        alert("Report Generated Successfully!")
      })
      .catch((err) => console.log("Refresh Error Occured"));
    // axios
    // .get(`${generate_url}${sampleID}/${refrenceID}/${filenumber}/`, {
    //   headers : { 
    //     'Content-Type': 'application/json'
    //    },
    //   responseType: 'blob',
    // })
    // .then((res) => {
    //   const url = window.URL.createObjectURL(new Blob([res.data]));
    //   console.log(url)
    //   const link = document.createElement('a');
    //   link.href = url;
    //   link.setAttribute('download', `${sampleID}.json`); //or any other extension
    //   document.body.appendChild(link);
    //   link.click();
    //   document.body.removeChild(link)
    // });
  };

  const onClickDownload = (e) => {
    e.stopPropagation();
    axios
      .post(download_url, filenumber, {
        headers: {
          'Content-Type': 'application/json; charset=utf-8'
        },
        responseType: 'blob',
      })
      .then((res) => {
        var fileDownload = require('js-file-download');
        fileDownload(res.data, 'report.pdf');

      });
  };

  const onClickEmail = (e) => {
    e.stopPropagation();
    console.log("only generate and no modal");
  };

  const makeHeader = () => {
    return (
      <thead>
        <tr>
          <th>
            <input
              type="checkbox"
              onClick={handleChangeParent}
              checked={activeParent}
            />
          </th>
          {columns.map((colName, index) => {
            return (
              <th style={{ minWidth: "100px" }} key={index}>
                {colName}
              </th>
            );
          })}
          <th style={{ maxWidth: "2em", textAlign: "center" }}>Actions</th>
        </tr>
      </thead>
    );
  };

  const makeBody = () => {
    if (data.length === 0) {
      return null;
    }
    return (
      <tbody>
        {data.map((row, index) => {
          return (
            <tr key={index}>
              <input
                type="checkbox"
                onClick={() => handleChange(index)}
                checked={(active && active[index]) || activeParent}
              />
              {Object.values(row).map((val, index) => {
                return (
                  <td key={index}>
                    {val !== "" ? val : new Array(10).join(" ")}
                  </td>
                );
              })}
              <td className="rowAlign">
                <Button className="table-button" onClick={onClickGenerate}>
                  Generate Reports
                </Button>
                <a>
                  <Button className="table-button" onClick={onClickDownload}>
                    Download
                  </Button>
                </a>
                <Button className="table-button" onClick={onClickDownload}>
                  Email
                </Button>
              </td>
            </tr>
          );
        })}
      </tbody>
    );
  };
  return (
    <TableContainer component={Paper}>
      <Table sx={{ minWidth: 700 }} aria-label="customized table">
        <TableHead>
          <TableRow>
            {columns.map((column, index) => {
              return (
                <StyledTableCell
                  key={index}
                  style={{ color: "black", fontWeight: "700" }}
                >
                  {column}
                </StyledTableCell>
              );
            })}
            <StyledTableCell
              align="center"
              style={{ color: "black", fontWeight: "700" }}
            >
              ACTIONS
            </StyledTableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {data.map((row, index) => (
            <StyledTableRow style={gunnarStyle} key={index}>
              <StyledTableCell style={gunnarStyle}>
                <input type="checkbox" />
              </StyledTableCell>
              <StyledTableCell style={gunnarStyle} component="th" scope="row">
                {row.sampleId}
              </StyledTableCell>

              <StyledTableCell style={gunnarStyle}>
                {row.barcodeName}
              </StyledTableCell>
              <StyledTableCell style={gunnarStyle}>
                {row.animalSpecies}
              </StyledTableCell>
              <StyledTableCell style={gunnarStyle}>{row.panel}</StyledTableCell>
              <StyledTableCell style={gunnarStyle}>
                {row.labRefId}
              </StyledTableCell>
              <StyledTableCell style={gunnarStyle}>
                {row.animalName}
              </StyledTableCell>
              <StyledTableCell style={gunnarStyle}>
                {row.refDate}
              </StyledTableCell>
              <StyledTableCell style={gunnarStyle}>
                {row.reportDate}
              </StyledTableCell>
              <StyledTableCell style={gunnarStyle}>
                {row.customerName}
              </StyledTableCell>
              <StyledTableCell style={gunnarStyle} align="center">
                <div className="table-button-wrapper">
                  <Button className="testbutton" 
                  //disabled={btnAvailable}
                  onClick={(e) => {
                    setButtonClickInfo({ "clicked": true, "index": index })
                    onClickGenerate(e, row.sampleId, row.referenceId)

                  }}>
                    Generate Reports
                  </Button>
                  <a
                  >
                    <Button className="testbutton" disabled={btnAvailable ? true : (buttonClickInfo['clicked'] === true && buttonClickInfo["index"] === index) ? false : true} onClick={(e) => onClickDownload()}>
                      Download
                    </Button>
                  </a>
                  <Button className="testbutton" onClick={onClickDownload}>
                    E-mail
                  </Button>
                </div>
              </StyledTableCell>
            </StyledTableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
    // <Table variant="light" size="sm" className="paddings">
    //     {makeHeader()}
    //     {makeBody()}
    // </Table>
  );
}

export default AttributesTable;
