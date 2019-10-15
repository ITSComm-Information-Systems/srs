$(document).ready(function() {

    $('[data-tab="CMC"]').on('shown.bs.tab', function(event) {

        max = $("#id_CodeCount").val();

        for (i = 1; i < max; i++) {

            num = i.toString();

            var rec = $("#cmcdiv").clone();

            rec.find("#cmc").attr('data-label', "Code " + num);

            rec.attr("id", "cmcdiv" + num);

            //rec.find("#workgroup").attr("name", "type" + num).attr("id", "workgroup" + num);
            //rec.find("label[for='workgroup']").attr("for", "workgroup" + num);
        
            //rec.find("#individual").attr("name", "type" + num).attr("id", "individual" + num);
            //rec.find("label[for='individual']").attr("for", "individual" + num);
            rec.find("label[for='cmc']").attr("for", "cmc" + num);
            rec.find("#cmc").attr("name", "auth" + num).attr("id","cmc" + num);
            

        
            $("#mainBody").append(rec);

        }
    })



});