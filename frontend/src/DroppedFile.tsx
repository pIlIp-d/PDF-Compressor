import {humanReadableFileSize} from "./file/humanReadableFileSize.ts";
import "./file/file.css"
import {FormEvent, ReactNode, useEffect, useRef, useState} from "react";
import ProcessingSelect from "./file/ProcessingSelect.tsx";
import {Requester} from "./Requester.ts";
import CustomToolTip from "./CustomToolTip.tsx";
import {classNames} from "react-select/dist/declarations/src/utils";

type FileProps = {
    id: string;
    progress: number;
    status: "uploading" | "failed" | "success";
    name: string;
    size: number;
    onDelete: () => void;
}

interface FormField {
    name: string;
    label: string;
    type: string;
    required: boolean;
    help_text: string;
    choices: { value: string; display: string }[];
    /*possibly more, but these have custom html and therefore need to be specified*/
}

const DroppedFile = ({id, progress, status, name, size, onDelete}: FileProps) => {
    const [currentProcessor, setProcessor] = useState<string>("null");
    const [showSettings, setShowSettings] = useState(false);
    const [settingsHTML, setSettingsHTML] = useState<ReactNode>(null);
    const formRef = useRef<HTMLFormElement>(null);
    if (status === "failed") {
        progress = 100;
        setTimeout(onDelete, 2000);
    }

    function toggleSettings() {
        setShowSettings(old => !old);
    }

    type FormInput = {
        name: string;
        value: any;
    }
    function submitForm(items: HTMLFormControlsCollection) {
        const formData: {[key: string]: any} = {};
        for (let i = 0; i < items.length; i++) {
            const input = items[i];
            if (input instanceof HTMLElement) {
                if ("name" in input && "value" in input)
                    formData[input.name+""] = input.value;
            }
        }
        formData["processor"] = currentProcessor
        Requester("", {method: "POST", data: formData});
    }

    function getSettingsHTMLFromConfig(config: any) {
        console.log(config);
        if ("form_data" in config) {
            return <form ref={formRef} className={"border-top py-2"}>
                {config.form_data.fields.map((field: FormField, key: number) => <div key={key}>
                    <CustomToolTip enabled={true} tooltipText={field.help_text} children={<>
                        <label htmlFor={field.name}>{field.label}</label>
                        {field.type === 'select' ?
                            (<select name={field.name} required={field.required}>{field.choices.map((choice) => (
                                <option key={choice.value} value={choice.value}>{choice.display}</option>
                            ))}</select>) :
                            (<input {...field}/>)
                        }
                    </>
                    }/>
                </div>)}
            </form>;
        }
        return <></>;
    }

    HTMLFormControlsCollection

    useEffect(() => {
        const parts = currentProcessor.split('-');
        const mime_type = parts.pop(); // Remove and retrieve the last element
        const processor_name = parts.join('-'); // Join the remaining elements with '-'
        console.log(mime_type);
        console.log(processor_name);

        if (currentProcessor != "null")
            Requester("/get_settings_config_for_processor", {params: {plugin: processor_name, destination_file_type: mime_type}})
                .then((response) => {
                    //if ("config" in response.data)
                    setSettingsHTML(getSettingsHTMLFromConfig(response.data.config));
                });
    }, [currentProcessor]);
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
                <ProcessingSelect disabled={status !== "success"} currentProcessor={currentProcessor}
                                  setProcessor={setProcessor} fileId={id}/>
                <span className={`m-auto bi bi-sliders ${status !== "success" && "opacity-50"}`}
                      onClick={toggleSettings}></span>
                <button className={"btn btn-secondary"} onClick={() => {
                    if (formRef.current) submitForm(formRef.current.elements);
                }} disabled={status !== "success"}>Convert
                </button>
                <span
                    className={`m-auto bi bi-x-lg ${status !== "success" && "opacity-50"}`}
                    onClick={onDelete}
                ></span>
            </div>
            <div className={`px-3 w-100 ${showSettings || "d-none"}`}>
                {settingsHTML}
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