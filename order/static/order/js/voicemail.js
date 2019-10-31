var locations = [];

$(document).ready(function() {

    $("#id_phone_number").focusout(function () {
      phone_number = $("#id_phone_number").val();

      $.ajax({
        url: '/orders/ajax/get_phone_location/' + phone_number,
  
        beforeSend: function(){
          $("#phLocationFields").hide();
          $('#phoneLookup').html('Searching...').addClass(' disabled');
        },
  
        success: function (data) {
          console.log('suc');
          if(data[0]) {
            locations = data;
            auth = data[0]['authorized'];
            dept = data[0]['dept'];
            //console.log(auth);
            if (auth) {
              document.getElementById("id_phone_number").setCustomValidity("");
              document.getElementById("id_phone_number").checkValidity();
              $("#id_phone_number").removeClass('is-invalid');
              $("#workflowForm").removeClass('was-validated');
            } else {
              console.log('not authorized');
              document.getElementById("id_phone_number").setCustomValidity("Not authorized");
              //document.getElementById("id_phone_number").checkValidity();
              $("#error_msg").html('You are not authorized for that number');
              $("#workflowForm").addClass('was-validated');
            }

          } else {
            console.log('nodata');
            $("#workflowForm").addClass('was-validated');
            $("#error_msg").html('Number Not Found')
            document.getElementById("id_phone_number").setCustomValidity("Not Found.");
          }
        },
  
        error: function(){
          console.log('error');
          document.getElementById("id_phone_number").setCustomValidity("Not Found.");
          $("#id_phone_number").addClass('is-invalid');
          $("#id_phone_number").removeClass('is-valid');
          $("#workflowForm").addClass('was-validated');
        },
  
        complete: function(){
          $('#phoneLookup').html('Find').removeClass(' disabled');
          console.log('end');
        }
  
      })

    });

});
