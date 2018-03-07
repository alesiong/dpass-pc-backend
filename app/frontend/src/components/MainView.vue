<template>
    <div>
        <div class="item-allBar">
            <div class="mdui-shadow-8 item-bar" v-for="item in items" v-if="!item.hide">
                <div class="mdui-row">
                    <div class="mdui-col-xs-1 mdui-float-left site-icon">
                        <img height=90px v-bind:src="item.url+'/favicon.ico'"/></div>
                    <div class="mdui-col-xs-6">
                        <div class="mdui-typo-headline">{{ item.url }}</div>
                        <p>{{item.userId}}</p>
                        <p>Last {{item.date}}</p>
                    </div>
                </div>
            </div>
        </div>
        <div class="mdui-dialog" id="AddDialog">
            <div class="mdui-dialog-title">Enter Your New Password</div>
            <div class="mdui-dialog-content">
                <div class="mdui-textfield">
                    <i class="mdui-icon material-icons">note_add</i>
                    <label class="mdui-textfield-label">URL</label>
                    <input class="mdui-textfield-input"
                           v-model="url"/>
                </div>
                <div class="mdui-textfield">
                    <i class="mdui-icon material-icons">explore</i>
                    <label class="mdui-textfield-label">Site Name</label>
                    <input class="mdui-textfield-input"
                           v-model="siteName"/>
                </div>
                <div class="mdui-textfield">
                    <i class="mdui-icon material-icons">account_circle</i>
                    <label class="mdui-textfield-label">User Name</label>
                    <input class="mdui-textfield-input" type="text"
                           v-model="userId"/>
                    <!--<div class="mdui-textfield-error mdui-typo-caption">Invalid User ID</div>-->
                </div>
                <div class="mdui-textfield">
                    <i class="mdui-icon material-icons">vpn_key</i>
                    <label class="mdui-textfield-label">Password</label>
                    <input class="mdui-textfield-input" type="password" v-model="password"/>
                    <!--<div class="mdui-textfield-error mdui-typo-caption">Invalid Password</div>-->
                </div>
            </div>
            <div class="mdui-dialog-actions">
                <span class="mdui-float-left dialog-warn">
                    Warning: No empty entry.
                </span>
                <button class="mdui-btn mdui-ripple">
                    <i class="mdui-icon mdui-icon-left material-icons">autorenew</i>
                    generate key
                </button>
                <button class="mdui-btn mdui-ripple" mdui-dialog-close>cancel</button>
                <button class="mdui-btn mdui-ripple" mdui-dialog-confirm v-on:click="addItem"
                        v-bind:disabled="checkIsInvalid()"
                    v-bind:mdui-tooltip="checkIsInvalid() ? '{content: \'Verify Master Password\'}' : ''">add
                </button>
            </div>
        </div>

        <div class="mdui-fab-wrapper" mdui-fab="{trigger: 'hover'}">
            <button class="mdui-fab mdui-ripple"
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
    .item-allBar .item-bar:not(:first-child) {
        margin-top: 24px;
    }

    .item-bar {
        padding: 25px;
    }

    .site-icon{
        width: 120px;
        min-height: 120px;
        max-height: 240px;
        float: left;
        margin: 3px;
        padding: 3px;
    }
    .dialog-warn{
        padding-top: 8px;
        margin-left: 60px;
        color:#FF1744;
    }
</style>