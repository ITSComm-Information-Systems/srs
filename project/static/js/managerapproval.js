document.addEventListener("DOMContentLoaded", function(event) {
    $("#manager_submit").attr("disabled", "disabled")
    $("#manager_reject").attr("disabled", "disabled")
    // get url parameters
    const urlParams = new URLSearchParams(window.location.search)
    $('.request_id').val(urlParams.get('id'))

    var review_table = $('#review_table').DataTable({
        "destroy": true,
        "lengthChange": false,
        "bFilter": false,
        "dom": 'rtp',
        "ordering": false,
        "processing": true,
        "language": {
            "processing": "Loading..."
        },
        "ajax": {
            url: '/managerapprovalinit/',
            data: {
                'id': urlParams.get('id')
            },
            dataSrc: "",
            dataType: 'json',
        },
        'columns': [
            { data: 'user_defined_id' },
            { data: 'building' },
            { data: 'mrc_account_number' },
            { data: 'toll_account_number' },
            { data: 'local_account_number' }
        ],
    })
    review_table.on("xhr", function () {
        $("#manager_submit").removeAttr("disabled")
        $("#manager_reject").removeAttr("disabled")
        for (user of review_table.ajax.json()) {
            for (key in user) {
                //Fills in information based on class
                $("." + key).html(user[key]) 
                if (key == "old_dept_mgr_uniqname") {
                    $(".old_dept_mgr_email").html(user[key] + "@umich.edu")
                }
                if (key == "new_dept_mgr_uniqname") {
                    $(".new_dept_mgr_email").html(user[key] + "@umich.edu")
                }
                // uniqname
                $('#' + key).val(user[key])
            }
        }
    })
    $("#confirmAccept").on("click", function () {
        $("#manager_submit").attr("disabled", "disabled");
        $("#manager_reject").attr("disabled", "disabled");
        accept();
    });
    $("#confirmReject").on("click", function () {
        $("#manager_submit").attr("disabled", "disabled");
        $("#manager_reject").attr("disabled", "disabled");
        reject();
    });


function accept() {
    document.getElementById("loading").style.display= "block";
    $.ajax({
        url: "submit/",
        type: "POST",
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            status:'accepted',
            request_id: document.getElementById('request_id').value,
            uniqname: document.getElementById('uniqname').value,
            optional_message: document.getElementById('optional_message').value,
            approver: document.getElementById('approver').value, //Approved by uses request.user.username
        },

        // handle a successful response
        success: function (json) {
            document.getElementById("loading").style.display= "none";
            $(".page_4_style").addClass("bg-success")
            $(".page_4_style").addClass("text-white")
            document.getElementById('page_4_top_text').classList.add('alert', 'alert-success')
            $("#page_4_top_text").html("Accepted! The Requestor will be notified and access will be automatically granted shortly. You may leave this page.")
            $("#manager_submit").attr("disabled", "disabled")
            $("#manager_reject").attr("disabled", "disabled")
        },

    });
}

function reject() {
    document.getElementById("loading").style.display= "block";
    $.ajax({
        url: "submit/",
        type: "POST",
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            rejectmessage: document.getElementById('rejectmessage').value,
            status:'rejected',
            request_id: document.getElementById('request_id').value,
            uniqname: document.getElementById('uniqname').value,
            approver: document.getElementById('approver').value, //Approved by uses request.user.username

        },
        success: function (json) {
            document.getElementById("loading").style.display= "none";
            $(".page_4_style").addClass("bg-danger")
            $(".page_4_style").addClass("text-white")
            document.getElementById('page_4_top_text').classList.add('alert','alert-danger')
            $("#page_4_top_text").html("Rejected! The Requestor will be notified shortly. You may leave this page.")
            $("#manager_submit").attr("disabled", "disabled")
            $("#manager_reject").attr("disabled", "disabled")
        },
    });
}

});