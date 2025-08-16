<template>
    Users:
    <div
    v-for="user in Users"
    v-bind:key="user.id"
    >
        <h1>{{ user.username }}</h1>
    </div>
</template>

<script>
    import axios from 'axios'
    export default {
        name: 'Users',
        data() {
            Users: []
        },
        components: {   
        },
        mounted() {
            this.getUser() 
        },
        methods: {
            Users() {
                axios.get('/tax/users/')
                .then(response => {
                    this.Users = response.data
                })
                .catch(error => {
                    console.log(error)
                })
            }
        }
    }
</script>