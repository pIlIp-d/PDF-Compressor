import {useEffect, useRef, useState} from "react";
import {Requester} from "../Requester.ts";
import {TabType} from "../App.tsx";

type ProcessingSelectProps = {
    disabled: boolean;
    currentProcessor: string;
    setProcessor: (processor: string) => void;
    currentTab: TabType;
    fileIds: string[] | string;
    setInputFileTypes: (types: { [key: string]: string[] }) => void;
}

type SelectOption = {
    [key: string]: string[]
};

const ProcessingSelect = ({
                              disabled,
                              currentProcessor,
                              setProcessor,
                              currentTab,
                              fileIds,
                              setInputFileTypes
                          }: ProcessingSelectProps) => {
    const [options, setOptions] = useState<SelectOption>({});
    const selectRef = useRef<HTMLSelectElement>(null);

    console.log(fileIds, typeof fileIds == "string" ? fileIds : Array.from(fileIds).join(","))
    useEffect(() => {
        if (!disabled) {
            // get possible destination types and set them as option
            Requester(`/get_possible_destination_file_types?file_ids=${typeof fileIds == "string" ? fileIds : Array.from(fileIds).join(",")}`).then((response) => {
                if ("possible_file_types" in response.data) {
                    let types: { [key: string]: string[] } = {};
                    switch (currentTab) {
                        case "Convert":
                            Object.keys(response.data.possible_file_types).map((key: string) => {
                                types[key] = response.data.possible_file_types[key].filter((i: string) => i != "compression")
                            });
                            break;
                        case "Merge":
                            Object.keys(response.data.possible_file_types).map((key: string) => {
                                if (key in response.data.list_of_mergers && response.data.list_of_mergers[key])
                                    types[key] = response.data.possible_file_types[key];
                            });
                            break;
                        case "Compress":
                            Object.keys(response.data.possible_file_types).map((key: string) => {
                                types[key] = response.data.possible_file_types[key].filter((i: string) => i == "compression")
                            });
                            break;
                    }
                    types = filterOutEmptyLists(types);
                    setOptions(types);

                    if ("input_file_types" in response.data) {
                        setInputFileTypes(response.data.input_file_types);
                    }

                    if (typeof fileIds == "string") { // is for file row
                        // activate the option if there is only one
                        const amountOfOptions = Object.keys(types).reduce((prev, current) => prev + types[current].length, 0);
                        if (amountOfOptions == 1)
                            setProcessor(Object.keys(types)[0] + "-" + Object.values(types)[0][0]);
                    } else if (
                        !Object.keys(types).reduce(
                            (prev: string[], t: string) => [...prev, ...types[t].map(val => `${t}-${val}`)], []
                        ).includes(currentProcessor)
                    ) {
                        // reset processor if the previous selected one isn't possible anymore
                        setProcessor("null");
                    }
                }
            });
        }
    }, [disabled, currentTab, fileIds]);

    useEffect(() => {
        if (selectRef.current) {
            if (currentProcessor == "null" || Object.keys(options).some(optionsKey => options[optionsKey].some(mime => `${optionsKey}-${mime}` == currentProcessor)))
                selectRef.current.value = currentProcessor;
            else
                setProcessor("null");
        }
    }, [currentProcessor]);

    return <select disabled={disabled}
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
    </select>;
}

function filterOutEmptyLists(list: {
    [key: string]: string[]
}) {
    const filteredKeys = Object.keys(list).filter((i, _) => list[i].length > 0);
    const filteredTypes: { [key: string]: string[] } = {};
    for (const key of filteredKeys) {
        filteredTypes[key] = list[key];
    }
    return filteredTypes;
}

export default ProcessingSelect;