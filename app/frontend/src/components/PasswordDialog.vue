<template>
    <div class="mdui-dialog" v-bind:id="id">
        <div class="mdui-dialog-title">{{ title }}</div>

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
            </div>

            <div class="mdui-textfield">
                <i class="mdui-icon material-icons">vpn_key</i>
                <label class="mdui-textfield-label">Password</label>
                <input class="mdui-textfield-input" type="password"
                       v-model="password"/>
            </div>
        </div>
        <div class="mdui-dialog-actions">
                <span class="mdui-float-left dialog-warn mdui-text-color-red-a400"
                      v-if="!valid">
                    Warning: All entries should be filled.
                </span>
            <button class="mdui-btn mdui-ripple">
                <i class="mdui-icon mdui-icon-left material-icons">autorenew</i>
                generate key
            </button>
            <button class="mdui-btn mdui-ripple" mdui-dialog-close>
                cancel
            </button>
            <button class="mdui-btn mdui-ripple" mdui-dialog-confirm
                    v-on:click="onClickAdd"
                    v-bind:disabled="!valid">
                add
            </button>
        </div>
    </div>
</template>

<script src="../scripts/PasswordDialog.js">
</script>

<style scoped>
    .dialog-warn {
        padding-top: 16px;
        margin-left: 72px;
    }

</style>