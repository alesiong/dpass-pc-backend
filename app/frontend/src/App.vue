<template>
    <div id="app">
        <div class="mdui-container-fluid app-container">
            <app-header/>
            <app-menu/>

            <router-view/>
        </div>
    </div>
</template>

<!--TODO: write scripts here like this-->
<script src="./scripts/App.js"></script>

<!--TODO: global(app-wise) style sheet should be put in the file app/frontend/src/css/app.css-->
<style src="./css/app.css"></style>
