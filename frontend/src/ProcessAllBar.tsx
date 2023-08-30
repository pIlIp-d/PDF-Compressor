import ProcessingSelect from "./file/ProcessingSelect.tsx";
import SettingsContainer from "./SettingsContainer.tsx";
import {Dispatch, SetStateAction, useRef, useState} from "react";
import {TabType} from "./App.tsx";
import "./processAllBar.css";


type ProcessAllBarProps = {
    fileIds: string[],
    currentAllFilesProcessor: string;
    setCurrentAllFilesProcessor: Dispatch<SetStateAction<string>>;
    currentTab: TabType;
    downloadAll: () => void;
    processAll: () => void;
    deleteAll: () => void;
    setAllFilesFormContent: Dispatch<SetStateAction<HTMLFormControlsCollection | null>>;
    allReadyForProcessorSelection: boolean;
    allFilesCanBeDownloaded: boolean;
    allFilesReadyForProcessing: boolean;
    currentlyProcessing: boolean;
    setInputFileTypes: (types: { [key: string]: string[] }) => void;
}

const ProcessAllBar = ({
                           fileIds,
                           currentAllFilesProcessor,
                           setCurrentAllFilesProcessor,
                           currentTab,
                           downloadAll,
                           processAll,
                           deleteAll,
                           setAllFilesFormContent,
                           allFilesReadyForProcessing,
                           allReadyForProcessorSelection,
                           allFilesCanBeDownloaded,
                           currentlyProcessing,
                           setInputFileTypes
                       }: ProcessAllBarProps) => {
    const allFilesFormRef = useRef<HTMLFormElement>(null);
    const [showAllFilesSettings, setShowAllFilesSettings] = useState(false);

    function toggleSettings() {
        setShowAllFilesSettings(old => !old);
    }

    return <>
        <div className={"border border-top-0 rounded-bottom p-3"}>
            <div className={"process-all-bar"}>
                <div className={"paceholder"}></div>
                <ProcessingSelect
                    currentTab={currentTab}
                    disabled={allReadyForProcessorSelection}
                    currentProcessor={currentAllFilesProcessor}
                    setInputFileTypes={setInputFileTypes}
                    fileIds={fileIds}
                    setProcessor={(processor) => {
                        if (processor == "null") setAllFilesFormContent(null);
                        setCurrentAllFilesProcessor(processor);
                    }}
                />

                <span
                    className={`m-auto bi bi-sliders ${currentTab != "Merge" ? "opacity-0" : (currentAllFilesProcessor == "null") ? "opacity-50" : ""}`}
                    onClick={(currentTab != "Merge" || currentAllFilesProcessor == "null") ? () => {
                    } : toggleSettings}>
            </span>
                {
                    allFilesCanBeDownloaded ?
                        <button
                            className={"btn btn-success"}
                            onClick={downloadAll}>
                            {currentTab != "Merge" ? "Download All" : "Download"}
                        </button> :
                        <button
                            className={"btn btn-secondary"}
                            disabled={!allFilesReadyForProcessing || currentlyProcessing}
                            onClick={processAll}>
                            {currentTab == "Merge" ? "Merge Files" : currentTab == "Compress" ? "Compress All" : "Convert All"}
                            {currentlyProcessing &&
                                <div className="spinner-border spinner-border-sm" role="status"
                                     style={{"animationDuration": "2s"}}>
                                    <span className="visually-hidden">...</span>
                                </div>
                            }
                        </button>
                }
                <div role={"button"} className={`m-auto ${fileIds.length === 0 && "pe-none"}`} onClick={deleteAll}>
                    <span className={` bi bi-x-lg ${fileIds.length === 0 && "opacity-50"}`}> All</span>
                </div>
            </div>
            {currentTab == "Merge" &&
                <SettingsContainer
                    showSettings={showAllFilesSettings} currentProcessor={currentAllFilesProcessor}
                    formRef={allFilesFormRef}
                    onChange={() => {
                        if (allFilesFormRef.current)
                            setAllFilesFormContent(allFilesFormRef.current.elements);
                    }}/>
            }
        </div>
    </>;
}

export default ProcessAllBar;