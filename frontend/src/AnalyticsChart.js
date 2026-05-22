import {
    BarChart,
    Bar,
    XAxis,
    YAxis,
    CartesianGrid,
    Tooltip,
    ResponsiveContainer
} from "recharts";

function AnalyticsChart({ topPerformers = [] }) {

    // SAFE DATA
    const chartData = (topPerformers || []).map((employee) => ({

        name: employee[0],

        profit: employee[1].profit

    }));


    return (

        <div className="card shadow p-4 mt-4">

            <h3 className="mb-4">
                Top Performer Analytics
            </h3>

            <ResponsiveContainer
                width="100%"
                height={400}
            >

                <BarChart data={chartData}>

                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis dataKey="name" />

                    <YAxis />

                    <Tooltip />

                    <Bar dataKey="profit" />

                </BarChart>

            </ResponsiveContainer>

        </div>
    );
}

export default AnalyticsChart;