type ProgressBarProps = {
    progress: number;
    isGreen: boolean;
}
const ProgressBar = ({progress, isGreen}: ProgressBarProps) => {
    return <div className="progress" style={{height: "2px"}}>
        <div className={`progress-bar ${isGreen ? "bg-success": "bg-danger"}`}
             role="progressbar" aria-valuenow={progress}
             aria-valuemin="0"
             aria-valuemax="100" style={{width: progress + "%"}}></div>
    </div>;
}
export default ProgressBar;