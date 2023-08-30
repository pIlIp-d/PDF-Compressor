type FileProcessingButtonProps = {
    isDownloadButton: boolean;
    isLoading: boolean;
    isDisabled: boolean;
    text: string;
    onClick: () => void;
    additionalText?: string;
}
const FileProcessingButton = ({isDownloadButton, isLoading, isDisabled, text, onClick, additionalText = ""}: FileProcessingButtonProps) => {
    return <button
        className={`btn ${isDownloadButton ? "btn-success" : "btn-secondary"}`}
        disabled={isDisabled}
        onClick={onClick}>
        {isDownloadButton ? "Download" : isLoading ? "Loading" : text}{additionalText}
        {isLoading && <>
            <span> </span><div className="spinner-border spinner-border-sm" role="status"
                 style={{"animationDuration": "2s"}}>
                <span className="visually-hidden">...</span>
            </div>
            </>
        }
    </button>;
}
export default FileProcessingButton;