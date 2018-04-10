<template>
    <div id="app">
        <div class="mdui-container-fluid ">
            <app-header
                    v-bind:guard="guard"
                    v-on:search="onSearch"/>
            <app-menu/>

            <div class="app-container">
                <guard-view v-if="guard"
                            v-bind:state="initState"
                            v-bind:verify="passwordVerification"
                            v-on:verified-password="onVerifiedPassword"/>
                <router-view v-else
                             v-bind:search="search"/>
            </div>

        </div>

        <input id="clickboard" type="hidden">
    </div>
</template>

<script src="./scripts/App.js"></script>

<style src="./css/app.css"></style>
