$(document).ready(function () {
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
                $("." + key).html(user[key]) //Fills in information based on id
                if (key == "old_dept_mgr_uniqname") {
                    $("#old_dept_mgr_email").html(user[key] + "@umich.edu")
                }
                if (key == "new_dept_mgr_uniqname") {
                    $("#new_dept_mgr_email").html(user[key] + "@umich.edu")
                }
                $('#' + key).val(user[key])
            }
        }
    })
    $("#confirmAccept").on("click", function () {
        accept();
    });
    $("#confirmReject").on("click", function () {
        reject();
    });
});

function accept() {
    $.ajax({
        url: "submit/",
        type: "POST",
        data: {
            csrfmiddlewaretoken: $('input[name=csrfmiddlewaretoken]').val(),
            status:'accepted',
            request_id: document.getElementById('request_id').value,
            uniqname: document.getElementById('uniqname').value,
            user_defined_id: document.getElementById('user_defined_id').value,
            mrc_account_number: document.getElementById('mrc_account_number').value,
            toll_account_number: document.getElementById('toll_account_number').value,
            local_account_number: document.getElementById('local_account_number').value,
            approver: document.getElementById('approver').value,
            optional_message: document.getElementById('optional_message').value
        },

        // handle a successful response
        success: function (json) {
            $(".page_4_style").addClass("bg-success")
            $(".page_4_style").addClass("text-white")
            $("#page_4_top_text").addClass("font-weight-bold")
            $("#page_4_top_text").addClass("text-success")
            $("#page_4_top_text").html("Accepted! The Requestor will be notified and access will be automatically granted shortly. You may leave this page.")
            $("#manager_submit").attr("disabled", "disabled")
            $("#manager_reject").attr("disabled", "disabled")
        },

    });
}

function reject() {
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
            $(".page_4_style").addClass("bg-danger")
            $(".page_4_style").addClass("text-white")
            $("#page_4_top_text").addClass("font-weight-bold")
            $("#page_4_top_text").addClass("text-danger")
            $("#page_4_top_text").html("Rejected! The Requestor will be notified shortly. You may leave this page.")
            $("#manager_submit").attr("disabled", "disabled")
            $("#manager_reject").attr("disabled", "disabled")
        },
    });
}