const midesktop_networks = new Vue({
    el: '#network',
    delimiters: ['[[', ']]'],
    data: {
        selectedNetwork: null,
        filteredNetworks: [], // Add a data property to store filtered networks
        visible: true
    },
    mounted() {
        // Listen for the custom event emitted by the global event bus
        eventBus.$on('group-selected', this.handleGroupChange);
    },
    methods: {
        handleGroupChange(selectedGroup) {
            // Update the selectedGroup value when the group selection changes
            this.selectedGroup = selectedGroup;
            this.updateFilteredNetworks();
        },
        updateFilteredNetworks() {
            if (!this.selectedGroup) {
                // If no group is selected, show all networks
                this.filteredNetworks = [];
            } else {
                // Filter networks based on the selected group's id
                this.filteredNetworks = networklist.filter(network => network.owner === this.selectedGroup);
            }
        },
    },
    watch: {
        // filteredNetworks: function (newVal) {
        //     if (newVal.length == 0){
        //         //this.hide()
        //     } else {
        //         this.show()
        //     }
        // }
    },
});