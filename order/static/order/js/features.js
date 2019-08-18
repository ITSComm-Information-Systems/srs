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
});