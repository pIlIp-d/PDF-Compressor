import CustomToolTip from "./utils/CustomToolTip.tsx";
import {toast} from "react-toastify";
import {useEffect} from "react";

type FileIconProps = {
    toolTipText: string;
}
const FileIcon = ({toolTipText}: FileIconProps) => {
    useEffect(() => {
        if (toolTipText) {
            toast.error(toolTipText, {
                position: "bottom-center",
                autoClose: false,
                hideProgressBar: false,
                closeOnClick: true,
                pauseOnHover: true,
                draggable: true,
                progress: undefined,
                theme: "colored",
            });
        }

    }, [toolTipText]);
    return <div id={"file-icon"}>
        <CustomToolTip enabled={toolTipText != ""} tooltipText={toolTipText} children={
            <span style={{color: toolTipText != "" ? "var(--bs-danger)" : "black"}}
                  className={`bi ${toolTipText != "" ? "bi-exclamation-triangle" : "bi-file-earmark-text"}`}/>
        }/>
    </div>;
}
export default FileIcon;