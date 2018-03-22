<template>
    <div class="mdui-dialog" v-bind:id="id">
        <div class="mdui-dialog-title">{{ title }}</div>

        <div class="mdui-dialog-content">
            <div class="mdui-textfield">
                <i class="mdui-icon material-icons">note_add</i>
                <label class="mdui-textfield-label">URL</label>
                <input class="mdui-textfield-input"
                       type="text"
                       autocomplete="off"
                       v-model="url"/>
            </div>

            <div class="mdui-textfield">
                <i class="mdui-icon material-icons">explore</i>
                <label class="mdui-textfield-label">Site Name</label>
                <input class="mdui-textfield-input"
                       type="text"
                       autocomplete="off"
                       v-model="siteName"/>
            </div>

            <div class="mdui-textfield">
                <i class="mdui-icon material-icons">account_circle</i>
                <label class="mdui-textfield-label">User Name</label>
                <input class="mdui-textfield-input"
                       type="text"
                       autocomplete="off"
                       v-model="userId"/>
            </div>

            <div class="mdui-row" style="position: relative">
                <div class="mdui-col-xs-10">
                    <div class="mdui-textfield">
                        <i class="mdui-icon material-icons">vpn_key</i>
                        <label class="mdui-textfield-label">Password</label>
                        <input class="mdui-textfield-input"
                               v-bind:type="showPlain? 'text' : 'password'"
                               autocomplete="off"
                               v-model="password"/>
                    </div>
                    <button class="mdui-btn mdui-btn-icon mdui-ripple reveal-button"
                            v-on:click="showPlain = !showPlain">
                        <i v-if="!showPlain"
                           class="mdui-icon ion-md-eye"></i>
                        <i v-else
                           class="mdui-icon ion-md-eye-off"></i>
                    </button>
                </div>
                <div class="mdui-col-xs-2">
                    <button class="mdui-btn mdui-ripple generate-button"
                            mdui-tooltip="{content: 'Generate a Random Complicated Key in 8-16 Digits', position: 'top'}"
                            v-on:click="generateRandomPassword">
                        <!--<i class="mdui-icon mdui-icon-left material-icons ">autorenew</i>-->
                        generate
                    </button>
                </div>
            </div>
        </div>
        <div class="mdui-dialog-actions">
                <span class="mdui-float-left dialog-warn mdui-text-color-red-a400"
                      v-if="!valid">
                    <i class="mdui-icon material-icons"
                       style="margin-top: -4px;">error_outline</i>
                    All entries should be filled.
                </span>

            <button class=" mdui-btn mdui-ripple" mdui-dialog-close>
                cancel
            </button>
            <button class="mdui-btn mdui-ripple" mdui-dialog-confirm
                    v-on:click="onClickAdd"
                    v-bind:disabled="!valid">
                {{confirmButton}}
            </button>
        </div>
    </div>
</template>

<script src="../scripts/PasswordDialog.js">
</script>

<style scoped>
    .dialog-warn {
        padding-top: 12px;
        margin-left: 72px;
        -webkit-user-select: none;
        -moz-user-select: none;
        -ms-user-select: none;
        user-select: none;
    }

    .generate-button {
        margin-top: 40px;
    }

    .reveal-button {
        position: absolute;
        right: 8px;
        bottom: 8px;
    }

</style>