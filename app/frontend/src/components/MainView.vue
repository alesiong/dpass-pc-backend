<template>
    <div class="mdui-fab-wrapper" mdui-fab="{trigger: 'hover'}">
        <button class="mdui-fab mdui-ripple mdui-color-theme"
                id="fab-add"
                mdui-tooltip="{content: 'New Master Password', position: 'left'}"
                v-on:click="addPassword">
            <i class="mdui-icon material-icons">add</i>
        </button>

        <div class="mdui-fab-dial">
            <button class="mdui-fab mdui-fab-mini mdui-ripple mdui-color-blue"
                    id="fab-verify"
                    mdui-tooltip="{content: 'Verify Master Password', position: 'left'}"
                    v-on:click="verifyPassword">
                <i class="mdui-icon material-icons">verified_user</i>
            </button>
        </div>
    </div>
</template>

<script src="../scripts/MainView.js"></script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<!-- TODO: either write the styles here or use 'src' attribute-->
<style scoped>

</style>