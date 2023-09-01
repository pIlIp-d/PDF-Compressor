import "./filerow/file.css"
import {useRef, useState} from "react";
import ProcessingSelect from "./filerow/ProcessingSelect.tsx";
import SettingsContainer from "./filerow/SettingsContainer.tsx";
import FileSizeText from "./filerow/FileSizeText.tsx";
import FileIcon from "./filerow/FileIcon.tsx";
import SettingsButton from "./filerow/SettingsButton.tsx";
import FileProcessingButton from "./filerow/FileProessingButton.tsx";
import ProgressBar from "./filerow/ProgressBar.tsx";
import DeleteButton from "./filerow/DeleteButton.tsx";
import {TabType} from "./utils/TabType.ts";

type FileProps = {
    id: string;
    progress: number;
    status: "uploading" | "failed" | "success";
    error: string;
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
                         error,
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
    }

    function toggleSettings() {
        setShowSettings(old => !old);
    }

    return <div className={"pt-2 px-2"}>
        <div className={`file-row h-100  m-3 align-items-center ${currentTab} ${processingState}`}>
            <FileIcon toolTipText={error}/>
            <span className={"fade-overflow fw-bold"}>{name}</span>
            <FileSizeText sizeBefore={sizeBefore} sizeAfter={sizeAfter}
                          showSizeAfter={currentTab == "Compress" && processingState == "processed"}/>
            {currentTab != "Merge" &&
                <>
                    {status == "failed" ?
                        <>
                            <div>{/*placeholder*/}</div>
                            <div>{/*placeholder*/}</div>
                            <div>{/*placeholder*/}</div>
                        </>
                        : <>
                            {processingState != "processed" &&
                                <>
                                    <ProcessingSelect
                                        disabled={status !== "success" || processingState !== "initial"}
                                        currentProcessor={currentProcessor}
                                        setProcessor={(processor) => {
                                            if (processor == "null")
                                                setFormContent(null);
                                            setCurrentProcessor(processor);
                                        }} fileIds={id} currentTab={currentTab}
                                        setInputFileTypes={setInputFileTypes}/>
                                    <SettingsButton
                                        disabled={status !== "success" || currentProcessor == "null" || processingState != "initial"}
                                        onClick={toggleSettings}/>
                                </>
                            }
                            <FileProcessingButton
                                isDownloadButton={processingState == "processed"}
                                isLoading={processingState == "processing"}
                                isDisabled={status !== "success" || currentProcessor == "null" || processingState == "processing"}
                                text={currentTab}
                                onClick={processingState == "initial" ? startProcessing : download}
                            />
                        </>
                    }
                </>
            }
            <DeleteButton onClick={onDelete} disabled={status == "uploading"}/>
        </div>
        {
            currentTab != "Merge" &&
            <SettingsContainer
                showSettings={showSettings} currentProcessor={currentProcessor} formRef={formRef}
                onChange={() => {
                    if (formRef.current)
                        setFormContent(formRef.current.elements);
                }}/>
        }
        <ProgressBar progress={progress} isGreen={status !== "failed"}/>
    </div>;
}

export default DroppedFile;