$(document).ready(function () {
    $('[data-toggle="popover"]').popover();

    $("input:checkbox").click(function() {
        id = "#addinfo" + this.id.substring(3,30);
        if (this.checked) {
            $(id).show().select()

        } else {
            $(id).hide();
        }
    });

    if ($("#wftype").val() == "A") {
        $("#currentFeatures").hide();
    }

    $("#keepFeatures").click(function() {
        if (this.checked) {
            $(".form-row input:visible").attr("disabled","disabled");
        } else {
            $(".form-row input:visible").removeAttr("disabled");
        }
    });


});