document.addEventListener("DOMContentLoaded", function (event) {

    var service_rates = {
        "9": // Turbo
            { "NFS": [11, 12, 13, 14], "CIFS": [15, 16, 17, 18] },
        "10": // Locker
            { "NFS": [19, 20, 21, 22], "CIFS": [23, 24, 25, 26] },
        "11": // Data Den
            { "NFS": [17] }
    }

    document.getElementById("id_service").addEventListener("change", function () {
        filter_rate_choices();
    });

    document.getElementById("id_type").addEventListener("change", function () {
        filter_rate_choices();
    });

    // Filter Rates based on Service
    function filter_rate_choices() {
        var protocol = document.getElementById('id_type');
        var service = document.getElementById('id_service');

        var rates = document.getElementById('id_rate'), rate, i;
        rates[0].selected = true;
        valid_rates = service_rates[service.value][protocol.value];
        for (i = 1; i < rates.length; i++) {
            rate = rates[i];
            if (valid_rates.includes(parseInt(rate.value))) {
                rate.style.display = "block";
            } else {
                rate.style.display = "none";
            }
        }
    }


});