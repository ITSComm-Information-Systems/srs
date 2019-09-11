$(document).ready(function() {

    $('[data-tab="CMC"]').on('shown.bs.tab', function(event) {

        max = $("#id_CodeCount").val();

        for (i = 1; i < max; i++) {

            num = i.toString();

            var rec = $("#authdiv").clone();

            rec.attr("id", "authdiv" + num);

            //rec.find("#workgroup").attr("name", "type" + num).attr("id", "workgroup" + num);
            //rec.find("label[for='workgroup']").attr("for", "workgroup" + num);
        
            //rec.find("#individual").attr("name", "type" + num).attr("id", "individual" + num);
            //rec.find("label[for='individual']").attr("for", "individual" + num);
        
            rec.find("#auth").attr("name", "auth" + num).attr("id","auth" + num);
        
            $("#mainBody").append(rec);

        }
    })



});