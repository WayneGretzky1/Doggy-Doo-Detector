// Referenced from gmdemo_server 
let geocoder;
let Place;
let myPos;
let data = [];
let map;
let directionsRenderer;



let InfoWindow;
let AdvancedMarkerElement;
let PlaceAutocompleteElement;


function getAddress(DOM) {
    let addy = DOM.cells[3].innerHTML.split("<", 1); // remove the thumbnail
    return addy[0];
}
function getName(DOM) {
    let name = DOM.cells[1].innerHTML;
    return name;
}
function getDay(DOM) {
    let day = DOM.cells[0].innerHTML;
    return day;
}
function getTime(DOM) {
    let time = DOM.cells[2].innerHTML;
    return time;
}

async function initMap() {

    // create the map
    const { Map } = await google.maps.importLibrary("maps");
    map = new Map(document.getElementById("maps"), {
        center: new google.maps.LatLng(44.9727, -93.23540000000003),
        zoom: 15,
        mapId: "HW3_DEMO2",
    });

    // only call this once so that the route clears for a new mode of transportation
    directionsRenderer = new google.maps.DirectionsRenderer();
    directionsRenderer.setMap(map); 
    directionsRenderer.setPanel(document.getElementById("directions-panel"));

    // Get the geocoder in place
    if (!geocoder) {
        const { Geocoder } = await google.maps.importLibrary("geocoding");
        geocoder = new Geocoder();
    }

     // This is the location we will search for using the geocoder in this example
    /* For your Homework assignment 3, you will have to create the code to return the values of the locations
        on your schedule, dynamically (they can not be hard coded)
    */
   
    // Grab my DOM objects
    let Pillsbury = document.getElementById("Pillsbury");
    data.push(Pillsbury);
    let YMCA  = document.getElementById("YMCA");
    data.push(YMCA);
    let Afton  = document.getElementById("Afton");
    data.push(Afton);
    let VanCleve  = document.getElementById("VanCleve");
    data.push(VanCleve);


    // https://developers.google.com/maps/documentation/javascript/geocoding
    data.forEach((DOM, index) => {
        geocoder.geocode({ "address" : getAddress(DOM) }, (results, status) => {
            
            if (status !== "OK") {
                if (status === "ZERO_RESULTS") {
                    return;
                }
                console.error(
                    "Geocoder was not successful for the following reason: " + status,
                );
            }
            
            const goldy = document.createElement("img");
            goldy.src = "/static/img/Goldy.png";
            goldy.alt = "Goldy marker!";
            goldy.style.height = "40px";
            goldy.style.width = "40px";
            goldy.style.display = "block";
            // console.log("dom results", results);
            // console.log("dom status", status);
            return createMarker({
                position: results[0].geometry.location,
                windowContent: `${getName(DOM)}<br>${getDay(DOM)}, ${getTime(DOM)}`,
                markerContent: goldy,  // this is where to include a graphic marker - see comment below
            });
        });
});

    // See the following link for information on how to create an image to be used within an AdvancedMarkerElement
    // https://developers.google.com/maps/documentation/javascript/advanced-markers/graphic-markers#custom-graphic-file

    async function createMarker({ windowContent, markerContent, position }) {
        if (!InfoWindow) {
            const maps = await google.maps.importLibrary("maps");
            InfoWindow = maps.InfoWindow;
        }

        if (!AdvancedMarkerElement) {
            const marker = await google.maps.importLibrary("marker");
            AdvancedMarkerElement = marker.AdvancedMarkerElement;
        }

        // See the following link for discussion about advanced markers and adding a marker
        // https://developers.google.com/maps/documentation/javascript/advanced-markers/add-marker#javascript
        const marker = new AdvancedMarkerElement({
                                map,
                                position,
                                content: markerContent,
                        });

        if (windowContent) {
            const infoWindow = new InfoWindow({
                    content: windowContent,
                    maxWidth: 300,
                });

            marker.addListener("click", () => {
                infoWindow.close();
                infoWindow.setContent(windowContent);
                infoWindow.open(map, marker);
            });
        }
    } // end createMarker

    if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
            (position) => {
                myPos = {
                    lat: position.coords.latitude,
                    lng: position.coords.longitude,
                };
            },
            () => {
                console.warn("Current location unavailable");
            },
        );
    }
    
} // end initMap

// https://developers.google.com/maps/documentation/javascript/examples/directions-panel
// reference for event handler
document.getElementById("directionForm").addEventListener("submit", getDirections);


initMap();

// https://developers.google.com/maps/documentation/javascript/examples/directions-simple this is the reference for the directions tutorial 
async function getDirections(event) {
    event.preventDefault(); // Prevent form submission from reloading the page
    // console.log("map", map);
    // console.log("mypos", myPos);
    const destinationAddress = document.getElementById('destination').value;
    const mode = document.querySelector('input[name="mode"]:checked').value;
    // console.log("dest", destinationAddress);
    


    const directionsService = new google.maps.DirectionsService();
    directionsRenderer.setDirections(null); // Clear the current route


    geocoder.geocode({ address: destinationAddress }, (results, status) => {
        if (status === "OK") {
            const destinationLatLng = results[0].geometry.location;


            const request = {
                origin: myPos, 
                destination: destinationLatLng,
                travelMode: mode.toUpperCase(), // Convert to uppercase for API
            };


            directionsService.route(request, (response, status) => {
                if (status === "OK") {
                    directionsRenderer.setDirections(response);
                    const route = response.routes[0].legs[0];
                    document.getElementById('output').innerText = `
                        Distance: ${route.distance.text}
                        Duration: ${route.duration.text}
                        Start Address: ${route.start_address}
                        End Address: ${route.end_address}
                    `;
                } 
                
                else {
                    console.error(
                        "Directions was not successful for the following reason: ", status);
                }
            });
        } 
        
        else {
            console.error(
            "Geocoder was not successful for the following reason: " + status);
        }
    });

}



