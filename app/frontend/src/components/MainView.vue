<template>
    <div>
        <div class="mdui-row action-bar">
            <div class="mdui-col-xs-3 mdui-typo-display-1-opacity mdui-m-l-1">
                All ({{length}})
            </div>

            <!--<button class="mdui-btn mdui-btn-icon mdui-ripple mdui-btn-raised mdui-color-red"-->
            <!--mdui-tooltip="{content: 'sort by date'}">-->
            <!--<i class="mdui-icon material-icons">sort</i>-->
            <!--</button>-->

            <!--<button class="mdui-btn mdui-btn-icon mdui-color-theme-accent mdui-btn-raised mdui-ripple"-->
            <!--mdui-tooltip="{content: 'sort by alpha'}">-->
            <!--<i class="mdui-icon material-icons">sort_by_alpha</i>-->
            <!--</button>-->

            <div class="mdui-col-xs-2 mdui-col-offset-xs-10 ">
                <select class="mdui-select" mdui-select="{position: 'bottom'}">
                    <option value="1">Sort by alpha</option>
                    <option value="2">Sort by date</option>
                </select>
            </div>

        </div>


        <div class="item-allbar">
            <item v-for="item in items"
                  v-bind:key="item.key"
                  v-if="shown(item)"

                  type="password"
                  v-bind:data="{
                    url: item.url,
                    siteName: item.siteName,
                    userId: item.userId,
                    date: item.date,
                    key: item.key
                  }"
                  v-on:copy-success="onCopiedPassword"
            />

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
    .item-allbar .item-block:not(:first-child) {
        margin-top: 24px;
    }

    .action-bar {
        margin-bottom: 40px;
    }
</style>