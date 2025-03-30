function clock() {
    const clk = new Date();
    const hr24 = clk.getHours();
    let meridiem = hr24.toString() >= 12 ? 'PM' : 'AM';
    let hr = hr24 >= 12 ? hr24 - 12 : hr24;
    const min = clk.getMinutes().toString();
    const sec = clk.getSeconds().toString();
    

    const time = `
    <table border-collapse="collapse">
        <tr><td>Hour</td><td>Min</td><td>Sec</td><td>Meridiem</td></tr>
        <tr><td>${hr}</td><td>${min}</td><td>${sec}</td><td>${meridiem}</td></tr>
    </table>
    `;

    return time;

}

function displayClock() {
    const clockContainer = document.querySelector('.clock-container');
    if (clockContainer) {
        clockContainer.innerHTML = clock();
    } else {
        console.error("Element '.clock-container' not found in DOM.");
    }
}

document.addEventListener("DOMContentLoaded", () => {
    setInterval(displayClock, 1000);
    displayClock();
});
// window.addEventListener( "load", start, false );
// setInterval(displayClock, 1000);
// displayClock();