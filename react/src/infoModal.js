import React from 'react';
import { Modal, Button } from 'react-bootstrap';
import './App.css'

export const InfoModal = ({
    rowInfo={},
    show=false,
    onClickClose = () => {},
    onClickGenerate = () => {},
    onClickDownload = () => {},
    onClickEmail = () => {}
 }) => {
    return (
    <Modal show={show} onHide={onClickClose} size="lg" centered>
        <Modal.Header closeButton>
            <Modal.Title>ID: {rowInfo !== {} ? rowInfo['Column1']: ''}</Modal.Title>
        </Modal.Header>
        <Modal.Body>
            {Object.keys(rowInfo).map(key => {
                return key !== 'Column1' && (
                    <div key={key} className="modal-cell-alignment">
                        <div className="wrapper">
                            <b>{key}</b>: {rowInfo[key] || "NA"}
                        </div>
                        <Button>
                            Edit
                        </Button>
                    </div>
                )
            })}
        </Modal.Body>
        <Modal.Footer>
            <Button variant="primary" onClick={onClickGenerate}>
                Generate
            </Button>
            <Button variant="primary" onClick={onClickDownload}>
                Download
            </Button>
            <Button variant="primary" onClick={onClickEmail}>
                Email
            </Button>
        </Modal.Footer>
    </Modal>
    )
}