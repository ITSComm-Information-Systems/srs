$(document).ready(function () {
    $('[data-toggle="popover"]').popover();

    $("input:checkbox").click(function() {
        id = "#addinfo" + this.id.substring(3,30);
        div = $(id).parent();
        if (this.checked) {
            $(div).show()
            $(id).select()
        } else {
            $(div).hide();
        }
    });

    $("input:radio").click(function() {
        id = "#addinfo" + this.id.substring(3,30);
        div = $(id).parent();
        console.log(div);
        if (this.checked) {
            $(".radio-addl").hide();
            $(div).show()
            $(id).select()
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