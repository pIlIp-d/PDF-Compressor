/* based on https://react-select.com */

import {CSSProperties} from 'react';

import Select from 'react-select';
import Dropdown, {Group} from 'react-dropdown';
import 'react-dropdown/style.css';

const groupStyles = {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
};
const groupBadgeStyles: CSSProperties = {
    backgroundColor: '#EBECF0',
    borderRadius: '2em',
    color: '#172B4D',
    display: 'inline-block',
    fontSize: 12,
    fontWeight: 'normal',
    lineHeight: '1',
    minWidth: 1,
    padding: '0.16666666666667em 0.5em',
    textAlign: 'center',
};

export interface GroupedOption {
    readonly label: string;
    readonly options: readonly SelectOption[];
}

interface SelectOption {
    readonly value: string;
    readonly label: string;
    readonly color?: string;
    readonly isFixed?: boolean;
    readonly isDisabled?: boolean;
}

const formatGroupLabel = (data: GroupedOption) => (
    <div style={groupStyles}>
        <span>{data.label}</span>
        <span style={groupBadgeStyles}>{data.options.length}</span>
    </div>
);

type NestedSelectProps = {
    options: Group[];
    disabled: boolean;
}


const NestedSelect = ({options, disabled}: NestedSelectProps) => {
    // @ts-ignore
    return <Dropdown
        options={options}
        onChange={console.log}
        value={"..."}
        disabled={disabled}
        placeholder="..."/>;
}
export default NestedSelect;