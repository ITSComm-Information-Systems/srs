document.addEventListener("DOMContentLoaded", function(event) { 

    element = document.getElementById("id_managed");

    element.addEventListener("click", myFunction);

    function myFunction() {
        console.log('managed')
    }    

    //do work
});