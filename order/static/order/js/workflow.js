$(document).ready(function() {

  var x, i;
  x = $('input:not(:checkbox)');
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
    $('#pills-step2').hide();  //.addClass(' hidden');
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


  //$("#analogIPpci_A").click(function() {
  //  $('#pills-step4').addClass(' hidden');
  
 //   $('#pills-step2').removeClass(' hidden');
 //   $('#pills-step3').removeClass(' hidden');
 //   $('#pills-step5').removeClass(' hidden');

 //   basicPhone()
 // });

  //$("#analogIPpci_IP").click(function() {
  //  $('#pills-step4').removeClass(' hidden');
  
  //  $('#pills-step2').addClass(' hidden');
  //  $('#pills-step3').addClass(' hidden');
  //  $('#pills-step5').addClass(' hidden');

  //  voipPhone();
  //});


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

    console.log(this.name);

  });

  //$("#analogIPFax_A").click(function() {
    //$('#pills-step4').addClass(' hidden'); // IPFaxInfo
    //$('#pills-step5').addClass(' hidden'); // 2Chartfields
  
    //$('#pills-step2').removeClass(' hidden');  //LocationNew
    //$('#pills-step3').removeClass(' hidden');  //Restrictions
    //$('#pills-step6').removeClass(' hidden'); //4Chartfields
    //$('[data-phoneset="advanced"]').show();
    //$('[data-phoneset="basic"]').hide();
    //$('[data-phoneset="voip"]').hide();
    //basicPhone()
  //});

  //$("#analogIPFax_IP").click(function() {
    //$('#pills-step4').removeClass(' hidden'); // IPFaxInfo
    //$('#pills-step5').removeClass(' hidden'); // 2Chartfields

    //$('#pills-step2').addClass(' hidden'); //LocationNew
    //$('#pills-step3').addClass(' hidden'); //Restrictions
    //$('#pills-step6').addClass(' hidden'); //4Chartfields

    //voipPhone();
  //});


  //Phone
  //$("#phoneSetType_B").click(function() {
  //  basicPhone();
  //  $("#equip2").hide();
  //  $("#equip1").show();
  //});

  //$("#phoneSetType_A").click(function() {
  //  advancedPhone();
  //});

  //$("#phoneSetType_V").click(function() {
  //  voipPhone();
  //  $("#equip1").hide();
  //  $("#equip2").show();
  //});

  //Phone
  //$("#PhoneSetType_B").click(function() {
  //  basicPhone();
  //  $("#equip2").hide();
  //  $("#equip1").show();
  //});

  //$("#PhoneSetType_A").click(function() {
  //  advancedPhone();
  //});

  //$("#PhoneSetType_V").click(function() {
  //  voipPhone();
  //  $("#equip1").hide();
  //  $("#equip2").show();
  //});

  //$("#ModelInfo_V").click(function() {
  //  voipPhone();
  //  $("#PhoneModelNum").show();
  //});
  
  //$("#ModelInfo_A").click(function() {
  //  advancedPhone();
  //  $("#PhoneModelNum").show();
  //});

  //$("#ModelInfo_B").click(function() {
  //  basicPhone();
  //  $("#PhoneModelNum").show();
  //});

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
  });

  $("#contact_yn_True").click(function(event) {
    $('#contact_id').hide();
    $('#contact_name').hide();
    $('#contact_number').hide();
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
  $('#nextBtn').prop('disabled', false);
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
    } else {
      text_box = $("#" + inp[i].id ).val();
      console.log(id + '<>' + text_box);
      $(id).html( text_box );
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



  function filterChartcom(id, value) {
    console.log('usa:' + value);
    //$("#edit-field-service-sub-cat-value option[value=" + title + "]").hide();
    //$(id).toggle($(this).text().toLowerCase().indexOf(value) > -1)
    //$('.city').find('option:contains('Aurangabad)').hide();
    //$(#id_oneTimeCharges).find([data-dept='481060']).hide();
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
      //data: {
      //  'phone_number': '7347642793'
      //},
      dataType: 'json',
      success: function (data) {

        //alert(" phone found.");
        if (data.code) {
          $("#phLocationFields").show();
          $("#phBuildingID").val(data.code);
          $("#id_building").val(data.name);
          $("#id_floor").val(data.floor);
          $("#id_room").val(data.room);
          $("#id_jack").val(data.jack);
        } else {
          alert("No phone found.");
        }
      }
    });

  });
