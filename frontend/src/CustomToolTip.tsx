import {Tooltip} from "react-tooltip";
import {ReactNode} from "react";
import {v4 as uuidv4} from 'uuid';

type CustomToolTipProps = {
    tooltipText: string;
    enabled: boolean;
    children?: ReactNode;
}

const CustomToolTip = ({tooltipText, enabled, children}: CustomToolTipProps) => {
    const id = uuidv4();
    return <><Tooltip id={id}/>
        <a data-tooltip-id={id} data-tooltip-content={enabled ? tooltipText: ""}>
            {children}
        </a>
    </>;
}

export default CustomToolTip;