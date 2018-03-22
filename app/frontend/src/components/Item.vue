<template>
    <div v-if="type === 'password'" class="mdui-shadow-8 item-block">
        <div class="mdui-row">
            <div class="mdui-col-xs-1 mdui-float-left site-icon">
                <img height=90px
                     v-if="data.url.startsWith('http')"
                     v-bind:src="data.url+'/favicon.ico'"/>
            </div>
            <div class="mdui-col-xs-6">
                <div class="mdui-typo-headline">{{ data.siteName }}
                </div>
                <br/>
                <div class="mdui-typo-subheading-opacity">
                    {{ data.url }}
                </div>
                <br/>
                <div class="mdui-typo-subheading">{{data.userId}}</div>
                <br/>
                <div v-if="!data.hidden"
                     class="mdui-row">
                    <span class="mdui-col-xs-3 mdui-typo-subheading">
                        <span v-if="showPlain">
                            {{ getPassword(data.key) }}
                        </span>
                        <span v-else>
                            ••••••••
                        </span>
                    </span>
                    <button class="mdui-col-xs-3 mdui-btn mdui-ripple mdui-btn-icon action-button mdui-text-color-pink-300"
                            mdui-tooltip="{content: 'Copy', position: 'top'}"
                            @click="onCopyPassword(data.key)">
                        <i class="mdui-icon material-icons">content_copy</i>
                    </button>
                    <button class="mdui-col-xs-3 mdui-btn mdui-ripple mdui-btn-icon action-button mdui-text-color-indigo-400"
                            :mdui-tooltip="JSON.stringify(
                                    {content: showPlain ? 'Hide': 'Show', position: 'top'})"
                            @click="onToggleReveal">
                        <i v-if="showPlain"
                           class="mdui-icon ion-md-eye-off"></i>
                        <i v-else
                           class="mdui-icon ion-md-eye"></i>
                    </button>
                    <button class="mdui-col-xs-3 mdui-btn mdui-ripple mdui-btn-icon action-button mdui-text-color-green-800"
                            mdui-tooltip="{content: 'Edit', position: 'top'}"
                            @click="onModify">
                        <i class="mdui-icon material-icons">edit</i>
                    </button>
                    <!-- TODO: It would be better to only allow deletion from editing dialog -->
                    <button hidden
                            class="mdui-col-xs-3 mdui-btn mdui-ripple mdui-btn-icon action-button mdui-text-color-brown-300"
                            mdui-tooltip="{content: 'Delete', position: 'top'}"
                            @click="onDelete">
                        <i class="mdui-icon material-icons">delete_forever</i>
                    </button>
                </div>
                <br/>
                <div class="mdui-typo-caption-opacity">
                    Last update at {{data.date | formatDate}}
                </div>
            </div>
        </div>

        <button class="mdui-btn mdui-ripple mdui-btn-icon hide-button"
                v-bind:mdui-tooltip="`{content: '${data.hidden? 'Show in list' : 'Hide from list'}'}`"
                @click="onHide">
            <i v-if="!data.hidden"
               class="mdui-icon material-icons">close</i>
            <i v-else
               class="mdui-icon material-icons">wb_sunny</i>
        </button>

        <div class="persistence"
             v-if="typeof(persistence) === 'boolean'">
            <div class="mdui-spinner mdui-spinner-colorful"
                 mdui-tooltip="{content: 'Synchronizing...'}"
                 v-if="!persistence"></div>
            <i class="mdui-icon material-icons mdui-text-color-theme"
               mdui-tooltip="{content: 'Already synchronized !'}"
               v-else>check</i>
        </div>
    </div>
    <div v-else-if="type === 'secret'"></div>
    <div v-else></div>
</template>

<script src="../scripts/Item.js">
</script>

<style scoped>
    .item-block {
        padding: 24px;
        position: relative;
    }

    .site-icon {
        width: 120px;
        min-height: 120px;
        max-height: 240px;
        float: left;
    }

    .action-button {
        margin-top: -16px;
        width: 48px;
        height: 48px;
    }

    .hide-button {
        top: 24px;
        right: 24px;
        position: absolute;
    }

    .persistence {
        bottom: 24px;
        right: 32px;
        position: absolute;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }

</style>