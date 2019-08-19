$(document).ready(function() {

  // Workflow stuff
  $('a[data-toggle="tab"]').on('shown.bs.tab', function(event) {
    currStep = $(this)[0].id.substring(10, 12) * 1;
    if (currStep == lastStep) {
        $('#nextBtn').html('Add to Cart');
        fillReviewForm();
    } else {
        $('#nextBtn').html('Next');
    }
    if (currStep == 1) {
      $('#prevBtn').hide();
    } else {
      $('#prevBtn').show();
    }

    if (currStep > maxStep) {
      maxStep = currStep;
      // Progressive Disclosure Fields
      preFields = $('#step' + currStep).find('[data-sequence]').hide();
      $(preFields[0]).show();
      curr = 0;
      pointer = 0;
      vals = []
    }




  })


  var x, i;
  //x = $('input:not(:checkbox)');
  x = $("input:not([type=radio], [type=checkbox])");
  for (i = 0; i < x.length; i++) {
      x[i].className += " form-control";
  }

  $('#pills-step1').removeClass('disabled');  // Enable first pill, that is how it all starts.

  currStep = 1;
  maxStep = 0;
  lastStep = document.getElementsByClassName("tab-pane").length;
  var tabs = new Array(lastStep);


  if ( $("#wfid").val() == 32 ) { // Test Workflow option
    for (i = 1; i < lastStep+1; i++) {
      $('#pills-step'+ i).removeClass('disabled'); 
    }
  }

  $('#pills-tab li:first-child a').tab('show'); // Select first tab



  var callback = function() {
    if (preFields.index(this) <= pointer) { // User changed a previous answer.
      for (i = preFields.index(this)+1; i < preFields.length; i++) {
        $(preFields[i]).hide();
        $(preFields[i]).find('input:checked').prop("checked", false);
        // todo clear value if input
      }
    }

    pointer = preFields.index(this);
    val = $('input:checked', this).val()
    vals[pointer] = val;

    for (question = 0; question < preFields.length; question++) {
      curr = preFields[question].dataset.sequence;
      cond = preFields[question].dataset.condition;
      if (cond) {
          arr = cond.split(',')
          for (i = 0; i < arr.length; i++) {
            if(!vals.includes(arr[i])) {
              cond = false;
              break;
            }
          }
      } else{
        cond = true; // Pass if no condition
      }

      if (cond) {
        if (curr > this.dataset.sequence) {
          $(preFields[question]).show();
          break;
        }
      }
    }
  
  };

  $(preFields).change(callback);
  $(preFields).keypress(callback);

  $("#activePhone_Y").click(function() {
    $('[data-tab="LocationNew"]').hide();
  });

  $("#activePhone_N").click(function() {
    $('[data-tab="LocationNew"]').show();
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
    $('#comments').show();
    $('#file').show();
    
    
  });

  $("#contact_yn_True").click(function(event) {
    $('#contact_id').hide();
    $('#contact_name').hide();
    $('#contact_number').hide();
    $('#comments').show();
    $('#file').show();
  });


  function saveReviewData(inp) {

    var tab = [];
  
    for (i = 0; i < inp.length; i++) {
      var obj = inp[i];
      var type = $(obj).attr('type')
      var id = $(obj).attr("id");
      var name = $(obj).attr("name");
  
      if(type=="radio") {
        if (obj.checked == true) {
          label = $("#legend" + name).text();
          value = $("label[for='" + id + "']").text();
          tab.push({'label': label, 'value': value})
        }
      } else if (type=="checkbox") {
        if (obj.checked == true) {
          //label = $("#legend" + name).text();
          value = $("label[for='" + id + "']").text();
          tab.push({'label': '', 'value': value})
        }
      } else if (type=="text" || type=="number" || obj.tagName=="TEXTAREA") {
        label = $("label[for='" + id + "']").text();
        value = $("#" + inp[i].id).val();
        tab.push({'label': label, 'value': value})
      } else if (obj.tagName=="SELECT") {
        if(name) { // Don't process data we are not saving
        label = $("label[for='" + id + "']").text();
        value = $( "#" + id + " option:selected" ).text();
        tab.push({'label': label, 'value': value})
        }
      } else {
        console.log('unknown type:' + type);
      }
    }
  
    tabs[currStep] = tab;
  }

  function validateForm() {

    inp = $("#step" + currStep + " :input:visible");
    valid = true;
    for (i = 0; i < inp.length; i++) {
      if (!inp[i].checkValidity()) {
        inp[i].className += " invalid";
        valid = false;
      }
    }
    
    if (valid) {
      document.getElementsByClassName("tab-pane")[currStep-1].className += " finish";
      $("#workflowForm").removeClass('was-validated');
      saveReviewData(inp);
    } else {
      $("#workflowForm").addClass('was-validated');
    }
    return valid; // return the valid status
  }


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

  function fillReviewForm() {

    var summary = '';
    for (tab = 1; tab < lastStep; tab++) {  
      $('#reviewstep' + tab).text('');
      if(tabs[tab]) {
         heading = $('#reviewstep' + tab).data('label')
         summary = summary + heading.toUpperCase() + '\n';
        for (field = 0; field < tabs[tab].length; field++) {
          txt = '<b>' + tabs[tab][field].label + '</b>  ' + tabs[tab][field].value + '<br>';
          summary = summary + tabs[tab][field].label + ' - ' + tabs[tab][field].value + '\n';
          $('#reviewstep' + tab).append(txt);
        }
      }
      summary = summary + '\n';
    }
    $('#reviewSummary').val(summary);
    console.log(summary);
  }


});  // Document Ready








  function filterChartcom(obj) { 
    id = '#id_' + obj.dataset.target;
    if (obj.value=='all') {
      $(id).find('[data-dept]').show();
    } else {
      $(id).find('[data-dept]').hide();
      $(id).find("[data-dept='" + obj.value + "']").show();
    }

  }

  
