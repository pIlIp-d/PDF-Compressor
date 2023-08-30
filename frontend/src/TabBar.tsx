import {TabType} from "./App.tsx";

type TabBarProps = {
    currentTab: TabType;
};

const TabBar = ({currentTab}: TabBarProps) => {
    return <ul className="nav nav-tabs">
        <li className="nav-item">
            <a className={`text-dark nav-link ${currentTab === "Convert" && "active fw-bold"}`}
               href="#Convert">Convert</a>
        </li>
        <li className="nav-item">
            <a className={`text-dark nav-link ${currentTab === "Compress" && "active fw-bold"}`}
               href="#Compress">Compress</a>
        </li>
        <li className="nav-item">
            <a className={`text-dark nav-link ${currentTab === "Merge" && "active fw-bold"}`}
               href="#Merge">Merge</a>
        </li>
    </ul>;
}

export default TabBar;