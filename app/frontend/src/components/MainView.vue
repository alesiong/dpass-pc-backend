<template>
    <div>
        <div class="mdui-row action-bar">
            <div class="mdui-col-xs-4 mdui-m-l-1">
                <div class="mdui-row mdui-typo-display-1-opacity">
                    {{title}} ({{length}})
                </div>
                <div class="mdui-row mdui-typo-caption-opacity mdui-m-t-1"
                     v-if="search">
                    Searching: {{search}}
                </div>
            </div>

            <!--<button class="mdui-btn mdui-btn-icon mdui-ripple mdui-btn-raised mdui-color-red"-->
            <!--mdui-tooltip="{content: 'sort by date'}">-->
            <!--<i class="mdui-icon material-icons">sort</i>-->
            <!--</button>-->

            <!--<button class="mdui-btn mdui-btn-icon mdui-color-theme-accent mdui-btn-raised mdui-ripple"-->
            <!--mdui-tooltip="{content: 'sort by alpha'}">-->
            <!--<i class="mdui-icon material-icons">sort_by_alpha</i>-->
            <!--</button>-->

            <div class="mdui-col-xs-2 mdui-float-right">
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

                  v-bind:type="item.type"
                  v-bind:data="{
                    url: item.url,
                    siteName: item.siteName,
                    userId: item.userId,
                    date: item.date,
                    key: item.key
                  }"
                  v-on:copy-success="onCopiedPassword"
                  v-on:click-delete="onConfirmDelete"
            />

        </div>

        <password-dialog
                ref="dialog"
                v-on:click-add="onConfirmAddItem"/>

        <div v-if="type === 'all'">
            <div class="mdui-fab-wrapper" mdui-fab="{trigger: 'hover'}">
                <button class="mdui-fab mdui-ripple mdui-color-theme"
                        mdui-tooltip="{content: 'Add Password', position: 'left'}"
                        v-on:click="onAddPassword">
                    <i class="mdui-icon material-icons">add</i>
                </button>

                <div class="mdui-fab-dial">
                    <button class="mdui-fab mdui-fab-mini mdui-ripple mdui-color-yellow"
                            mdui-tooltip="{content: 'Add Secret Note', position: 'left'}"
                            v-on:click="onAddSecretNote">
                        <i class="mdui-icon material-icons">note_add</i>
                    </button>
                </div>

            </div>
        </div>
        <div v-else>
            <button class="mdui-fab mdui-fab-fixed mdui-ripple mdui-color-theme"
                    v-bind:mdui-tooltip="'Add ' + typeName | mduiTooltip"
                    v-on:click="type === 'password'? onAddPassword() : onAddSecretNote()">
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