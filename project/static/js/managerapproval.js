function accept(){
	$(".page_4_style").addClass("bg-success")
	$(".page_4_style").addClass("text-white")
	$("#page_4_top_text").addClass("font-weight-bold")
	$("#page_4_top_text").addClass("text-success")
	$("#page_4_top_text").html("Accepted! The Requestor will be notified and access will be automatically granted shortly. You may leave this page.")
	$("#manager_submit").attr("disabled", "disabled")
	$("#manager_reject").attr("disabled", "disabled")
    $.ajax({
        url: '/managerapprovalsubmit/',
        data: {
            'id': params["id"]
        },
        dataType:'json',
        
        success: function(data) {
            console.log(data)
            $("#manager_submit").removeAttr("disabled")
	        $("#manager_reject").removeAttr("disabled")
            for (user of data){
                review_table.row.add([
                    user.user_defined_id,
                    user.building,
                    user.mrc_account_number,
                    user.toll_account_number,
                    user.local_account_number,
                ]).draw();
                for (key in user){
                    $("#" + key).html(user[key])
                }
            }
            
        }
    });
}


function reject(){
	$(".page_4_style").addClass("bg-danger")
	$(".page_4_style").addClass("text-white")
	$("#page_4_top_text").addClass("font-weight-bold")
	$("#page_4_top_text").addClass("text-danger")
	$("#page_4_top_text").html("Rejected! The Requestor will be notified shortly. You may leave this page.")
	$("#manager_submit").attr("disabled", "disabled")
	$("#manager_reject").attr("disabled", "disabled")
}


$(document).ready(function() {
    $("#manager_submit").attr("disabled", "disabled")
	$("#manager_reject").attr("disabled", "disabled")
    // get url parameters
    params={};location.search.replace(/[?&]+([^=&]+)=([^&]*)/gi,function(s,k,v){params[k]=v})

    var review_table =  $('#review_table').DataTable({
		"destroy": true,
		"lengthChange": false,
		"bFilter": false,
		"dom": 'rtp',
		"ordering":false
	});

    $.ajax({
        url: '/managerapprovalinit/',
        data: {
            'id': params["id"]
        },
        dataType:'json',
        
        success: function(data) {
            console.log(data)
            $("#manager_submit").removeAttr("disabled")
	        $("#manager_reject").removeAttr("disabled")
            for (user of data){
                review_table.row.add([
                    user.user_defined_id,
                    user.building,
                    user.mrc_account_number,
                    user.toll_account_number,
                    user.local_account_number,
                ]).draw();
                for (key in user){
                    $("#" + key).html(user[key])
                }
            }
            
        }
    });
    $("#confirmAccept").on("click", function(){
        accept();
    });
    $("#confirmReject").on("click", function(){
        reject();
    });
});