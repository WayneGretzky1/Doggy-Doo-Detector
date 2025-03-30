document.addEventListener("DOMContentLoaded", function () {
    document.getElementById("stockForm").addEventListener("submit", async function (event) {
        event.preventDefault(); 

        const symbol = document.getElementById("symbol").value.trim();
        const apiKey = "2J6V3XZUVVLQ3UCH";
        const apiUrl = `https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=${symbol}&apikey=${apiKey}`;
        const stockDataPanel = document.getElementById("stockdata-panel");
        

        const response = await fetch(apiUrl);
        if (!response.ok) {
            console.log("Retrieval failed to load")
        }

        const data = await response.json();
        const timeSeries = data["Time Series (Daily)"];
        // console.log("timeSeries", timeSeries); 
        const formattedData = [];
        // console.log("formattedData", formattedData);
        for (const [date, dailyData] of Object.entries(timeSeries)) {
            formattedData.push({
                date: date,
                open: dailyData["1. open"],
                high: dailyData["2. high"],
                low: dailyData["3. low"],
                close: dailyData["4. close"],
                volume: dailyData["5. volume"],
            });
        }
        stockDataPanel.innerHTML = JSON.stringify(formattedData, null, 4); 
    });
});
