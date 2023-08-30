import {TabType} from "../App.tsx";
import {useLocation} from "react-router-dom";
import {Dispatch, SetStateAction, useEffect} from "react";

type TabBarProps = {
    currentTab: TabType;
    setCurrentTab: Dispatch<SetStateAction<TabType>>;
};

const TabBar = ({currentTab, setCurrentTab}: TabBarProps) => {
    const location = useLocation()
    useEffect(() => {
        const tab = location.hash.substring(1);
        switch (tab) {
            case "Convert":
            case "Compress":
            case "Merge":
                setCurrentTab(tab);
                break;
            default:
                setCurrentTab("Convert");
        }
    }, [location]);

    return <ul className="nav nav-tabs">
        <li className="nav-item">
            <a className={`text-dark nav-link ${currentTab === "Convert" && "active fw-bold bg-white"}`}
               href="#Convert">Convert</a>
        </li>
        <li className="nav-item">
            <a className={`text-dark nav-link ${currentTab === "Compress" && "active fw-bold bg-white"}`}
               href="#Compress">Compress</a>
        </li>
        <li className="nav-item">
            <a className={`text-dark nav-link  ${currentTab === "Merge" && " active fw-bold bg-white"}`}
               href="#Merge">Merge</a>
        </li>
    </ul>;
}

export default TabBar;