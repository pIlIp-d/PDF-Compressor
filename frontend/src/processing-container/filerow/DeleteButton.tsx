type DeleteButtonProps = {
    onClick: () => void;
    disabled: boolean;
    additionalText?: string;
}
const DeleteButton = ({onClick, disabled, additionalText = ""}: DeleteButtonProps) => {
    return <span
        role={"button"}
        className={`m-auto delete-btn bi bi-x-lg ${disabled && "pe-none opacity-50"}`}
        onClick={onClick}
    >{additionalText}</span>;
}
export default DeleteButton;