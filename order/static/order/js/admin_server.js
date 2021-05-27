document.addEventListener("DOMContentLoaded", function(event) { 

    document.getElementById("id_managed").addEventListener("change", function(){
        if (this.checked) {
            document.getElementsByClassName("managed-section")[0].disabled = false;
        } else {
            document.getElementsByClassName("managed-section")[0].disabled = true;
        }
        
    });
    
});