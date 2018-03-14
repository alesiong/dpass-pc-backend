<template>
    <div v-if="type === 'password'">
        <div class="mdui-shadow-8 item-block">
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
                    <div class="mdui-row">
                            <span class="mdui-col-xs-3 mdui-typo-subheading">
                                Password
                            </span>
                        <span class="mdui-col-xs-3 mdui-typo-subheading">
                                <span v-if="showPlain">
                                    {{ getPassword(data.key) }}
                                </span>
                                <span v-else>
                                    ••••••••
                                </span>
                            </span>
                        <button class="mdui-col-xs-3 mdui-btn mdui-ripple mdui-btn-icon button-reveal"
                                mdui-tooltip="{content: 'Copy', position: 'top'}"
                                @click="onCopyPassword(data.key)">
                            <i class="mdui-icon material-icons">content_copy</i>
                        </button>
                        <button class="mdui-col-xs-3 mdui-btn mdui-ripple mdui-btn-icon button-reveal"
                                mdui-tooltip="{content: 'Reveal/Hide', position: 'top'}"
                                @click="onToggleReveal">
                                <span v-if="showPlain">
                                    <i class="mdui-icon ion-md-eye-off"></i>
                                </span>
                            <span v-else>
                                    <i class="mdui-icon ion-md-eye"></i>
                                </span>
                        </button>
                    </div>
                    <br/>
                    <div class="mdui-typo-caption-opacity">
                        Last update at {{data.date | formatDate}}
                    </div>
                </div>
            </div>
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
    }

    .site-icon {
        width: 120px;
        min-height: 120px;
        max-height: 240px;
        float: left;
    }

    .button-reveal {
        margin-top: -16px;
        width: 48px;
        height: 48px;
    }
</style>