let iconImg = null;
let intervalID = null; 
var pictures = [ "/static/img/Anderson.jpg", "/static/img/shepherd.jpg", "/static/img/Anderson.jpg", "/static/img/keller.jpg", "/static/img/track.jpg", "/static/img/swim.jpg", "/static/img/vanCleve.jpg" ];
var descriptions = [ "Anderson", 
   "Shepherd", "Anderson", 
   "Keller", "track", "Swim", 
   "vanCleve" ];
var index = 0;



// displays the big picture on mouseover of the 1st 
function showBigPic(num) {
    // window.alert("got to showBigPic number is " + num);
    bigpic = document.getElementById("big");
    if (parseInt(num) == 1) {
        bigpic.src = "/static/img/Anderson.jpg";
        bigpic.alt = "Anderson"
    }
    if (parseInt(num) == 2) {
        bigpic.src = "/static/img/shepherd.jpg";
        bigpic.alt = "shepherd"
    }
    if (parseInt(num) == 3) {
        bigpic.src = "/static/img/Anderson.jpg";
        bigpic.alt = "Anderson"
    }
    if (parseInt(num) == 4) {
        bigpic.src = "/static/img/keller.jpg";
        bigpic.alt = "Keller"
    }
    if (parseInt(num) == 5) {
        bigpic.src = "/static/img/track.jpg";
        bigpic.alt = "Track"
    }
    if (parseInt(num) == 6) {
        bigpic.src = "/static/img/swim.jpg";
        bigpic.alt = "Swim"
    }
    if (parseInt(num) == 7) {
        bigpic.src = "/static/img/vanCleve.jpg";
        bigpic.alt = "vanCleve"
    }
}

function pickImage()
{
   console.log("pick");
   iconImg.setAttribute( "src", pictures[ index ] );
   iconImg.setAttribute( "alt", descriptions[ index ] );
   index = (index + 1) % pictures.length; //whatever the length is
} // end function pickImage


function start() {
    console.log("start");
    if (!iconImg) {
        iconImg = document.getElementById("big"); 
    }
    if (!intervalID) {
        intervalID = setInterval(pickImage, 1000); 
    }
}


function stop() {
    console.log("stop");
    if (intervalID) {
        clearInterval(intervalID); 
        intervalID = null; 
    }
}


