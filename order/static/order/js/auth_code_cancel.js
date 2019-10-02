$(document).ready(function() {

    $('[data-tab="AuthCodeCancel"]').on('shown.bs.tab', function(event) {

        max = $("#id_CodeCount").val();
        num = $(".form-row").length;

        for (i = num; i < max; i++) {

            num = i.toString();

            var rec = $("#authdiv").clone();

            rec.attr("id", "authdiv" + num);

            rec.find("#cancel").attr("name", "type" + num).attr("id", "cancel" + num);
            rec.find("label[for='cancel']").attr("for", "cancel" + num);
        
            rec.find("#change").attr("name", "type" + num).attr("id", "change" + num);
            rec.find("label[for='change']").attr("for", "change" + num);
        
            rec.find("#sub").attr("name", "sub" + num).attr("id","sub" + num);

            rec.find("#group").attr("name", "group" + num).attr("id","group" + num);

            $("#mainBody").append(rec);

        }
    })



});