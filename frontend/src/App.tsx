import React, {useEffect, useRef, useState} from 'react';
import './custom-dropzone.css'
import FileUploader from "./FileUploader.tsx";
import {FileType} from "./FileType.ts";
import DroppedFile from "./DroppedFile.tsx";
import {useLocation} from 'react-router-dom';
import axios, {AxiosResponse} from "axios";
import {Requester} from "./Requester.ts";
import {BACKEND_HOST} from "./config.ts";
import ProcessAllBar from "./ProcessAllBar.tsx";
import TabBar from "./TabBar.tsx";


export type TabType = "Convert" | "Compress" | "Merge";

type ProcessingStateType = "initial" | "processing" | "processed";

type FileDataType = {
    file: FileType;
    downloadPath: string;
    processingState: ProcessingStateType;
    currentProcessor: string;
    formContent: HTMLFormControlsCollection | null;
    inputFileTypes: { [key: string]: string[] };
    requestId: null | number
    sizeAfter: number;
};
const POLLING_TICK = 1000;

const App = () => {
    //const [files, setFiles] = useState<FileType[]>([]);
    const location = useLocation()

    const [currentTab, setCurrentTab] = useState<TabType>("Convert");
    const [filesData, setFileData] = useState<FileDataType[]>([]);
    const [fileIds, setFileIds] = useState<string[]>([]);

    const [currentAllFilesProcessor, setCurrentAllFilesProcessor] = useState<string>("null");
    const [allFilesFormContent, setAllFilesFormContent] = useState<HTMLFormControlsCollection | null>(null);
    const [inputFileTypes, setInputFileTypes] = useState<{ [key: string]: string[] }>({});
    const pollingTimer = useRef<number>();
    const [requestIdForAll, setRequestIdForAll] = useState<null | number>(null);
    const [processingStateForMerge, setProcessingStateForMerge] = useState<ProcessingStateType>("initial");
    const [downloadAllPath, setDownloadAllPath] = useState("");

    function updateFileData(key: number, values: Partial<FileDataType>) {

        setFileData(prev => {
            const newState = [...prev];
            newState[key] = {...newState[key], ...values};
            return newState;
        });
    }

    function addFile(file: FileType) {
        setDownloadAllPath("");
        setProcessingStateForMerge("initial");
        setRequestIdForAll(null);

        setFileData((prev) => {
            const newState = [...prev];
            newState.push({
                file: file,
                downloadPath: "",
                processingState: "initial",
                formContent: null,
                currentProcessor: currentAllFilesProcessor,
                inputFileTypes: {},
                requestId: null,
                sizeAfter: 0
            });
            setFileIds(newState.map(f => "" + f.file.id));
            return newState;
        })
    }

    function updateFile(id: string, newProps: Partial<FileType>) {
        setFileData(prevFileData => {
            const newfilesData = prevFileData.map(fileData => {
                if (fileData.file.id === id) {
                    return {...fileData, file: {...fileData.file, ...newProps}};
                } else return fileData;
            });
            setFileIds(newfilesData.map(f => "" + f.file.id));
            return newfilesData;
        });
    }

    async function removeFile(id: string) {
        setFileData(oldFileData => {
            const files = oldFileData.filter(f => f.file.id != id)
            setFileIds(files.map(f => "" + f.file.id));
            if (files.length == 0)
                setCurrentAllFilesProcessor("null");
            return files;
        });
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


    function submitSingleFile(key: number) {
        submitForm(
            filesData[key].currentProcessor,
            [filesData[key].file.id],
            filesData[key].formContent,
            (response) => {
                updateFileData(key, {processingState: "processing"});
                if ("processing_request_id" in response.data)
                    updateFileData(key, {requestId: response.data.processing_request_id});
            }
        );
    }

    function downloadAll() {
        if (currentTab == "Merge") {
            download(downloadAllPath);
        } else {
            filesData.forEach((file) => {
                if (file.downloadPath != "") {
                    download(file.downloadPath);
                }
            })
        }
    }

    function deleteAll() {
        filesData.forEach(async (fileData) => await removeFile(fileData.file.id));
    }
    function processAll() {
        if (currentTab == "Merge") {
            const fileIds = filesData.map(f => "" + f.file.id);
            console.log(fileIds);
            submitForm(
                currentAllFilesProcessor,
                fileIds,
                allFilesFormContent,
                (response) => {
                    setProcessingStateForMerge("processing");
                    if ("processing_request_id" in response.data)
                        setRequestIdForAll(response.data.processing_request_id);
                });
        } else {
            filesData.map((_, key) => key).filter(key => filesData[key].processingState === "initial").forEach(key => {
                console.log(key, filesData[key])
                submitSingleFile(key);
            });
        }
    }

    function submitForm(currentProcessor: string, fileIds: string[], items: HTMLFormControlsCollection | null, responseHandler: (response: AxiosResponse) => void) {
        if (items) {
            const formData = new FormData();
            for (let i = 0; i < items.length; i++) {
                const input = items[i];
                if (input instanceof HTMLElement) {
                    if ("name" in input && "value" in input)
                        formData.append(input.name + "", input.value + "");
                    if (currentTab == "Merge")
                        formData.append("merge_files", "true");
                }
            }
            formData.append("processor", currentProcessor);
            formData.append("files", JSON.stringify(fileIds));

            Requester("/process_files/", {
                method: "POST",
                data: formData,
                headers: {"Content-Type": "application/json"}
            }).then((response) => {
                if (response.status == 200) {
                    responseHandler(response);
                }
            });
        }
    }

    function pollProcessedFiles() {
        if (currentTab != "Merge") {
            filesData.forEach((file, key) => {
                if (file.processingState == "processing") {
                    Requester("/get_all_files_of_request", {params: {request_id: file.requestId}}).then((response) => {
                        if ("request_finished" in response.data && response.data.request_finished) {
                            updateFileData(key, {processingState: "processed"});
                        }
                        if ("files" in response.data) {
                            const processedFiles: {
                                filename_path: string,
                                size: number
                            }[] = response.data.files.filter((f: {
                                file_origin: string
                            }) => f.file_origin == "processed")
                            if (processedFiles.length > 0) {
                                updateFileData(key, {downloadPath: BACKEND_HOST + "/" + processedFiles[0].filename_path});
                                updateFileData(key, {sizeAfter: processedFiles[0].size});

                            }
                            // TODO error handling
                            // TODO show processedFiles and make them downloadable
                        }
                    })

                }
            });
        } else {
            if (processingStateForMerge == "processing") {
                Requester("/get_all_files_of_request", {params: {request_id: requestIdForAll}}).then((response) => {
                    if ("request_finished" in response.data && response.data.request_finished) {
                        setProcessingStateForMerge("processed");
                    }
                    if ("files" in response.data) {
                        const processedFiles: {
                            filename_path: string
                        }[] = response.data.files.filter((f: {
                            file_origin: string
                        }) => f.file_origin == "processed")
                        if (processedFiles.length > 0)
                            setDownloadAllPath(BACKEND_HOST + "/" + processedFiles[0].filename_path);
                        // TODO error handling
                        // TODO show processedFiles and make them downloadable
                    }
                })

            }

        }
    }

    useEffect(() => {
        filesData.forEach((_, key) => {
            updateFileData(key, {currentProcessor: currentAllFilesProcessor});
        })
    }, [currentAllFilesProcessor]);

    useEffect(() => {
        // if any file is currently processing
        if (filesData.reduce((prev: boolean, current: FileDataType) => prev || current.processingState == "processing", false) || processingStateForMerge == "processing") {
            pollingTimer.current = setInterval(pollProcessedFiles, POLLING_TICK);
            return () => clearInterval(pollingTimer.current);
        } else if (pollingTimer.current) {
            console.log("not processing");
            clearInterval(pollingTimer.current);
        }
    }, [filesData, processingStateForMerge]);// TODO split up filesData hook

    return (
        <div className={"container-lg mt-3"}>
            <h1>DragonFile</h1>
            <br/>
            <TabBar currentTab={currentTab}/>
            <div className={"border border-top-0"}>
                {filesData.map((fileData, key) => {
                        return <DroppedFile
                            key={key}
                            id={fileData.file.id}
                            progress={fileData.file.progress}
                            status={fileData.file.status}
                            name={fileData.file.name}
                            sizeBefore={fileData.file.size}
                            sizeAfter={fileData.sizeAfter}
                            onDelete={async () => await removeFile(fileData.file.id)}
                            currentTab={currentTab}
                            setFormContent={(val: HTMLFormControlsCollection | null) => updateFileData(key, {formContent: val})}
                            startProcessing={() => submitSingleFile(key)}
                            setCurrentProcessor={(processor: string) => updateFileData(key, {currentProcessor: processor})}
                            currentProcessor={fileData.currentProcessor}
                            processingState={fileData.processingState}
                            download={() => download(fileData.downloadPath)}
                            setInputFileTypes={(types) => updateFileData(key, {inputFileTypes: types})}
                        />
                    }
                )}
                <div className={"w-100 py-2"}>
                    <FileUploader updateFile={updateFile} addFile={addFile}
                                  currentProcessor={currentAllFilesProcessor}
                                  inputFileTypes={inputFileTypes}></FileUploader>
                </div>
            </div>
            <ProcessAllBar
                fileIds={fileIds}
                currentAllFilesProcessor={currentAllFilesProcessor}
                setCurrentAllFilesProcessor={setCurrentAllFilesProcessor}
                setAllFilesFormContent={setAllFilesFormContent}
                currentTab={currentTab}
                downloadAll={downloadAll}
                processAll={processAll}
                deleteAll={deleteAll}
                allReadyForProcessorSelection={filesData.some(f => f.file.status !== "success") || filesData.some(f => f.processingState != "initial")}
                allFilesCanBeDownloaded={filesData.length > 0 && (!filesData.some(f => f.processingState != "processed") || processingStateForMerge == "processed")}
                allFilesReadyForProcessing={filesData.filter(f => f.processingState == "initial").length > 0 && !filesData.filter(f => f.processingState == "initial").some(f => f.currentProcessor == "null")}
                currentlyProcessing={filesData.some(f => f.processingState == "processing") || processingStateForMerge == "processing"}
                setInputFileTypes={setInputFileTypes}
            />

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