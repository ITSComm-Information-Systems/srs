const admin_group = new Vue({
    el: '#group',
    delimiters: ['[[', ']]'],
    data: {
        selectedGroup: null,
        groups: groups
    },
    mounted() {
    },
    watch: {
        selectedGroup: function (newVal) {
            // Emit the custom event when the selected group changes using the global event bus
            eventBus.$emit('group-selected', newVal);
            console.log(newVal);
        }
    },

    methods: {
        handleGroupChange() {
            this.selectedGroup = this.selectedGroup;
        }
    }
});

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

const networks_wrapper = new Vue({
    el: '#networks-wrapper',
    delimiters: ['[[', ']]'],
    data: {
        visible: false
    },
    mounted() {
        // Listen for the custom event emitted by the global event bus
        console.log('ted')
        eventBus.$on('new-dedicated-network-selected', this.handleDedicatedNetworkSelected);
        eventBus.$on('network-type-selected', this.handleNetworkTypeSelected);
        
    },
    methods: {
        handleDedicatedNetworkSelected(selectedDedicatedType){
            if (selectedDedicatedType == 'new'){
                this.selectedDedicatedType = selectedDedicatedType
                this.visible = true
            }
            else{
                this.visible = false
            }
    
        },
        handleNetworkTypeSelected(selectedNetworkType){
            console.log(selectedNetworkType)
            if(selectedNetworkType == 'dedicated' && this.selectedDedicatedType == 'new'){
                this.selectedNetworkType = selectedNetworkType
                this.visible = true
            }else{
                this.selectedNetworkType = selectedNetworkType
                this.visible = false
            }
     }
    },
});

const midesktop_network_type = new Vue({
    el: '#network_type',
    delimiters: ['[[', ']]'],
    data: {
        selectedNetworkType: null,
    },
    mounted() {
        console.log('mount')
        // Listen for the custom event emitted by the global event bus
    },
    
    watch: {
        selectedNetworkType: function (newVal) {
            eventBus.$emit('network-type-selected', newVal);
        }
        
    },
});