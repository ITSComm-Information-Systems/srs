$(document).ready(function() {

  var x, i;
  //x = $('input:not(:checkbox)');
  x = $("input:not([type=radio], [type=checkbox])");
  for (i = 0; i < x.length; i++) {
      x[i].className += " form-control";
  }

  $('#pills-step1').removeClass('disabled');  // Enable first pill, that is how it all starts.

  currStep = 1;
  lastStep = document.getElementsByClassName("tab-pane").length;


  if ( $("h1").html() === 'TestWorkflows' ) {
    for (i = 1; i < lastStep+1; i++) {
      $('#pills-step'+ i).removeClass('disabled'); 
    }
  }

  $('#pills-tab li:first-child a').tab('show'); // Select first tab


  $("#buildingFields").hide();
  $("#phLocationFields").hide();
  $("#buildingTable").hide();
  $("#Conduit").hide();
  $("#PurchasePhone").hide();
  $("#ModelInfo").hide();
  $("#PhoneSetType").hide();
  $("#JackNumber").hide();
  $("#PhoneModelNum").hide();
  $("#voipPhoneMac").hide();
  
  
  $("#ModelInfo_basic").click(function() {
    $("#PhoneModelNum").show();
    $("#voipPhoneMac").hide();
  });

  $("#ModelInfo_advanced").click(function() {
    $("#PhoneModelNum").show();
    $("#voipPhoneMac").hide();
  });

  $("#ModelInfo_voip").click(function() {
    $("#PhoneModelNum").show();
    $("#voipPhoneMac").show();
  });


  $("#activePhone_Y").click(function() {
    $('[data-tab="LocationNew"]').hide();
  });

  $("#activePhone_N").click(function() {
    $('[data-tab="LocationNew"]').show();
  });
  


  //Data
  $("#activePhone").hide();
  $("#jackNumber").hide();
  $("#conduit").hide();
  $("#linesToInstall").hide();

  $("#jack_Y").click(function() {
    $("#activePhone").show();
    $("#conduit").hide();
  });

  $("#jack_N").click(function() {
    $("#conduit").show();
    $("#activePhone").hide();
    $("#jackNumber").hide();
  });

  $("#jackNumber").keypress(function() {
    $("#activePhone").show();
  });

  $("#activePhone_Y").click(function() {
    $("#linesToInstall").show();
  });

  $("#activePhone_N").click(function() {
    $("#linesToInstall").show();
    //$('#pills-step2').hide();  //.addClass(' hidden');
  });

  $("#conduit_Y").click(function() {
    $("#linesToInstall").show();
  });

  $("#conduit_N").click(function() {
    $("#linesToInstall").show();
  });

  // Addl info
  $('#contact_id').hide();
  $('#contact_name').hide();
  $('#contact_number').hide();

  // data based radio actions
  $('input[type=radio]').click(function(){

    if(this.value=='basic'){
      $('[data-phoneset="advanced"]').hide();
      $('[data-phoneset="basic"]').show();
      $('[data-phoneset="voip"]').hide();
    }
    if(this.value=='advanced'){
      $('[data-phoneset="advanced"]').show();
      $('[data-phoneset="basic"]').hide();
      $('[data-phoneset="voip"]').hide();
    }
    if(this.value=='voip'){
      $('[data-phoneset="advanced"]').hide();
      $('[data-phoneset="basic"]').hide();
      $('[data-phoneset="voip"]').show();
    }

    if (this.value=='buy'){
      $('[data-tab="Equipment"]').show();
    }

    if (this.value=='nobuy'){
      $('[data-tab="Equipment"]').hide();
    }

    if(this.name=='analogIPFax' || this.name=='analogIPpci'){
      if(this.value=='basic') { // Analog
        $('[data-tab="IPFaxInfo"]').hide();
        $('[data-tab="2Chartfields"]').hide();
        $('[data-tab="LocationNew"]').show();
        $('[data-tab="Restrictions"]').show();
        $('[data-tab="4Chartfields"]').show();
      }
      if(this.value=='voip'){
        $('[data-tab="IPFaxInfo"]').show();
        $('[data-tab="2Chartfields"]').show();
        $('[data-tab="LocationNew"]').hide();
        $('[data-tab="Restrictions"]').hide();
        $('[data-tab="4Chartfields"]').hide();
      }
    }

  });

  

  // Phone Type Tab
  $("#Jack_Y").click(function() {
    $("#JackNumber").show();
    $("#JackNumber_review").show();
    $("#Conduit").hide();
    $("#Conduit_review").hide();
  });

  $("#Jack_N").click(function() {
    $("#JackNumber").hide();
    $("#JackNumber_review").hide();
    $("#Conduit").show();
    $("#Conduit_review").show();
  });

  $("#JackNumber").keypress(function() {
    $("#PurchasePhone").show();
    $("#PurchasePhone_review").show();
  });

  $("#Conduit_Y").click(function() {
    $("#PurchasePhone").show();
    $("#PurchasePhone_review").show();
  });

  $("#Conduit_N").click(function() {
    $("#PurchasePhone").show();
    $("#PurchasePhone_review").show();
  });

  $("#PurchasePhone_buy").click(function() {
    $("#PhoneSetType").show();
    $("#PhoneSetType_review").show();
    $("#ModelInfo").hide();
    $("#ModelInfo_review").hide();
    $("#PhoneModelNum").hide();
    $("#PhoneModelNum_review").hide();
    //$('#pills-step3').show();  //removeClass(' hidden');
  });

  $("#PurchasePhone_nobuy").click(function() {
    $("#ModelInfo").show();
    $("#ModelInfo_review").show();
    $("#PhoneSetType").hide();
    $("#PhoneSetType_review").hide();
    //$('#pills-step3').hide();  //addClass(' hidden');
  });


  $("#purchasePhone_buy").click(function() {
    $("#PhoneSetType").show();
    $("#PhoneSetType_review").show();
    $("#ModelInfo").hide();
    $("#ModelInfo_review").hide();
    $("#PhoneModelNum").hide();
    $("#PhoneModelNum_review").hide();
    //$('#pills-step4').hide();  //.removeClass(' hidden');
  });

  $("#purchasePhone_nobuy").click(function() {
    $("#ModelInfo").show();
    $("#ModelInfo_review").show();
    $("#PhoneSetType").hide();
    $("#PhoneSetType_review").hide();
    //$('#pills-step4').hide();  //.addClass(' hidden');
  });


  $("#phone_type").click(function() {
    if ($('#phone_type option:selected') > 1) {
      $('#nextBtn').prop('disabled', false);
    }
  });

  $("#nextBtn").click(function(event) {
    nextPrev(1);
  });

  $("#prevBtn").click(function(event) {
    nextPrev(-1);
  });

  $("#contact_yn_False").click(function(event) {
    $('#contact_id').show();
    $('#contact_name').show();
    $('#contact_number').show();
    $('#contact_id_review').show();
    $('#contact_name_review').show();
    $('#contact_number_review').show();
  });

  $("#contact_yn_True").click(function(event) {
    $('#contact_id').hide();
    $('#contact_name').hide();
    $('#contact_number').hide();
    $('#contact_id_review').hide();
    $('#contact_name_review').hide();
    $('#contact_number_review').hide();
  });

  $("#buildingFields").hide();
  $("#buildingTable").hide();

  $("#buildingSearch").on("keyup", function() {
      $("#buildingTable").show();
      var value = $(this).val().toLowerCase();
      $("#buildingTable tr").filter(function() {
      $(this).toggle($(this).text().toLowerCase().indexOf(value) > -1)
      });
  });

  $('#buildingTable tr').click(function() {
      var building = $(this).find("td").eq(1).html();   
      var buildingCode = $(this).find("td").eq(0).html();   
      $('#id_new_building_name').val(building);
      $('#id_new_building_code').val(buildingCode);
      $("#buildingTable").hide();
      $("#buildingFields").show();
  });


});

