document.addEventListener("DOMContentLoaded", function(event) { 
    MDB_ADMIN_GROUP = 1110;

    document.getElementById("id_managed").addEventListener("change", function(){
        if (this.checked) {
            document.getElementsByClassName("managed-section")[0].disabled = false;
        } else {
            document.getElementsByClassName("managed-section")[0].disabled = true;
        }
    });

    set_db_type();

    function set_db_type() {
        console.log('MDB_ADMIN_GROUP', MDB_ADMIN_GROUP);
        db_type = document.getElementById("id_database_type")
        if (document.getElementById("id_admin_group").value==MDB_ADMIN_GROUP) {
            db_type.disabled = false;
        } else {
            db_type.disabled = true;
            db_type.value = null;            
        }
    }

    document.getElementById("id_admin_group").addEventListener("change", function(){
        set_db_type();
    });


});