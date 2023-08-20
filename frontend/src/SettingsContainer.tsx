import {RefObject, useCallback, useEffect, useState} from "react";
import {Requester} from "./Requester.ts";
import CustomToolTip from "./CustomToolTip.tsx";

type SettingsContainerProps = {
    showSettings: boolean;
    currentProcessor: string;
    formRef: RefObject<HTMLFormElement>;
    onChange: () => void;
}


interface FormField {
    name: string;
    label: string;
    type: string;
    required: boolean;
    help_text: string;
    choices: { value: string; display: string }[];
    value: string;
    disabled: boolean;
    /*possibly more, but these have custom html and therefore need to be specified*/
}

type HierarchyType = {
    [key: string]: {
        type: "bool" | "choice",
        children: string[],
        "hide_state"?: string,
        "values_for_deactivation"?: string[]
    }
};

const SettingsContainer = ({showSettings, currentProcessor, formRef, onChange}: SettingsContainerProps) => {

    const [formFields, setFormFields] = useState<{ [key: string]: FormField }>({});
    const [hierarchy, setHierarchy] = useState<HierarchyType>({});
    // const [formValues, setFormValues] = useState<{ [key: string]: string }>({});

    const [, updateState] = useState<{}>();
    const forceUpdate = useCallback(() => updateState({}), []);


    function getSettingsHTMLFromConfig(config: any) {
        setHierarchy(config.hierarchy);
        if ("form_data" in config && "fields" in config.form_data) {
            config.form_data.fields.map((val: FormField) => {
                console.log("What the fuck");
                setFormFields((prev) => {
                    val.disabled = false;
                    return {...prev, [val.name]: val}
                })
            });
        }
    }

    useEffect(() => {
        const parts = currentProcessor.split('-');
        const mime_type = parts.pop(); // Remove and retrieve the last element
        const processor_name = parts.join('-'); // Join the remaining elements with '-'

        if (currentProcessor != "null")
            Requester("/get_settings_config_for_processor", {
                params: {
                    plugin: processor_name,
                    destination_file_type: mime_type
                }
            })
                .then((response) => {
                    //if ("config" in response.data)
                    getSettingsHTMLFromConfig(response.data.config);
                });
        onChange();
    }, [currentProcessor]);

    function onUpdate(fieldName: string, value: string) {
        // store the new value
        setFormFields((prev) => {
            const newState = {...prev};
            newState[fieldName].value = value;
            return newState;
        })
        // update disabled states with the hierarchy

        const disabledStates: { [key: string]: boolean } = {}
        Object.keys(hierarchy).map((hierarchyKey) => {
            hierarchy[hierarchyKey].children.forEach((child: string) => {
                if (!(child in disabledStates))
                    disabledStates[child] = false;
                switch (hierarchy[hierarchyKey]["type"]) {
                    case "bool":
                        disabledStates[child] ||= formFields[hierarchyKey].value + "" == hierarchy[hierarchyKey]["hide_state"].toLowerCase();
                        break;
                    case "choice":
                        disabledStates[child] ||= hierarchy[hierarchyKey]["values_for_deactivation"].includes(formFields[hierarchyKey].value);
                        break;
                }
            })
        });
        Object.keys(disabledStates).map((child: string) => {
            setFormFields((prev) => {
                const currentChild = prev[child];
                currentChild.disabled = disabledStates[child];
                return {...prev, [child]: {...prev[child], ...currentChild}};
            });
        });
        forceUpdate(); // TODO can be removed??

        onChange();
    }

    useEffect(() => {
        Object.keys(formFields).map((key: string) => {
            onUpdate(key, formFields[key].value);
        });
    }, [showSettings]);

    return <div className={`px-3 w-100 ${showSettings || "d-none"}`}>
        <form ref={formRef} className={"border-top py-2"}>
            {Object.keys(formFields).map((key: string) => {
                const field = formFields[key];
                if (field.type == "checkbox")
                    console.log("VALLLLLL:", field.value);
                return <div key={key}>
                    <CustomToolTip enabled={true} tooltipText={field.help_text} children={<>
                        <label htmlFor={field.name}>{field.label}</label>
                        {field.type === 'select' ?
                            (<select
                                value={field.value}
                                disabled={field.disabled}
                                onChange={((e) => onUpdate(field.name, e.target.value))}
                                name={field.name} required={field.required}
                            >{field.choices.map((choice) => (
                                <option key={choice.value}
                                        value={choice.value}>{choice.display}</option>
                            ))}</select>) :
                            field.type === 'checkbox' ?
                                (<input
                                    {
                                        ...Object.keys(field)
                                            .filter((f) => f != "value")
                                            .reduce((prev, f) => ({...prev, [f]: field[f]}), {})
                                    }
                                    checked={String(field.value) == "true"}
                                    onChange={((e) => onUpdate(field.name, "" + e.target.checked))}
                                />)
                                :
                                (<input
                                    {...field}
                                    onChange={((e) => onUpdate(field.name, e.target.value))}
                                />)
                        }
                    </>
                    }/>
                </div>
            })}
        </form>
    </div>;
}

export default SettingsContainer;