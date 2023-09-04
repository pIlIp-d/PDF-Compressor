import ProcessingSelect from "./filerow/ProcessingSelect.tsx";
import SettingsContainer from "./filerow/SettingsContainer.tsx";
import {Dispatch, SetStateAction, useRef, useState} from "react";
import "./processAllBar.css";
import FileUploader from "./FileUploader.tsx";
import {TabType} from "./utils/TabType.ts";
import {FileType} from "./utils/FileType.ts";
import SettingsButton from "./filerow/SettingsButton.tsx";
import DeleteButton from "./filerow/DeleteButton.tsx";
import FileProcessingButton from "./filerow/FileProessingButton.tsx";


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
    //setInputFileTypes: (types: { [key: string]: string[] }) => void;
    updateFile: (id: string, newProps: Partial<FileType>) => void;
    addFile: (file: FileType) => void;
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
                           updateFile,
                           addFile
                       }: ProcessAllBarProps) => {
    const allFilesFormRef = useRef<HTMLFormElement>(null);
    const [showAllFilesSettings, setShowAllFilesSettings] = useState(false);
    const [inputFileTypes, setInputFileTypes] = useState<{ [key: string]: string[] }>({});

    function toggleSettings() {
        setShowAllFilesSettings(old => !old);
    }

    return <>
        <div className={"border border-top-0 rounded-bottom p-3 bg-white"}>
            <div className={"process-all-bar"}>
                <FileUploader updateFile={updateFile} addFile={addFile} currentProcessor={currentAllFilesProcessor}
                              inputFileTypes={inputFileTypes}/>
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
                {currentTab == "Merge" ?
                    <SettingsButton disabled={currentAllFilesProcessor == "null"} onClick={toggleSettings}/>
                    :
                    <div>{/*placeholder*/}</div>
                }
                <FileProcessingButton
                    isDownloadButton={allFilesCanBeDownloaded}
                    isLoading={currentlyProcessing}
                    isDisabled={!allFilesCanBeDownloaded && !allFilesReadyForProcessing || currentlyProcessing}
                    text={currentTab}
                    onClick={allFilesCanBeDownloaded ? downloadAll : processAll}
                    additionalText={" All"}
                />
                <DeleteButton onClick={deleteAll} disabled={fileIds.length === 0} additionalText={" All"}/>
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