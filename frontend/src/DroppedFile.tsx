import {humanReadableFileSize} from "./file/humanReadableFileSize.ts";
import "./file/file.css"
import React, {useState} from "react";
import {Tooltip} from 'react-tooltip'
import ProcessingSelect from "./file/ProcessingSelect.tsx";

type FileProps = {
    id: string;
    progress: number;
    status: "uploading" | "failed" | "success";
    name: string;
    size: number;
    onDelete: () => void;
}


const DroppedFile = ({id, progress, status, name, size, onDelete}: FileProps) => {
    const [currentProcessor, setProcessor] = useState<string>("");

    if (status === "failed") {
        progress = 100;
        setTimeout(onDelete, 2000);
    }

    return (
        <div className={"pt-2 px-2"}>
            <div className={"file-row h-100  m-3 align-items-center"}>
                <div id={"file-icon"}>
                    <Tooltip id="my-tooltip"/>
                    <a data-tooltip-id="my-tooltip" data-tooltip-content="Potential Error">
                        <span className={"bi bi-file-earmark-text"}/>
                    </a>
                </div>
                <span className={"fade-overflow fw-bold"}>{name}</span>
                <span className={`fw-lighter fs-7 text-end mx-2`}>{humanReadableFileSize(size)}</span>
                <ProcessingSelect disabled={status !== "success"} currentProcessor={currentProcessor} setProcessor={setProcessor} fileId={id}/>
                <span className={`m-auto bi bi-sliders ${status !== "success" && "opacity-50"}`}></span>
                <button className={"btn btn-secondary"} disabled={status !== "success"}>Convert</button>
                <span
                    className={`m-auto bi bi-x-lg ${status !== "success" && "opacity-50"}`}
                    onClick={onDelete}
                ></span>
            </div>
            <div className="progress" style={{height: "2px"}}>
                <div className={`progress-bar ${status === "failed" ? "bg-danger" : "bg-success"}`}
                     role="progressbar" aria-valuenow={progress}
                     aria-valuemin="0"
                     aria-valuemax="100" style={{width: progress + "%"}}></div>
            </div>
        </div>
    );
}

export default DroppedFile;