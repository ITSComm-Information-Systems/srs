const midesktop_networks = new Vue({
    el: '#network',
    delimiters: ['[[', ']]'],
    data: {
        selectedNetwork: null,
        filteredNetworks: [], // Add a data property to store filtered networks
        visible: false,
        groups: groups
    },
    mounted() {
        // Listen for the custom event emitted by the global event bus
        eventBus.$on('group-selected', this.handleGroupChange);
        eventBus.$on('network-type-selected', this.handleVisibility);
        this.filteredNetworks.push({
            'id': 'new',
            "name": '-- New Dedicated Network',
            "owner": 'None'
        })
    },
    methods: {
        handleGroupChange(selectedGroup) {
            // Update the selectedGroup value when the group selection changes
            this.selectedGroup = selectedGroup;
            this.selectedGroupID = this.getGroupIdByName(selectedGroup)
            this.updateFilteredNetworks();
        },
        handleVisibility(selectedNetworkType){
            if (selectedNetworkType == 'dedicated'){
                this.visible = true
            }
            else{
                this.visible = false
            }
        },
        updateFilteredNetworks() {
            if (!this.selectedGroup) {
                // If no group is selected, show all networks
                this.filteredNetworks = [];
            } else {
                // Filter networks based on the selected group's id
                this.filteredNetworks = networklist.filter(network => network.owner === this.selectedGroupID);
            }

            this.filteredNetworks.push({
                'id': 'new',
                "name": '-- New Dedicated Network',
                "owner": 'None'
            })
        },
        getGroupIdByName(groupName) {
            const group = this.groups.find(group => group.name === groupName);
            return group ? group.id : null;
        }
    },
    watch: {
        selectedNetwork: function (newVal) {
            eventBus.$emit('new-dedicated-network-selected', newVal);
            
        }
    },
});