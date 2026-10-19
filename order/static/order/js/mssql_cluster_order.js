$(function () {
  const $form = $('#mssql-cluster-form');
  const $identifier = $('#id_cluster_identifier');
  const $diskBody = $('#cluster-disk-table tbody');
  const $diskData = $('#id_disks_json');

  function updatePreview() {
    const identifier = ($identifier.val() || '').toLowerCase();
    if (/^[tnp][da](?:0[1-9]|[1-9][0-9])$/.test(identifier)) {
      $('#cluster-name-preview').text(`db-${identifier}-c`);
      $('#server-name-preview').text(`db-${identifier}-cm1 / db-${identifier}-ca1`);
      if (identifier.charAt(0) === 'p') {
        $('#production-status-preview').text('Production');
      } else {
        $('#production-status-preview').text('Non-Production');
      }
    } else {
      $('#cluster-name-preview').text('db-...-c');
      $('#server-name-preview').text('db-...-cm1 / db-...-ca1');
      $('#production-status-preview').text('Enter a valid cluster identifier');
    }
    updateControllerChoices();
  }

  function updateControllerChoices() {
    const isSsas = ($identifier.val() || '').toLowerCase().charAt(1) === 'a';
    $diskBody.find('.cluster-controller').each(function () {
      const current = $(this).val();
      const choices = isSsas ? [1, 3] : [1, 2, 3];
      $(this).empty();
      choices.forEach((value) => $(this).append(new Option(String(value), String(value))));
      $(this).val(choices.includes(Number(current)) ? String(current) : String(choices[0]));
    });
  }

  function nextDeviceId(controller) {
    const used = new Set();
    $diskBody.find('tr').each(function () {
      if ($(this).find('.cluster-controller').val() === String(controller)) {
        used.add(Number($(this).find('.cluster-device').val()));
      }
    });
    const allowed = Array.from({ length: 16 }, (_, deviceId) => deviceId).filter((deviceId) => deviceId !== 7);
    return allowed.find((deviceId) => !used.has(deviceId)) ?? allowed[0];
  }

  function addDiskRow(disk = {}) {
    const $row = $('<tr>');
    const $controller = $('<select class="form-control cluster-controller" aria-label="SCSI controller">');
    const $device = $('<select class="form-control cluster-disk-input cluster-device" aria-label="Device ID">');
    const ssas = ($identifier.val() || '').toLowerCase().charAt(1) === 'a';
    (ssas ? [1, 3] : [1, 2, 3]).forEach((value) => $controller.append(new Option(String(value), String(value))));
    $controller.val(String(disk.controller || 1));
    const deviceId = disk.device_id ?? nextDeviceId($controller.val());
    Array.from({ length: 16 }, (_, value) => value)
      .filter((value) => value !== 7)
      .forEach((value) => $device.append(new Option(String(value), String(value))));
    $device.val(String(deviceId));

    $row.append($('<td>').append($controller));
    $row.append($('<td>').append($device));
    $row.append($('<td>').append($('<input type="text" maxlength="100" class="form-control cluster-disk-input cluster-label" aria-label="Disk label">').val(disk.label || '')));
    $row.append($('<td>').append($('<input type="number" min="1" step="1" class="form-control cluster-disk-input cluster-size" aria-label="Size in GB">').val(disk.size_gb || '')));
    $row.append($('<td>').append($('<button type="button" class="btn btn-link text-danger remove-cluster-disk" aria-label="Remove disk" title="Remove disk"><i class="fas fa-minus-circle" aria-hidden="true"></i></button>')));
    $diskBody.append($row);
  }

  $('#add-cluster-disk').on('click', function () { addDiskRow(); });
  $diskBody.on('click', '.remove-cluster-disk', function () { $(this).closest('tr').remove(); });
  $identifier.on('input change', updatePreview);

  $form.on('submit', function () {
    const disks = [];
    $diskBody.find('tr').each(function () {
      disks.push({
        controller: $(this).find('.cluster-controller').val(),
        device_id: $(this).find('.cluster-device').val(),
        label: $(this).find('.cluster-label').val(),
        size_gb: $(this).find('.cluster-size').val()
      });
    });
    $diskData.val(JSON.stringify(disks));
  });

  addDiskRow();
  updatePreview();
});
