<template>
    <div id="app">
        <div class="mdui-container-fluid app-container">
            <app-header/>
            <app-menu/>
            <div v-if="guard">
                <guard-view v-bind:state="initState"
                            v-bind:verify="passwordVerification"
                            v-on:added-password="refreshState"
                            v-on:verified-password="onVerifiedPassword"/>
            </div>
            <div v-else>
                <router-view/>
            </div>
        </div>
    </div>
</template>

<!--TODO: write scripts here like this-->
<script src="./scripts/App.js"></script>

<!--TODO: global(app-wise) style sheet should be put in the file app/frontend/src/css/app.css-->
<style src="./css/app.css"></style>
