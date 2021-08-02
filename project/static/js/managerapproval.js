$(document).ready(function() {
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
});