import {humanReadableFileSize} from "./file/humanReadableFileSize.ts";
import "./file/file.css"
import {useEffect, useRef, useState} from "react";
import ProcessingSelect from "./file/ProcessingSelect.tsx";
import CustomToolTip from "./CustomToolTip.tsx";
import {TabType} from "./App.tsx";
import SettingsContainer from "./SettingsContainer.tsx";

type FileProps = {
    id: string;
    progress: number;
    status: "uploading" | "failed" | "success";
    name: string;
    sizeBefore: number;
    sizeAfter: number;
    onDelete: () => void;
    currentTab: TabType;
    download: () => void;
    processingState: "initial" | "processing" | "processed"
    setFormContent: (val: HTMLFormControlsCollection | null) => void;
    startProcessing: () => void;
    currentProcessor: string
    setCurrentProcessor: (processor: string) => void;
    setInputFileTypes: (types: { [key: string]: string[] }) => void;
}

const DroppedFile = ({
                         id,
                         progress,
                         status,
                         name,
                         sizeBefore,
                         sizeAfter,
                         onDelete,
                         currentTab,
                         download,
                         processingState,
                         setFormContent,
                         startProcessing,
                         currentProcessor,
                         setCurrentProcessor,
                         setInputFileTypes
                     }: FileProps) => {
    const [showSettings, setShowSettings] = useState(false);
    const formRef = useRef<HTMLFormElement>(null);

    if (status === "failed") {
        progress = 100;
        setTimeout(onDelete, 2000);
    }

    function toggleSettings() {
        setShowSettings(old => !old);
    }

    useEffect(() => {
        console.log(currentProcessor);
    }, [currentProcessor]);

    return (
        <div className={"pt-2 px-2"}>
            <div className={`file-row h-100  m-3 align-items-center ${currentTab} ${processingState}`}>
                <div id={"file-icon"}>
                    <CustomToolTip enabled={status === "failed"} tooltipText={"Potential Error"} children={
                        <span className={"bi bi-file-earmark-text"}/>
                    }/>
                </div>
                <span className={"fade-overflow fw-bold"}>{name}</span>
                <span className={`fw-lighter fs-7 text-end mx-2`}>
                    {humanReadableFileSize(sizeBefore)}
                    {
                        currentTab == "Compress" && processingState == "processed" && <>
                            <i className="bi bi-arrow-right-short"></i>
                            <span className={"text-success"}>{humanReadableFileSize(sizeAfter)}</span>
                        </>
                    }
                </span>
                {processingState != "processed" && currentTab != "Merge" && <>
                    <ProcessingSelect disabled={status !== "success" || processingState !== "initial"}
                                      currentProcessor={currentProcessor}
                                      setProcessor={(processor) => {
                                          if (processor == "null")
                                              setFormContent(null);
                                          setCurrentProcessor(processor);
                                      }} fileIds={id} currentTab={currentTab} setInputFileTypes={setInputFileTypes}/>
                    <span
                        className={`m-auto bi bi-sliders ${(status !== "success" || currentProcessor == "null" || processingState != "initial") && "opacity-50"}`}
                        onClick={(status !== "success" || currentProcessor == "null" || processingState != "initial") ? () => {
                        } : toggleSettings}>

                        </span>
                </>
                }
                {currentTab != "Merge" && <>
                    {processingState == "initial" &&
                        <button className={"btn btn-secondary"} onClick={startProcessing}
                                disabled={status !== "success" || currentProcessor == "null"}>
                            {currentTab == "Convert" ? "Convert" :
                                currentTab == "Compress" ? "Compress" : ""
                            }
                        </button>
                    }
                    {processingState == "processing" &&
                        <button className={"btn btn-secondary"} disabled={true}>Loading
                            <div className="spinner-border spinner-border-sm" role="status"
                                 style={{"animationDuration": "2s"}}>
                                <span className="visually-hidden">...</span>
                            </div>
                        </button>
                    }
                    {processingState == "processed" &&
                        <button className={"btn btn-success"} onClick={() => download()}>
                            Download
                        </button>
                    }
                </>
                }
                <span role={"button"}
                    className={`m-auto bi bi-x-lg ${status !== "success" && "pe-none opacity-50"}`}
                    onClick={onDelete}
                ></span>
            </div>
            <SettingsContainer
                showSettings={showSettings} currentProcessor={currentProcessor} formRef={formRef}
                onChange={() => {
                    if (formRef.current)
                        setFormContent(formRef.current.elements);
                }}/>
            <div className="progress" style={{height: "2px"}}>
                <div className={`progress-bar ${status === "failed" ? "bg-danger" : "bg-success"}`}
                     role="progressbar" aria-valuenow={progress}
                     aria-valuemin="0"
                     aria-valuemax="100" style={{width: progress + "%"}}></div>
            </div>
        </div>
    )
        ;
}

export default DroppedFile;