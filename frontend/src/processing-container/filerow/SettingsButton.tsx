type SettingsButtonProps = {
    disabled: boolean;
    onClick: () => void;
}
const SettingsButton = ({disabled, onClick}: SettingsButtonProps) => {
    return <span role={disabled ? undefined : "button"}
                 className={`m-auto bi bi-sliders ${disabled && "opacity-50"}`}
                 onClick={disabled ? undefined : onClick}>
    </span>;
}
export default SettingsButton;