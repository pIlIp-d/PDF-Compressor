import {humanReadableFileSize} from "./file/humanReadableFileSize.ts";
import "./file/file.css"
import { useEffect, useRef, useState} from "react";
import ProcessingSelect from "./file/ProcessingSelect.tsx";
import {Requester} from "./Requester.ts";
import CustomToolTip from "./CustomToolTip.tsx";
import {TabType} from "./App.tsx";
import {BACKEND_HOST} from "./config.ts";
import SettingsContainer from "./SettingsContainer.tsx";
import axios from "axios";

type FileProps = {
    id: string;
    progress: number;
    status: "uploading" | "failed" | "success";
    name: string;
    size: number;
    onDelete: () => void;
    currentTab: TabType;
}


const DroppedFile = ({id, progress, status, name, size, onDelete, currentTab}: FileProps) => {
    const [currentProcessor, setProcessor] = useState<string>("null");
    const [showSettings, setShowSettings] = useState(false);
    const formRef = useRef<HTMLFormElement>(null);
    const [processingState, setProcessingState] = useState<"initial" | "processing" | "processed">("initial");
    const [requestId, setRequestId] = useState<null | number>(null);
    const pollingTimer = useRef<number>();
    const [downloadPath, setDownloadPath] = useState("");

    if (status === "failed") {
        progress = 100;
        setTimeout(onDelete, 2000);
    }

    function toggleSettings() {
        setShowSettings(old => !old);
    }

    function submitForm(items: HTMLFormControlsCollection) {
        const formData = new FormData();
        for (let i = 0; i < items.length; i++) {
            const input = items[i];
            if (input instanceof HTMLElement) {
                if ("name" in input && "value" in input)
                    formData.append(input.name + "", input.value + "");
            }
        }
        formData.append("processor", currentProcessor);

        // @ts-ignore
        formData.append("files[]", [id]);
        Requester("/process_files/", {
            method: "POST",
            data: formData,
            headers: {"Content-Type": "application/json"}
        }).then((response) => {
            if (response.status == 200) {
                setProcessingState("processing");
                if ("processing_request_id" in response.data)
                    setRequestId(response.data.processing_request_id);
            }
        });
    }

    function pollProcessedFiles() {
        Requester("/get_all_files_of_request", {params: {request_id: requestId}}).then((response) => {
            if ("request_finished" in response.data && response.data.request_finished) {
                setProcessingState("processed");
            }
            if ("files" in response.data) {
                const processedFiles = response.data.files.filter((f: {
                    file_origin: string
                }) => f.file_origin == "processed")
                if (processedFiles.length > 0)
                    setDownloadPath(BACKEND_HOST + "/" + processedFiles[0].filename_path);
                // TODO error handling
                // TODO show processedFiles and make them downloadable
            }
        })
    }

    useEffect(() => {
        const POLLING_TICK = 1000;
        if (processingState == "processing") {
            pollingTimer.current = setInterval(pollProcessedFiles, POLLING_TICK);
            return () => clearInterval(pollingTimer.current);
        } else if (processingState == "processed")
            if (pollingTimer.current) {
                clearInterval(pollingTimer.current);
            }
    }, [processingState]);



    return (
        <div className={"pt-2 px-2"}>
            <div className={"file-row h-100  m-3 align-items-center"}>
                <div id={"file-icon"}>
                    <CustomToolTip enabled={status === "failed"} tooltipText={"Potential Error"} children={
                        <span className={"bi bi-file-earmark-text"}/>
                    }/>
                </div>
                <span className={"fade-overflow fw-bold"}>{name}</span>
                <span className={`fw-lighter fs-7 text-end mx-2`}>{humanReadableFileSize(size)}</span>
                <ProcessingSelect disabled={status !== "success" || processingState != "initial"}
                                  currentProcessor={currentProcessor}
                                  setProcessor={setProcessor} fileId={id} currentTab={currentTab}/>
                <span
                    className={`m-auto bi bi-sliders ${(status !== "success" || currentProcessor == "null") && "opacity-50"}`}
                    onClick={(status !== "success" || currentProcessor == "null")?()=>{} :toggleSettings}></span>
                {processingState == "initial" &&
                    < button className={"btn btn-secondary"} onClick={() => {
                        if (formRef.current) submitForm(formRef.current.elements);
                    }} disabled={status !== "success" || currentProcessor == "null"}>Convert
                    </button>
                }
                {processingState == "processing" &&
                    < button className={"btn btn-secondary"} disabled={true}>Loading
                        <div className="spinner-border spinner-border-sm" role="status"
                             style={{"animationDuration": "2s"}}>
                            <span className="visually-hidden">...</span>
                        </div>
                    </button>
                }
                {processingState == "processed" &&
                    <button className={"btn btn-success"} onClick={()=>download(downloadPath)}>
                            Download
                        <a href={downloadPath} download target={"_blank"} style={{"color": "inherit", "textDecoration": "inherit"}}>
                        </a>
                    </button>
                }
                <span
                    className={`m-auto bi bi-x-lg ${status !== "success" && "opacity-50"}`}
                    onClick={onDelete}
                ></span>
            </div>
            <SettingsContainer showSettings={showSettings} currentProcessor={currentProcessor} formRef={formRef}/>
            <div className="progress" style={{height: "2px"}}>
                <div className={`progress-bar ${status === "failed" ? "bg-danger" : "bg-success"}`}
                     role="progressbar" aria-valuenow={progress}
                     aria-valuemin="0"
                     aria-valuemax="100" style={{width: progress + "%"}}></div>
            </div>
        </div>
    );
}

 function download(fileUrl: string){
          axios({
              url: fileUrl,
              method:'GET',
              responseType: 'blob'
      })
      .then((response) => {
             const url = window.URL
             .createObjectURL(new Blob([response.data]));
                    const link = document.createElement('a');
                    link.href = url;
                    link.setAttribute('download', fileUrl.split("/").pop() as string);
                    document.body.appendChild(link);
                    link.click();
      })
      }

export default DroppedFile;