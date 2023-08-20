import { useEffect, useRef, useState} from 'react';
import './custom-dropzone.css'
import FileUploader from "./FileUploader.tsx";
import {FileType} from "./FileType.ts";
import DroppedFile from "./DroppedFile.tsx";
import {useLocation} from 'react-router-dom';
import axios from "axios";
import {Requester} from "./Requester.ts";
import {BACKEND_HOST} from "./config.ts";


export type TabType = "Convert" | "Compress" | "Merge";

type FileDataType = {
    file: FileType;
    downloadPath: string;
    processingState: "initial" | "processing" | "processed";
    currentProcessor: string;
    formContent: HTMLFormControlsCollection | null;
};
const POLLING_TICK = 1000;

const App = () => {
    //const [files, setFiles] = useState<FileType[]>([]);
    const location = useLocation()

    const [currentTab, setCurrentTab] = useState<TabType>("Convert");
    const [filesData, setFileData] = useState<FileDataType[]>([]);

    function updateFileData(key: number, values: Partial<FileDataType>) {

        setFileData(prev => {
            const newState = [...prev];
            newState[key] = {...newState[key], ...values};
            return newState;
        });
    }

    function addFile(file: FileType) {
        setFileData((prev) => {
            const newState = [...prev];
            newState.push({file: file, downloadPath: "", processingState: "initial", formContent: null, currentProcessor: "null"});
            return newState;
        })
    }

    function updateFile(id: string, newProps: Partial<FileType>) {
        setFileData(prevFileData => {
            return prevFileData.map(fileData => {
                if (fileData.file.id === id) {
                    return {...fileData, file: {...fileData.file, ...newProps}};
                } else return fileData;
            });
        });
    }

    async function removeFile(id: string) {
        setFileData(oldFileData => oldFileData.filter(f => f.file.id != id));
        const response = await Requester(`/file/${id}/`, {
            method: "DELETE",
            params: {file_origin: "uploaded"}
        });
        if (response.status != 200) {
            console.log("Couldn't remove file from server."); // TODO incorporate error message into GUI
        }
    }

    useEffect(() => {
        Requester("/get_csrf/").then((response) => {
            if ("csrfToken" in response.data) {
                // setting csrftoken header for all following requests
                axios.defaults.headers.common['X-CSRFTOKEN'] = response.data.csrfToken;
            }
        });
    }, []);

    useEffect(() => {
        const tab = location.hash.substring(1);
        switch (tab) {
            case "Convert":
            case "Compress":
            case "Merge":
                setCurrentTab(tab);
                break;
            default:
                setCurrentTab("Convert");
        }
        console.log(tab);
    }, [location]);

    function processAll() {
        if (currentTab == "Merge") {
            // TODO
        } else {
            filesData.forEach((val, key)=>{
                submitForm(key, val.formContent);
            })
        }
    }

    function downloadAll() {
        filesData.forEach((file)=>{
            if (file.downloadPath != ""){
                download(file.downloadPath);
            }
        })
    }

    function submitForm(key: number, items: HTMLFormControlsCollection | null) {
        if (items) {
            const formData = new FormData();
            for (let i = 0; i < items.length; i++) {
                const input = items[i];
                if (input instanceof HTMLElement) {
                    if ("name" in input && "value" in input)
                        formData.append(input.name + "", input.value + "");
                }
            }
            formData.append("processor", filesData[key].currentProcessor);
            // @ts-ignore
            formData.append("files[]", [filesData[key].file.id]);

            Requester("/process_files/", {
                method: "POST",
                data: formData,
                headers: {"Content-Type": "application/json"}
            }).then((response) => {
                if (response.status == 200) {
                    updateFileData(key, {processingState: "processing"});
                    if ("processing_request_id" in response.data)
                        setRequestId(response.data.processing_request_id);
                }
            });
        }
    }

    const pollingTimer = useRef<number>();
    const [requestId, setRequestId] = useState<null | number>(null);

    function pollProcessedFiles() {
        filesData.forEach((file, key) => {
            if (file.processingState == "processing") {
                Requester("/get_all_files_of_request", {params: {request_id: requestId}}).then((response) => {
                    if ("request_finished" in response.data && response.data.request_finished) {
                        updateFileData(key, {processingState: "processed"});
                    }
                    if ("files" in response.data) {
                        const processedFiles: {
                            filename_path: string
                        }[] = response.data.files.filter((f: {
                            file_origin: string
                        }) => f.file_origin == "processed")
                        if (processedFiles.length > 0)
                            updateFileData(key, {downloadPath: BACKEND_HOST + "/" + processedFiles[0].filename_path});

                        // TODO error handling
                        // TODO show processedFiles and make them downloadable
                    }
                })

            }
        });
    }

    useEffect(() => {
        // if any file is currently processing
        if (filesData.reduce((prev: boolean, current: FileDataType) => prev || current.processingState == "processing", false)) {
            pollingTimer.current = setInterval(pollProcessedFiles, POLLING_TICK);
            return () => clearInterval(pollingTimer.current);
        } else if (pollingTimer.current) {
            console.log("not processing");
            clearInterval(pollingTimer.current);
        }
    }, [filesData]);// TODO split up filesData hook

    return (
        <div className={"container-lg mt-3"}>
            <h1>DragonFile</h1>
            <br/>
            <ul className="nav nav-tabs">
                <li className="nav-item">
                    <a className={`text-dark nav-link ${currentTab === "Convert" && "active fw-bold"}`}
                       href="#Convert">Convert</a>
                </li>
                <li className="nav-item">
                    <a className={`text-dark nav-link ${currentTab === "Compress" && "active fw-bold"}`}
                       href="#Compress">Compress</a>
                </li>
                <li className="nav-item">
                    <a className={`text-dark nav-link ${currentTab === "Merge" && "active fw-bold"}`}
                       href="#Merge">Merge</a>
                </li>
            </ul>

            <div className={"border border-top-0"}>
                {filesData.map((fileData, key) => {
                    console.log("RERENDERED")
                        return <DroppedFile
                            key={key}
                            id={fileData.file.id}
                            progress={fileData.file.progress}
                            status={fileData.file.status}
                            name={fileData.file.name}
                            size={fileData.file.size}
                            onDelete={async () => await removeFile(fileData.file.id)}
                            currentTab={currentTab}
                            setDownloadPath={(path: string) => updateFileData(key, {downloadPath: path})}
                            setFormContent={(val: HTMLFormControlsCollection | null) => updateFileData(key, {formContent: val})}
                            startProcessing={() => submitForm(key, fileData.formContent)}
                            setCurrentProcessor={(processor: string) => updateFileData(key, {currentProcessor: processor})}
                            currentProcessor={fileData.currentProcessor}
                            processingState={fileData.processingState}
                            download={()=>download(fileData.downloadPath)}
                        />
                    }
                )}
                <div className={"w-100 py-2"}>
                    <FileUploader updateFile={updateFile} addFile={addFile}></FileUploader>
                </div>
            </div>
            <div className={"border border-top-0 rounded-bottom p-3"}>
                {filesData.length == 0  || filesData.some(f=>f.processingState != "processed") ?
                    <button
                        className={"btn btn-secondary"}
                        disabled={filesData.length == 0 || filesData.some(f=>f.currentProcessor == "null")}
                        onClick={processAll}>
                        Convert All
                    </button> :
                    <button
                        className={"btn btn-success"}
                        disabled={filesData.some((f)=>f.processingState != "processed")}
                        onClick={downloadAll}>
                        Download All
                    </button>
                }
            </div>
        </div>
    );
};


function download(fileUrl: string) {
    axios({
        url: fileUrl,
        method: 'GET',
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

export default App;