import CustomToolTip from "./utils/CustomToolTip.tsx";

type FileIconProps = {
    showTooltip: boolean;
    toolTipText: string;
}
const FileIcon = ({showTooltip ,toolTipText}: FileIconProps) => {
    return <div id={"file-icon"}>
        <CustomToolTip enabled={showTooltip} tooltipText={toolTipText} children={
            <span className={"bi bi-file-earmark-text"}/>
        }/>
    </div>;
}
export default FileIcon;