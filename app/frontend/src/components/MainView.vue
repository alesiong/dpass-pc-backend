<template>
    <div>
        <div class="item-allbar">
            <div class="mdui-shadow-8 item-bar"
                 v-for="item in items" v-bind:key="item.key"
                 v-if="!item.hide">
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
                                **********
                            </div>
                            <button class="mdui-col botton-reveal mdui-row-gapless mdui-typo-caption mdui-btn mdui-ripple"
                                    @click="copyPassword(item.key)">
                                COPY
                            </button>
                            <button class="mdui-col botton-reveal mdui-row-gapless mdui-typo-caption mdui-btn mdui-ripple"
                                    @click="showToggle">
                                reveal
                            </button>
                        </div>
                        <p></p>
                        <div class="mdui-typo-caption-opacity">Last update at
                            {{formatDate(item.date)}}
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
    }

    .botton-reveal {
        margin-top: -11px;
        width: 32px;
        font-size: 12px;
        height: 32px;
    }
</style>