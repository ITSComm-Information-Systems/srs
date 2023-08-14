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