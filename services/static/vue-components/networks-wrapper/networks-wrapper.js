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