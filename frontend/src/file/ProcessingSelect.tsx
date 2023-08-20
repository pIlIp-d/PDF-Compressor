import { useEffect, useRef, useState} from "react";
import {Requester} from "../Requester.ts";
import {TabType} from "../App.tsx";

type ProcessingSelectProps = {
    disabled: boolean;
    currentProcessor: string;
    setProcessor: (processor: string)=>void;
    fileId: string;
    currentTab: TabType
}

type SelectOption = { [key: string]: [string] };

const ProcessingSelect = ({disabled, currentProcessor, setProcessor, fileId, currentTab}: ProcessingSelectProps) => {
    const [options, setOptions] = useState<SelectOption>({});
    const selectRef = useRef<HTMLSelectElement>(null);

    useEffect(() => {
        if (!disabled) {
            setProcessor("null");
            // get possible destination types and set them as option
            Requester(`/get_possible_destination_file_types/${fileId}`).then((response) => {
                if ("possible_file_types" in response.data) {
                    let types = response.data.possible_file_types;
                    for (const t in types) {
                        switch (currentTab) {
                            case "Convert":
                            case "Merge":
                                types[t] = types[t].filter((i: string) => i != "compression")
                                break;
                            case "Compress":
                                types[t] = types[t].filter((i: string) => i == "compression")
                                break;
                        }
                    }
                    types = filterOutEmptyLists(types);
                    setOptions(types);

                    // activate the option if there is only one
                    const amountOfOptions = Object.keys(types).reduce((prev, current) => prev + types[current].length, 0);
                    if (amountOfOptions == 1)
                        setProcessor(Object.keys(types)[0] + "-" + Object.values(types)[0]);

                }
            });
        }
    }, [disabled, currentTab]);

    useEffect(() => {
        if (selectRef.current)
            selectRef.current.value = currentProcessor;
    }, [currentProcessor]);

    return <>
        <select
            ref={selectRef}
            onChange={(event) => setProcessor(event.target.value)}
            defaultValue={"null"}>
            <option value={"null"}>...</option>
            {Object.keys(options).map((optionsKey, key1) => (
                <optgroup key={key1} label={optionsKey}>
                    {options[optionsKey].map((mime, key2) => (
                        <option key={key1 + "-" + key2} value={`${optionsKey}-${mime}`}>
                            {mime}
                        </option>
                    ))}
                </optgroup>
            ))}
        </select></>;
}

function filterOutEmptyLists(list: { [key: string]: string[] }) {
    const filteredKeys = Object.keys(list).filter((i, _) => list[i].length > 0);
    const filteredTypes: { [key: string]: string[] } = {};
    for (const key of filteredKeys) {
        filteredTypes[key] = list[key];
    }
    return filteredTypes;
}

export default ProcessingSelect;