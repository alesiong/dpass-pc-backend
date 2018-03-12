<template>
    <div>

        <h1 class="doc-chapter-title doc-chapter-title-first mdui-text-color-grey"
            style="margin-top:1.5em">All (6)</h1>


        <div class="mdui-container mdui-valign" >
            <div class="mdui-toolbar-spacer"></div>

            <button class="mdui-fab mdui-fab-mini mdui-ripple mdui-color-red"
                    mdui-tooltip="{content: 'sort by date'}">
                <i class="mdui-icon material-icons">sort</i>
            </button>

            <button class="mdui-fab mdui-fab-mini mdui-color-theme-accent mdui-ripple mdui-color-yellow"
                    mdui-tooltip="{content: 'sort by alpha'}">
                <i class="mdui-icon material-icons">sort_by_alpha</i>
            </button>

            <select class="mdui-select" mdui-select="{position: 'bottom'}"
                    style="margin-left:2.5em; margin-bottom:1.5em" >
                <option value="1">Sort by alpha</option>
                <option value="2">Sort by date</option>
            </select>
        </div>


        <div class="item-allbar" >
            <div class="mdui-shadow-8 item-bar"
                 v-for="(item, index) in items" v-bind:key="item.key"
                 v-if="!item.hide">
                <div class="mdui-row">
                    <div class="mdui-col-xs-1 mdui-float-left site-icon">
                        <img height=90px
                             v-bind:src="item.url+'/favicon.ico'"/>
                    </div>
                    <div class="mdui-col-xs-6">
                        <div class="mdui-typo-headline">{{ item.siteName }}</div>
                        <br/>
                        <div class="mdui-typo-subheading-opacity">{{ item.url }}</div>
                        <br/>
                        <div class="mdui-typo-subheading">{{item.userId}}</div>
                        <br/>
                        <div class="mdui-row">
                            <span class="mdui-col passwordZoneFirst mdui-typo-subheading">
                                Password
                            </span>
                            <span class="mdui-col mdui-typo-subheading">
                                <span v-if="item.isShow">
                                    {{ getPass(item.key) }}
                                </span>
                                <span v-else>
                                    ••••••••
                                </span>
                            </span>
                            <button class="mdui-col botton-reveal mdui-typo-caption mdui-btn mdui-ripple"
                                    @click="copyPassword(item.key)">
                                Copy
                            </button>
                            <button class="mdui-col botton-reveal mdui-typo-caption mdui-btn mdui-ripple"
                                    @click="showToggle(index)">
                                <span v-if="item.isShow">
                                    Hide
                                </span>
                                <span v-else>
                                    Reveal
                                </span>
                            </button>
                        </div>
                        <br/>
                        <div class="mdui-typo-caption-opacity">
                            Last update at {{formatDate(item.date)}}
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