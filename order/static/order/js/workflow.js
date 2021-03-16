var popOverSettings = {
  placement: 'bottom',
  container: 'body',
  html: true,
  trigger: 'hover',
  selector: '[data-toggle="popover"]', //Sepcify the selector here
  content: function () {
      return $('#popover-content').html();
  }
}


$(document).ready(function() {

  $('#productType_1').attr('disabled', true);


  $(document).on("click", "a.remove" , function() {
    $(this).parent().remove();
  });

  $('body').popover(popOverSettings);
  //$('[data-toggle="popover"]').popover();

  use_cart = $("#wfcart").val();
  use_ajax = $("#wfajax").val();
  var wfid = parseInt($("#wfid").val());
  const reviewPages = [50,56,61,63,66,72,73]
  const modifyPages = [47,49,53,55,59,60,62,65,70,71]

  item_id = 0;
  // Workflow stuff
  $('a[data-toggle="tab"]').on('shown.bs.tab', function(event) {

    //console.log(this.dataset.tab);
    currTab = this.dataset.tab;

    currStep = $(this)[0].id.substring(10, 12) * 1;
    if (currStep == lastStep) {
      if (use_cart=="True") {
        $('#nextBtn').html('Add to Cart');
        fillReviewForm();
      } else {
        $('#nextBtn').html('Submit Now');
      }
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

  if (reviewPages.includes(wfid)) {
    $('#pills-step1').hide();
    $('p').hide();
    $('h2').hide();
    $('#nextBtn').hide();
  }

  if (modifyPages.includes(wfid)) {
    $('#nextBtn').hide();
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


  (function ($) {
	  $.each(['show', 'hide'], function (i, ev) {
	    var el = $.fn[ev];
	    $.fn[ev] = function () {
	      this.trigger(ev);
	      return el.apply(this, arguments);
	    };
	  });
  })(jQuery);
  
  $('.dynlabel').on('show', function() {
    $(this).keypress();
  });

  // Hide phone location if no active phone line
  if ($("#activePhone").length) {
    $('[data-tab="PhoneLocation"]').hide();
  }

  $("#AdminUnique").click(function() {
    $('#PhoneNumber').show();
    $('#GroupEmailAdd').show();
  });

  $("#jack_nojack").click(function() {
    $('[data-tab="PhoneLocation"]').hide();
    $('[data-tab="LocationNew"]').show();
  });

  $("#activePhone_yesactivephone").click(function() {
    $('[data-tab="PhoneLocation"]').show();
    $('[data-tab="LocationNew"]').hide();
  });

  $("#activePhone_noactivephone").click(function() {
    $('[data-tab="PhoneLocation"]').hide();
    $('[data-tab="LocationNew"]').show();
  });
  
  $("#ExistingPhone_nophone").click(function() {
    $('[data-tab="PhoneLocation"]').hide();
    $('[data-tab="LocationNew"]').show();
    $('[data-tab="SelectFeatures"]').show();
    $('[data-tab="Restrictions"]').show();
    
    $('[data-phoneset="advanced"]').hide();
    $('[data-phoneset="basic"]').hide();
    $('[data-phoneset="voip"]').show();

  });

  $("#ExistingPhone_yesphone").click(function() {
    $('[data-tab="PhoneLocation"]').show();
    $('[data-tab="LocationNew"]').hide();
    $('[data-tab="SelectFeatures"]').hide();
    $('[data-tab="Restrictions"]').hide();
    
    $('[data-phoneset="advanced"]').hide();
    $('[data-phoneset="basic"]').hide();
    $('[data-phoneset="voip"]').show();

  });

  $(document).on("click", "#multi_protocol_0" , function() {
    $('#div_ad_group').show();
  });

  $(document).on("click", "#multi_protocol_1" , function() {
    $('#div_ad_group').hide().prop('required',false);
  });

  $(document).on("load", "#div_ad_group" , function() {
    $('#div_ad_group').hide();
  });



  // miSevBasic
  $('[data-tab="miSevBasic"]').on('shown.bs.tab', function(event) {
    $("#div_misevexissev").trigger("change");
  });

  $(document).on("change", "#div_misevexissev" , function() {
    if ($('#misevexissev_1').prop("checked")) {  // Yes contact me to migrat
      $('#div_mcommserveradmin').hide().prop('required',false);
      $('#div_owner').hide().prop('required',false);
    } else if ($('#misevexissev_0').prop("checked")) {  // Nah, new server
      $('#div_mcommserveradmin').show().prop('required',true);
      $('#div_owner').show().prop('required',true);
    } else {
      $('#div_mcommserveradmin').hide().prop('required',false);
      $('#div_owner').hide().prop('required',false);
    }
  });




  // MiDatabase Type
  $('[data-tab="midbtype"]').on('show.bs.tab', function(event) {

    $("#id_midatatype").trigger("change");
    server = $('#id_midatasize').data('server');

    if (server) {
      $('#id_midatasize').data('server', '');
      type = $('#id_midatatype').val();
      version = $('#id_dbversion').val();
      size=$('#id_midatasize').val();
      console.log('type', type, version, size);
      //onclick="location.href='67?database=55';"
      link = "location.href='67?type=" + type + "&version=" + version + "&size=" + size +"';"; 
      $('#go_button').attr('onclick', link)
      $("#order_server").modal('show');
    }
  });

  $(document).on("change", "[data-pane='midbtype']" , function() {
    set_dedicated_server();
  });

  function set_dedicated_server() {
    dedicated = false;

    if ($('#id_midatasize').val() > 50) {
      console.log('size over fidy');
      dedicated = true;
    }

    if ($('#id_midatatype').val() == "66") {  // MS SQL
      if ($('#midatasql_0').prop("checked")) {  // SQL Agent Jobs
        console.log('sql jobs')
        dedicated = true;
      }
      if ($('#id_dbversion option:selected').text().indexOf('SSAS') > 0) {  // SSAS
        console.log('Sassy')
        dedicated = true;
      }
    }

    if ($('#sensitiveData_0').prop("checked")) {  // Sensitive Data
      console.log('data too sensitive')
      dedicated = true;
    }

    if (dedicated) {
      $('#div_shared').prop('readonly', true);
      $('#shared_1').prop("checked", true);
    } else {
      $('#div_shared').prop('readonly', false);
      //$('#shared_1').prop("checked", true);
    }

    return dedicated;

  }

  $(document).on("change", "#id_midatatype" , function() {
    if (this.value=="66") { // MSSQL
      $("#div_dbversion").show();
      $("#div_midatasql").show();
    } else {
      $("#div_dbversion").hide();
      $("#div_midatasql").hide();
    }
  });


  //MiServer Specification
  $('[data-tab="miSeverSpec"]').on('show.bs.tab', function(event) {
    ram_rate = $('#server_rates').data('ram_rate');
    disk_replicated = $('#server_rates').data('disk_replicated');
    disk_no_replication = $('#server_rates').data('disk_no_replication');
    disk_backup = $('#server_rates').data('disk_backup');

    $("#div_managed").trigger("change");
    $("#div_misevprefix").trigger("change");
    $("#id_cpu").trigger("change");
    $("#id_misevos").trigger("change");
    update_total_cost();
  });

  $(document).on("change", ".cost-driver" , function() {
    update_total_cost();
  });

  function update_total_cost() {

    ram = $('#id_ram').val();
    ram_cost = ram * ram_rate;
    $('#ram_cost').html('$' + ram_cost.toFixed(2));

    if ($('#id_cpu').data('server')){
      disk_0 = $('.disk-size')[1];

      if (ram < 8) {
        paging_disk = 60;
      } else {
        paging_disk = Math.ceil((ram-8)/4) * 10 + 60;
      }

      $(disk_0).val(paging_disk);
    }

    if ($('#replicated_0').prop("checked")) {  // Replicated
      disk_rate = disk_replicated;
    } else {
      disk_rate = disk_no_replication; // Default until selected
    }

    total_disk_size = 0;
    total_disk_cost = 0;

    $( ".disk-div" ).each(function( index ) {  // Tally all disks

      uom = $(this).find("select").val();
      size = $(this).find(".disk-size").val();

      if (uom=="TB") {
        size = size * 1024;
      } else {
        size = size * 1;

      }
      cost = size * disk_rate

      $(this).find("span").html('$' + cost.toFixed(2));
      total_disk_size = total_disk_size + size
      total_disk_cost = total_disk_cost + cost

    });
    
    if ($('#backup_0').prop("checked")) {  // Backup
      backup_cost = total_disk_size * disk_backup
      $("#backup_cost").html('$' + backup_cost.toFixed(2));
    } else {
      backup_cost = 0;
      $("#backup_cost").html('$0.00');
    } 

    total_cost = ram_cost + total_disk_cost + backup_cost;
    $("#total_cost").html('$' + total_cost.toFixed(2));
    $("#total_cost_field").val(total_cost.toFixed(2));
  }

  $(document).on("change", "#id_cpu" , function() {
    if ($('#id_ram').val() < this.value * 2) {
      $('#id_ram').val(this.value * 2);
      update_total_cost();
    }
  });

  $(document).on("change", "#id_misevos" , function() {
    os = $('#id_misevos option:selected').text();
    if (os) {
      if (os.startsWith('Windows')) {
        $('#div_misevprefix').show().prop('required',true);
        $('#div_misevregpre').show().prop('required',true);     
      } else {
        $('#div_misevprefix').hide().prop('required',false);
        $('#div_misevregpre').hide().prop('required',false); 
      }
    } else {
      $('#div_misevprefix').hide().prop('required',false);
      $('#div_misevregpre').hide().prop('required',false); 
    }
  });

  $(document).on("change", "#div_managed" , function() {
    if ($('#managed_0').prop("checked")) {  // Managed
      $('#div_misevos').show().prop('required',true);
      $('#div_misernonmang').hide().prop('required',false);
    } else if ($('#managed_1').prop("checked")) {  // Unmanaged
        $('#div_misevos').hide().prop('required',false);
        $('#div_misernonmang').show().prop('required',true);
    } else {
      $('#div_misevos').hide().prop('required',false);
      $('#div_misernonmang').hide().prop('required',false);
    }
  });

  $(document).on("change", "#div_misevprefix" , function() {
    if ($('#misevprefix_0').prop("checked")) {  // Registered Prefix
      $('#div_misevregpre').show().prop('required',true);
      //$('#div_misevnopre').hide().prop('required',false);
    } else if ($('#misevprefix_1').prop("checked")) {  // No, use standard
      $('#div_misevregpre').hide().prop('required',false);
      //$('#div_misevnopre').show().prop('required',true);
    } else {
      $('#div_misevregpre').hide().prop('required',false);
      //$('#div_misevnopre').hide().prop('required',false);
    }
  });

  // MiServer Data Sensitivity
  $('[data-tab="miServerData"]').on('show.bs.tab', function(event) {
    $("#div_misevregu").trigger("change");
    $("#div_misevnonregu").trigger("change");
  });

  $(document).on("change", "#div_misevregu" , function() {
    if ($('#misevregu_0').prop("checked")) {  // Regulated Sensitive Data
      $('#div_regulated_data').show().prop('required',true);
    } else if ($('#misevregu_1').prop("checked")) {  // No Sensitive Data
      $('#div_regulated_data').hide().prop('required',false);
    } else {
      $('#div_regulated_data').hide().prop('required',false);
    }
  });

  $(document).on("change", "#div_misevnonregu" , function() {
    if ($('#misevnonregu_0').prop("checked")) {  // Not Regulated Sensitive Data
      $('#div_non_regulated_data').show().prop('required',true);
    } else if ($('#misevnonregu_1').prop("checked")) {  // No Unregulated Sensitive Data
      $('#div_non_regulated_data').hide().prop('required',false);
    } else {
      $('#div_non_regulated_data').hide().prop('required',false);
    }
  });

  // Miserver Support Services
  $('[data-tab="miSevSupport"]').on('show.bs.tab', function(event) {
    $("#div_backup").trigger("change");
  });

  var x = document.getElementsByClassName("ccsel");
  var i;
  for (i = 0; i < x.length; i++) {
    chartcomChange(x[i]);
    //x[i].style.backgroundColor = "red";
  }
  


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

    if (use_ajax=="False") {  // TODO Enable AJAX
      //if (n == 1 && !validateForm()) return false;
      nextPrev(1);
    } else {
      $("#nextBtn").prop('disabled', true).addClass("spinner-border")
      sendTabData();
      //$("#nextBtn").prop('disabled', false).removeClass("spinner-border")
    }

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
  
      var label = obj.dataset.label;

      if(!name) {  // Don't display data not being saved
        continue;
      }

      if(type=="radio") {
        if (obj.checked == true) {
          label = $("#legend" + name).text();
          value = $("label[for='" + id + "']").text();
          if (obj.id == 'cat3feature31' || obj.id == 'cat2feature31' ) {
            label = "Speed Call";
          }
          if (obj.id == 'cat3feature47' || obj.id == 'cat2feature47' || obj.id == 'cat1feature47' ) {
            label = "Voicemail";
          }   
          tab.push({'label': label, 'value': value})
        }
      } else if (type=="checkbox") {
        if (obj.checked == true) {

          //label = $("#legend" + name).text();
          label = ''
          value = $("label[for='" + id + "']").text();
          if (obj.id == 'cat1feature48' || obj.id == 'cat2feature48' || obj.id == 'cat3feature48'  ) {
            label = "Optional";
          }
          if(id != "useSameCode56")
            tab.push({'label': label, 'value': value})
        }
      } else if (obj.tagName=="SELECT") {
        if(name) { // Don't process data we are not saving
        label = $("label[for='" + id + "']").text();
        value = $( "#" + id + " option:selected" ).text();
        tab.push({'label': label, 'value': value})
        }
      } else if (type=="button") {
        if($("#" + id).hasClass('selected')) { 
          label = $("label[for='" + id + "']").text();
          value = $("#" + inp[i].id).val();
          if (name=="product" && obj.dataset.zcode ) {
            value = value + "(" + obj.dataset.zcode + ")";
          }
          tab.push({'label': label, 'value': value})
        }
      } else {
        name = $("#" + inp[i].id).attr('name')
        //console.log('name:' + name);
        if (!label) {
          label = $("label[for='" + id + "']").text();
        }
        if (name=="subscriberId") {
          label = "Subscriber ID";
        }
        value = $("#" + inp[i].id).val();
        if(name != 'product' || value != 0) { // don't show 0 product
          if (name=='product') {
            label = label + "(" + obj.dataset.zcode + ")";
          }
          tab.push({'label': label, 'value': value})
        }

      }
    }
  
    tabs[currStep] = tab;
  }

  function validateForm() {

    loccard = false;
    prodbutton = false;
    prodinput = false;

    inp = $("#step" + currStep + " :input:visible");
    //console.log(inp);
 
    valid = true;



    for (i = 0; i < inp.length; i++) {
      if (inp[i].checkValidity()) {
        $(inp[i]).attr("aria-invalid", "false");
      } else {
        $(inp[i]).attr("aria-invalid", "true");
        inp[i].className += " invalid";
        valid = false;
      }
      if($(inp[i]).hasClass('location-button')) {
        loccard = true;
      }
      if($(inp[i]).hasClass('product-button')) {
        prodbutton = true;
      }
      if($(inp[i]).hasClass('product-input')) {
        prodinput = true;
      }
    }

    if(currTab == 'PhoneLocation' && $("#foundPhone").html() == '123-123-1234') {
      document.getElementById("id_phone_number").setCustomValidity("Not Found");
      $("#workflowForm").addClass('was-validated');
      valid = false;
    }

    if (loccard) {
        if (!$(".location-button").hasClass("selected")) {
          $(".location-card").addClass("card-not-selected");
          $("#must_sel").show();
          valid = false;
        }
    }

    if (prodbutton) {
      if (!$(".product-button").hasClass("selected")) {
        $(".product-card").addClass("card-not-selected");
        $("#mustchoose").show();
        valid = false;
      }
    }  
    if(prodinput){
       if (!$(".product-input").hasClass("selected")) {
        $(".product-card").addClass("card-not-selected");
        $("#mustchoose").show();
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
         summary = summary + '~' + heading + '^';
         
        for (field = 0; field < tabs[tab].length; field++) {
          txt = '<b>' + tabs[tab][field].label.trim() + '</b>  ' + tabs[tab][field].value.trim() + '<br>';
          summary = summary + tabs[tab][field].label.trim() + '\t' + tabs[tab][field].value.trim() + '^';
          $('#reviewstep' + tab).append(txt);
        }
      }
    }
    $('#reviewSummary').val(summary); 
  }




  $('[data-tab="SubscriberID"]').on('shown.bs.tab', function(event) {

    max = $("#id_cancelAuth").val();
    $("#subscriberId").show();
    count = $("[id^=authdiv]").length;

    $("#subscriberId").removeAttr('data-sequence');
    $("#subscriberId").removeAttr('data-condition');
    var rec = $("#subscriberId").clone();

    for (i = 1; i < (max-count); i++) {

        num = i.toString();

        var rec = $("#subscriberId").clone();

        rec.attr("id", "authdiv" + num);
    
        $("#step2").append(rec);

    }
})

$('[data-tab="volumeSelection"]').ready(function() {
  //$("#nextBtn").hide();
});

$('[data-tab="volumeSelection"]').on('hidden.bs.tab', function(event) {
  $("#nextBtn").show();
});



});  // Document Ready


function useSameShortCode(obj) {
  if (obj.checked) {    
    $('.ccsel').not('#name_oneTimeCharges').attr("disabled","disabled");
    $('.dccsel').not('#dept_oneTimeCharges').attr("disabled","disabled");
    occ = $('#name_oneTimeCharges option:selected').val();
    $('.ccsel').val(occ);
    occ = $('#oneTimeCharges').val();
    $(".ccval").val(occ);  // Set all chartcom values same as OCC
  } else {
    $('.ccsel').removeAttr("disabled","disabled");
    $('.dccsel').removeAttr("disabled","disabled");
  }
}

function chartcomChange(obj) {

  id = "#" + obj.id.substring(5,99);
  val = $('#' + obj.id + ' option:selected').data('chartcom');

  $(id).val(val);


  if (obj.id == 'name_oneTimeCharges') {
    val = $('#' + obj.id + ' option:selected').data('chartcom-id');
    $('#occ_key').val(val);
  }

  if ( $('#useSameCode' + obj.dataset.tabid).prop('checked') ) {
    occ = $('#name_oneTimeCharges option:selected').val();
    $(".ccsel").val(occ);  // Set all chartcom names same as OCC
    occ = $('#oneTimeCharges').val();
    $(".ccval").val(occ);  // Set all chartcom values same as OCC
  }
}

  function filterChartcom(obj) { 
    id = '#name_' + obj.dataset.target;
    $(id).find('option:selected').attr('selected', false);
    if (obj.value=='all') {
      $(id).find('[data-dept]').show();
    } else {
      $(id).find('[data-dept]').hide();
      $(id).find("[data-dept='" + obj.value + "']").show();
    }
    $(id).find('option:selected').attr('selected', false);
    
  }


  function addRow(record) {
    // clone source div by ID
    console.log(record, "add")
    if (typeof row_count == "undefined") {
      row_count = 0;
    } else {
      row_count = row_count + 1;
    }

    var row = $("#" + record + "_new").clone();
    row.attr("id", record + "_" + row_count);
    row.show();
    $("#" + record + "_list").append(row);   // TODO Find last host
    $("#" + record + "_new").hide()
  
    $(".nodeName").focus(); 
    $(this).next('input:text').focus();

  }

function addHost() {
  // clone host_new
  if (typeof host_count == "undefined") {
    host_count = 0;
  } else {
    host_count = host_count + 1;
  }
  
  var rec = $("#host_new").clone();

  rec.attr("id", "host_new_" + host_count);
  rec.show();
  $("#host_list").append(rec);   // TODO Find last host

  $("#host_new").hide()

  $(".nodeName").focus(); 
}

function modifyVolume(del_flag, volumeID) {
  currStep = 4;

  $('#instance_id').val(volumeID);


  if(del_flag==1) {
    lastStep = document.getElementsByClassName("tab-pane").length;
    $('#pills-step'+lastStep).removeClass('disabled');
    //$('#pills-tab li:last-child a').tab('show') 

    $('[data-tab="nfsAccess"]').hide();
    $('[data-tab="detailsNFS"]').hide();
    $('[data-tab="detailsCIFS"]').hide();
    $('[data-tab="storageBilling"]').hide();

    sendTabData({name: 'volaction', value: 'Delete'});
  } else {
    $('#instance_id').val(volumeID);
    sendTabData();
  }

  $('[data-tab="volumeSelection"]').hide();

  //$('#pills-step'+currStep).removeClass('disabled');
  //$('#pills-tab li:nth-child(' + currStep + ') a').tab('show');
}
  


function modifySubscription(del_flag, subscriptionID) {
  currStep = 4;

  $('#instance_id').val(subscriptionID);

  if(del_flag==1) {
    lastStep = document.getElementsByClassName("tab-pane").length;
    $('#pills-step'+lastStep).removeClass('disabled');
    //$('#pills-tab li:last-child a').tab('show') 

    $('[data-tab="backupDetails"]').hide();
    $('[data-tab="storageBilling"]').hide();

    sendTabData({name: 'volaction', value: 'Delete'});
  } else {
    $('#instance_id').val(subscriptionID);
    sendTabData();
  }

  $('[data-tab="subscriptionSelect"]').hide();

  //$('#pills-step'+currStep).removeClass('disabled');
  //$('#pills-tab li:nth-child(' + currStep + ') a').tab('show');
}

function sendTabData(field) {
  data = $('#workflowForm').serializeArray();
  if (field != 'undefined') {
    data.push(field)
  }
  data.push({name: 'tab', value: currTab});
  data.push({name: 'item_id', value: item_id});
  data.push({name: 'sequence', value: currStep});

  // List the fields that are visible.  TODO use the data from validate form
  inp = $("#step" + currStep + " :input:visible");

  visible = []
  for (i = 0; i < inp.length; i++) {
    visible.push(inp[i].name);
  }
  data.push({name: 'visible', value: visible});

  $.ajax({
      url : "/orders/ajax/send_tab_data/", 
      type : "POST", 
      data : data, 

      beforeSend: function(){
        console.log('before');
        //$('#nextBtn').addClass('disabled'); 
      },

      success : function(json) {
          redirect = json['redirect'];

          if (typeof(redirect) != 'undefined') {
            window.location.replace(redirect);
          } else {
            $("#nextBtn").prop('disabled', false).removeClass("spinner-border");
          }

          tab_name = json['tab_name'];
          valid = json['valid'];
          tab_content = json['tab_content'];
          console.log(tab_name)
          pane = $('[data-pane="' + tab_name + '"]').html(tab_content);

          if (valid) {
            $("input").removeClass('is-invalid');
            //$("#workflowForm").removeClass('was-validated');
            item_id = json['item_id'];
            $('[data-tab="' + tab_name + '"]').removeClass('disabled');
            $('#pills-tab a[href="#' + pane[0].id + '"]').tab('show')
          } else {
            //$("#workflowForm").addClass('was-validated');
            $('#pills-tab a[href="#' + pane[0].id + '"]').trigger('show')
            console.log('not valid');
          }
      },

      // handle a non-successful response
      error : function(xhr,errmsg,err) {
          $('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+
              " <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
          console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
      },

      // handle a non-successful response
      complete: function(){
        console.log('complete');

        //$('#nextBtn').removeClass('disabled'); ;
      }

  });
};