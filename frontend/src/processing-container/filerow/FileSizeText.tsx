import {humanReadableFileSize} from "./utils/humanReadableFileSize.ts";

type FileSizeTextProps = {
    sizeBefore:number;
    sizeAfter:number;
    showSizeAfter: boolean;
}
const FileSizeText = ({sizeBefore, sizeAfter, showSizeAfter}: FileSizeTextProps) => {

    return <span className={`fw-lighter fs-7 text-end mx-2`}>
        {humanReadableFileSize(sizeBefore)}
        {
            showSizeAfter && <>
                <i className="bi bi-arrow-right-short"></i>
                <span className={"text-success"}>{humanReadableFileSize(sizeAfter)}</span>
            </>
        }
    </span>;
}
export default FileSizeText;