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

        <input id="clickboard" type="hidden">
    </div>
</template>

<script src="./scripts/App.js"></script>

<style src="./css/app.css"></style>
