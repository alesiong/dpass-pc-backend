<template>
    <div>
        <div class="item-allbar">
            <div class="mdui-shadow-8 item-bar"
                 v-for="(item, index) in items" v-bind:key="item.key"
                 v-if="!item.hidden">
                <div class="mdui-row">
                    <div class="mdui-col-xs-1 mdui-float-left site-icon">
                        <img height=90px
                             v-if="item.url.startsWith('http')"
                             v-bind:src="item.url+'/favicon.ico'"/>
                    </div>
                    <div class="mdui-col-xs-6">
                        <div class="mdui-typo-headline">{{ item.siteName }}
                        </div>
                        <br/>
                        <div class="mdui-typo-subheading-opacity">
                            {{ item.url }}
                        </div>
                        <br/>
                        <div class="mdui-typo-subheading">{{item.userId}}</div>
                        <br/>
                        <div class="mdui-row">
                            <span class="mdui-col-xs-3 mdui-typo-subheading">
                                Password
                            </span>
                            <span class="mdui-col-xs-3 mdui-typo-subheading">
                                <span v-if="item.showPlain">
                                    {{ getPassword(item.key) }}
                                </span>
                                <span v-else>
                                    ••••••••
                                </span>
                            </span>
                            <button class="mdui-col-xs-3 mdui-btn mdui-ripple mdui-btn-icon botton-reveal"
                                    @click="onCopyPassword(item.key)">
                                <i class="mdui-icon material-icons">content_copy</i>
                            </button>
                            <button class="mdui-col-xs-3 mdui-btn mdui-ripple mdui-btn-icon botton-reveal"
                                    @click="onToggleReveal(index)">
                                <span v-if="item.showPlain">
                                    <i class="mdui-icon ion-md-eye-off"></i>
                                </span>
                                <span v-else>
                                    <i class="mdui-icon ion-md-eye"></i>
                                </span>
                            </button>
                        </div>
                        <br/>
                        <div class="mdui-typo-caption-opacity">
                            Last update at {{item.date | formatDate}}
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <password-dialog
                ref="dialog"
                v-on:click-add="onConfirmAddItem"/>

        <div class="mdui-fab-wrapper" mdui-fab="{trigger: 'hover'}">
            <button class="mdui-fab mdui-ripple mdui-color-theme"
                    id="fab-add"
                    mdui-tooltip="{content: 'New Password', position: 'left'}"
                    v-on:click="onAddPassword">
                <i class="mdui-icon material-icons">add</i>
            </button>

        </div>

    </div>
</template>

<script src="../scripts/MainView.js"></script>

<!-- Add "scoped" attribute to limit CSS to this component only -->

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
    }

    .botton-reveal {
        margin-top: -16px;
        width: 48px;
        height: 48px;
    }
</style>