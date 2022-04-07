import './App.css';

export default ({
    reportingAndInterpretation
}) => {
    if (reportingAndInterpretation === {} || reportingAndInterpretation === undefined) {
        return null
    }
    return (
        <div className="rowBlock">
            <div className="blockBlock">
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Run Name
                    </div>
                    <div className="text-color-reporting-result">
                        {reportingAndInterpretation?.run_game}
                    </div>
                </div>
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Report Name
                    </div>
                    <div className="text-color-reporting-result">
                        {reportingAndInterpretation?.report_name}
                    </div>
                </div>
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Dependencies
                    </div>
                    {reportingAndInterpretation?.dependencies?.map((dependency, index) => {
                        return (
                            <div key={index} className="text-color-reporting-result">
                                {dependency}
                            </div>
                        )
                    })}
                </div>
            </div>
            <div className="blockBlock">
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Original Run Date
                    </div>
                    <div className="text-color-reporting-result">
                        {reportingAndInterpretation?.original_run_date}
                    </div>
                </div>
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Latest Plugin Run Date
                    </div>
                    <div className="text-color-reporting-result">
                        {reportingAndInterpretation?.latest_plugin_run_date}
                    </div>
                </div>
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Total Samples in Run
                    </div>
                    <div className="text-color-reporting-result">
                        {reportingAndInterpretation?.total_samples_in_run}
                    </div>
                </div>
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Total Panels in Run
                    </div>
                    <div className="text-color-reporting-result">
                        {reportingAndInterpretation?.total_panels_in_run}
                    </div>
                </div>
            </div>
            <div className="blockBlocks">
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Reports Generated
                    </div>
                    <div className="text-color-reporting-result">
                        {reportingAndInterpretation?.reports_generated}
                    </div>
                </div>
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Customer Data Uploaded
                    </div>
                    <div className="text-color-reporting-result">
                        {reportingAndInterpretation?.customer_data_uploaded}
                    </div>
                </div>
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Customers in Run
                    </div>
                    <div className="text-color-reporting-result">
                        {reportingAndInterpretation.customers_in_run}
                    </div>
                </div>
                <div className="blockHorizontal">
                    <div className="text-color-reporting">
                        Samples Failed
                    </div>
                    <div className="text-color-reporting-result">
                        {reportingAndInterpretation.samples_failed}
                    </div>
                </div>
            </div>
        </div>
    )
}