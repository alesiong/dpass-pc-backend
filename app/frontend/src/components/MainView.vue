<template>
    <div>
        <div class="item-allbar">
            <div class="mdui-shadow-8 item-bar"
                 v-for="item in items" v-bind:key="item.key" v-if="!item.hide">
                <div class="mdui-row">
                    <div class="mdui-col-xs-1 mdui-float-left site-icon">
                        <img height=90px
                             v-bind:src="item.url+'/favicon.ico'"/>
                    </div>
                    <div class="mdui-col-xs-6">
                        <div class="mdui-typo-headline">{{ item.url }}</div>
                        <p></p>
                        <div class="mdui-typo-subheading">{{item.userId}}</div>
                        <p></p>
                        <div class="mdui-row-xs-6">
                            <div class=" mdui-col passwordZoneFirst mdui-typo-subheading">
                                Password
                            </div>
                            <div class=" mdui-col mdui-row-gapless mdui-typo-subheading">
                                {{message}}
                            </div>
                            <button class="mdui-col botton-1 mdui-row-gapless mdui-typo-caption mdui-btn mdui-ripple"
                                    v-clipboard:copy="message"
                                    v-clipboard:success="onCopy"
                                    v-clipboard:error="onError">COPY
                            </button>
                            <button class="mdui-col botton-1  mdui-row-gapless mdui-typo-caption mdui-btn mdui-ripple"
                                    v-text="btnText"
                                    @click="showToggle"></button>
                        </div>
                        <p></p>
                        <div class="mdui-typo-caption-opacity">Last update at
                            {{item.date}}
                        </div>
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
    .botton-1{
        margin-top: -11px;
        width:30px;
        font-size: 12px;
        height:30px;
    }
</style>