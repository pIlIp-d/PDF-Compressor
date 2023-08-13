const DropZoneTemplate = () => {
    return (
        <div className="table table-striped files" id="previews">
            <div id="template" className="file-row">
                <div>
                    <span className="preview"><img data-dz-thumbnail/></span>
                </div>
                <div>
                    <p className="name" data-dz-name></p>
                    <strong className="error text-danger" data-dz-errormessage></strong>
                </div>
                <div>
                    <p className="size" data-dz-size></p>
                    <div className="progress progress-striped active" role="progressbar" aria-valuemin={"0"} aria-valuemax={"100"} aria-valuenow={"0"}>
                        <div className="progress-bar progress-bar-success" style={{"width": "0%"}}
                             data-dz-uploadprogress>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default DropZoneTemplate;