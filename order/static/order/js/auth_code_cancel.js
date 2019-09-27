$(document).ready(function() {

    $('[data-tab="AuthCodeCancel"]').on('shown.bs.tab', function(event) {

        max = $("#id_CodeCount").val();

        for (i = 1; i < max; i++) {

            num = i.toString();

            var rec = $("#authdiv").clone();

            rec.attr("id", "authdiv" + num);

            rec.find("#cancel").attr("name", "type" + num).attr("id", "cancel" + num);
            rec.find("label[for='cancel']").attr("for", "cancel" + num);
        
            rec.find("#change").attr("name", "type" + num).attr("id", "change" + num);
            rec.find("label[for='change']").attr("for", "change" + num);
        
            rec.find("#auth").attr("name", "auth" + num).attr("id","auth" + num);

            rec.find("#authName").attr("name", "auth" + num).attr("id","auth" + num);

            $("#mainBody").append(rec);

        }
    })



});