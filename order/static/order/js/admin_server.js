document.addEventListener("DOMContentLoaded", function(event) { 

    document.getElementById("id_managed").addEventListener("change", function(){
        if (this.checked) {
            document.getElementsByTagName("fieldset")[1].disabled = true;
        } else {
            document.getElementsByTagName("fieldset")[1].disabled = false;
        }
    });

    
});