// Workflow stuff
$('a[data-toggle="tab"]').on('shown.bs.tab', function(e) {
  currStep = $(this)[0].id.substring(10, 12) * 1;
  if (currStep == lastStep) {
      $('#nextBtn').html('Add to Cart');
  } else {
      $('#nextBtn').html('Next');
  }
  if (currStep == 1) {
    $('#prevBtn').hide();
  } else {
    $('#prevBtn').show();
  }
  //$('#nextBtn').prop('disabled', false);
})


function nextPrev(n) {

  if (n == 1 && !validateForm()) return false;

  currStep = currStep + n;

  //while ( $('#pills-step'+currStep).hasClass('hidden')) {
  while ( $('#pills-step'+currStep).is(':hidden')) {
    currStep = currStep + n;
  }

  $('#pills-step'+currStep).removeClass('disabled');
  $('#pills-tab li:nth-child(' + currStep + ') a').tab('show');
  if (currStep > lastStep) {
      $('#workflowForm').submit();
      return false;
  }
}


function validateForm() {

  inp = $("#step" + currStep + " :input:visible");
  valid = true;
  for (i = 0; i < inp.length; i++) {
    id = "#" + $(inp[i]).attr('id') + "_review";
    selected_text = $( "#" + inp[i].id + " option:selected" ).text()

    if (selected_text) {
      $(id).html(selected_text);
      console.log(id + "-" + selected_text + "<");
    } else {
      text_box = $("#" + inp[i].id ).val();
      $(id).html( text_box );
      console.log(id + ":" + text_box);
    }

    if (!inp[i].checkValidity()) {
      inp[i].className += " invalid";
      valid = false;
    }
  }

    $("input[type='radio']:checked").each(function() { // Update review form with radio data
        var idVal = $(this).attr("id");
        id = "#id_" + $(this).attr("name") + "_review";
        $(id).html($("label[for='"+idVal+"']").text());
    });
  
  if (valid) {
    document.getElementsByClassName("tab-pane")[currStep-1].className += " finish";
    $("#workflowForm").removeClass('was-validated');
  } else {
    $("#workflowForm").addClass('was-validated');
  }
  return valid; // return the valid status
}

  function filterChartcom(obj) { 
    id = '#id_' + obj.dataset.target;
    if (obj.value=='all') {
      $(id).find('[data-dept]').show();
    } else {
      $(id).find('[data-dept]').hide();
      $(id).find("[data-dept='" + obj.value + "']").show();
    }

  }

  $("#phoneLookup").click(function () {
    var phone_number = $("#id_phone_number").val();
    phone_number = phone_number.replace(/\D/g,'');

    $("#phLocationFields").show();
    $("#phBuildingID").val('');
    $("#id_building").val('');
    $("#id_floor").val('');
    $("#id_room").val('');
    $("#id_jack").val('');


    $.ajax({
      url: '/orders/ajax/get_phone_location/' + phone_number,
      //dataType: 'json',

      beforeSend: function(){
        $("#phLocationFields").hide();
        $('#phoneLookup').html('Searching...').addClass(' disabled');
        $("#buildingCode").html('');
        $("#building").html('');
        $("#floor").html('');
        $("#room").html('');
        $("#jack").html('');
      },

      success: function (data) {
        if (data.code !== '') {
          $("#buildingCode").html(data.code);
          $("#building").html(data.name);
          $("#floor").html(data.floor);
          $("#room").html(data.room);
          $("#jack").html(data.jack);

          $("#id_buildingCode_review").html(data.code);
          $("#id_building_review").html(data.name);
          $("#id_floor_review").html(data.floor);
          $("#id_room_review").html(data.room);
          $("#id_jack_review").html(data.jack);

          console.log('good:' + data.code)
          $("#id_phone_number").addClass('is-valid');
          $("#id_phone_number").removeClass('invalid');
          $("#workflowForm").removeClass('was-validated');
          $("#phLocationFields").show();
        } else {
          alert("No phone found.");
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
