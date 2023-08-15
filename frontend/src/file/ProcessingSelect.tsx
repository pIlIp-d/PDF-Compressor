import {Dispatch, SetStateAction, useEffect, useRef, useState} from "react";
import {Requester} from "../Requester.ts";
import {Simulate} from "react-dom/test-utils";
import select = Simulate.select;

type ProcessingSelectProps = {
    disabled: boolean;
    currentProcessor: string;
    setProcessor: Dispatch<SetStateAction<string>>;
    fileId: string;
}

type SelectOption = { [key: string]: [string] };

const ProcessingSelect = ({disabled, currentProcessor, setProcessor, fileId}: ProcessingSelectProps) => {
    const [options, setOptions] = useState<SelectOption>({});
    const selectRef = useRef<HTMLSelectElement>(null);

    useEffect(() => {
        if (!disabled) {
            // get possible destination types and set them as option
            Requester(`/get_possible_destination_file_types/${fileId}`).then((response) => {
                if ("possible_file_types" in response.data) {
                    let types = response.data.possible_file_types;
                    const listOfTypes = deduplicate(flattenObjectOfLists(types));
                    types = filterOutEmptyLists(types);

                    // put the types into the types-list (f.e image/png -> {'image': 'png'}
                    types = {...types, ...categorizeByMimeType(listOfTypes)};

                    setOptions(prevOptions => {
                        return {...prevOptions, ...types};
                    });
                }
            });
        }
    }, [disabled]);

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

function flattenObjectOfLists(obj: { [key: string]: any[] }) {
    const flattenedList = [];
    for (const key of Object.keys(obj))
        for (const element of obj[key])
            flattenedList.push(element);
    return flattenedList;
}

function deduplicate(list: any[]): any[] {
    return list.filter((item, pos) => list.indexOf(item) == pos);
}

function categorizeByMimeType(listOfTypes: string[]) {
    const resultingDict: { [key: string]: string[] } = {};
    for (const raw_type of listOfTypes) {
        const category = raw_type.split("/", 1)[0];
        if (raw_type.includes("/")) {
            if (!(category in resultingDict))
                resultingDict[category] = [];
            resultingDict[category].push(raw_type.split("/", 2)[1]);
        }
    }
    return resultingDict;
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