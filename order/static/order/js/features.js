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
        type = $(this).data('type');
        if (this.checked) {
            //$(".radio-addl").hide();
            $("[data-addl='" + type + "']").hide();
            $(div).show()
            $(id).select()
        } else {
            $(id).hide();
        }
    });

    if ($("#wftype").val() == "A") {
        $(".keep-features").hide();
    }

    $(".keep-check").click(function() {
        if (this.checked) {
            $(".form-row input:visible").attr("disabled","disabled");
            // Selecting all checked inout fields
            var checked;
            checked = $(".form-row input:visible:checked");
            // Looping through checked input fields and unchecking them
            for (var cnt = 0;cnt < checked.length; cnt++) {
                checked[cnt].checked=false;
            }
            
            // selecting all visible input types
            var text;
            text = $(".form-row input[type='text']:visible");
            // Looping through all the visible input fields to reset
            // their value and hide their parent div containers
            for (var txt =0;txt<text.length;txt++){
                text[txt].value = "";
                var div;
                // Hide the parent of the text input which is a div
                div =  $(text[txt]).parent();
                $(div).hide();
                // remove the disabled attribute from the input fields
                $(text[txt]).removeAttr("disabled");
            }
        }
    });


});