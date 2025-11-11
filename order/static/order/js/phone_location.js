var locations = [];

$(document).ready(function() {

    $("#newLocationFields").hide();    
    $("#phLocationFields").hide();

    $("#phoneLookup").click(function () {
        var phone_number = $("#id_phone_number").val();
        //phone_number = phone_number.replace(/\D/g,'');
        phone_number=  phone_number.replace(/[&\/\\#,+()$~%.'":*?<>{}]/g, '');
        phone_number = phone_number.replace(/\s+/g, '');
        //console.log("phone_number")
        //console.log(phone_number)
    
        $("#phLocationFields").show();
        $("#phBuildingID").val('');
        $("#id_building").val('');
        $("#id_floor").val('');
        $("#id_room").val('');
        $("#id_jack").val('');
    
        $.ajax({
          url: '/orders/ajax/get_phone_location/' + phone_number,
    
          beforeSend: function(){
            $("#phLocationFields").hide();
            $('#phoneLookup').html('Searching...').addClass(' disabled');
          },
    
          success: function (data) {
            locations = data;

            $("#cardDeck .generated-card").remove();
            if (data.length < 1) { // Validation
                $("#id_phone_number").addClass('is-invalid').removeClass('is-valid');
                $("#id_phone_number").siblings(".invalid-feedback").html(
                    '<i class="fas fa-exclamation-triangle"></i>Number not found.'
                );
              document.getElementById("id_phone_number").setCustomValidity("Not found");
              $("#workflowForm").addClass('was-validated');
            } else if (data[0]['authorized'] === false) {
                $("#id_phone_number").addClass('is-invalid').removeClass('is-valid');
                $("#id_phone_number").siblings(".invalid-feedback").html(
                    '<i class="fas fa-exclamation-triangle"></i> Not Authorized for number.'
                );
                document.getElementById("id_phone_number").setCustomValidity("Not authorized");
                //$("#workflowForm").addClass('was-validated');
                //$('#phoneLookup').html('Find').removeClass(' disabled');

            } else {
              document.getElementById("id_phone_number").setCustomValidity("");
              document.getElementById("id_phone_number").checkValidity();
              $("#id_phone_number").removeClass('is-invalid');
              $("#workflowForm").removeClass('was-validated');

            for (loc = 0; loc < data.length; loc++) {
                var newCard = $("#mainCard").clone();
                $(newCard).attr('id',loc).addClass("generated-card");
                $(newCard).show();
                $(newCard).find("#name").text(data[loc]['building_name']);
                $(newCard).find("#code").text(data[loc]['building_code']);
                $(newCard).find("#floor").text(data[loc]['floor_name']);
                $(newCard).find("#room").text(data[loc]['room_name']);
                $(newCard).find("#jack").text(data[loc]['jack_name']);
                $(newCard).find(".card-body").data('location', loc);
                $("#cardDeck").prepend(newCard);
                $("#foundPhone").text(phone_number);
                $("#phLocationFields").show();
            }
            }
          },
    
          error: function(){
            $("#id_phone_number").addClass('is-invalid');
            $("#id_phone_number").removeClass('is-valid');
            $("#workflowForm").addClass('was-validated');
          },
    
          complete: function(){
            $('#phoneLookup').html('Find').removeClass(' disabled');
          }
    
        })
      });

});



function selectCard(card) {
    $('#div_suspend_restore').show();

    if (card.id == 'updateLocation') {
        $("#newLocationFields").show();
        current_number = $("#foundPhone").html()
        $("#service_number").val(current_number);
    } else {
        $("#newLocationFields").hide();
        div = $(card).parent();
        $("#newBuildingName").val(div.find('#name').html());
        $("#newBuildingCode").val(div.find('#code').html());
        $("#newBuildingFloor").val(div.find('#floor').html());
        $("#newBuildingRoom").val(div.find('#room').html());
        $("#newBuildingJack").val(div.find('#jack').html());
    
        loc = div.find('#name').html() + "\n" 
        + "Building ID: " + div.find('#code').html() + "\n" 
        + "Floor: " + div.find('#floor').html() + "\n" 
        + "Room: " + div.find('#room').html() + "\n" 
        + "Jack: " + div.find('#jack').html() + "\n";
        $(card).val(loc);

        //sel = $(div).data('location');
        selectedLocation = locations[$(div).data('location')];

        $("#subscriber_id").val(selectedLocation.subscriber_id);
        $("#service_number").val(selectedLocation.service_number);
        $("#location_id").val(selectedLocation.location_id);
        $("#service_type").val(selectedLocation.service_type);


    }



    $(".current-button").text("Select");
    $(card).addClass('btn-outline-success')
    $('.location-card').removeClass('selected-card').val('Select')
    $(card).closest('.location-card').addClass('selected-card').val('Selected')

    $("button").removeClass('selected');
    $(card).addClass('selected');
    $(card).text("Selected");

    $(".location-card").removeClass("card-not-selected")
    $("#mustchoose").hide();


}
