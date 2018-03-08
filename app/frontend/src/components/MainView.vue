<template>
    <div>
        <div class="item-allbar">
            <div class="mdui-shadow-8 item-bar"
                 v-for="item in items" v-if="!item.hide">
                <div class="mdui-row">
                    <div class="mdui-col-xs-1 mdui-float-left site-icon">
                        <img height=90px
                             v-bind:src="item.url+'/favicon.ico'"/>
                    </div>
                    <div class="mdui-col-xs-6">
                        <div class="mdui-typo-headline">{{ item.url }}</div>
                        <p>{{item.userId}}</p>
                        <p>Last {{item.date}}</p>
                    </div>
                </div>
            </div>
        </div>

        <password-dialog
                ref="dialog"
                v-on:click-add="addItem"/>

        <div class="mdui-fab-wrapper" mdui-fab="{trigger: 'hover'}">
            <button class="mdui-fab mdui-ripple mdui-color-theme"
                    id="fab-add"
                    mdui-tooltip="{content: 'New Password', position: 'left'}"
                    v-on:click="onAddPassword">
                <i class="mdui-icon material-icons">add</i>
            </button>

            <!--<div class="mdui-fab-dial">-->
            <!--<button class="mdui-fab mdui-fab-mini mdui-ripple mdui-color-blue"-->
            <!--id="fab-verify"-->
            <!--mdui-tooltip="{content: 'Verify Master Password', position: 'left'}"-->
            <!--v-on:click="verifyPassword">-->
            <!--<i class="mdui-icon material-icons">verified_user</i>-->
            <!--</button>-->
            <!--</div>-->
        </div>
    </div>
</template>

<script src="../scripts/MainView.js"></script>

<!-- Add "scoped" attribute to limit CSS to this component only -->

<!-- TODO: either write the styles here or use 'src' attribute-->
<style scoped>
    .item-allbar .item-bar:not(:first-child) {
        margin-top: 24px;
    }

    .item-bar {
        padding: 24px;
    }

    .site-icon {
        width: 120px;
        min-height: 120px;
        max-height: 240px;
        float: left;
        /*margin: 3px;*/
        /*padding: 3px;*/
    }
</style>