<!-- This view is used to create/verify the master password-->

<template>
    <!--Verify the password-->
    <div v-if="verify">
        <div class="mdui-textfield">
            <label class="mdui-textfield-label">Enter Master Password</label>
            <input class="mdui-textfield-input" type="password"
                   v-model="password"/>
        </div>
        <button class="mdui-btn mdui-btn-raised mdui-ripple mdui-color-theme-accent"
                v-on:click="onVerifyMasterPassword">
            Unlock DPass
        </button>
    </div>

    <!--Set the password-->
    <div v-else-if="state === 0">
        <div class="mdui-textfield">
            <label class="mdui-textfield-label">Enter Master Password</label>
            <input class="mdui-textfield-input" type="password"
                   v-model="password"/>
        </div>

        <div class="mdui-textfield"
             v-bind:class="{'mdui-textfield-invalid': !validPassword}">
            <label class="mdui-textfield-label">Confirm Master Password</label>
            <input class="mdui-textfield-input" type="password"
                   v-model="confirmPassword"/>
            <div class="mdui-textfield-error">
                Two passwords are not the same!
            </div>
        </div>

        <!--FIXME: seems to need clicking the button twice (fix the position)-->
        <button class="mdui-btn mdui-btn-raised mdui-ripple mdui-color-theme-accent"
                v-bind:disabled="confirmPassword === '' || !validPassword"
                v-on:click="onAddMasterPassword">
            Set Master Password
        </button>
    </div>

    <!--Loading-->
    <div v-else>
        <span>Initializing</span>
        <div class="mdui-spinner mdui-text-color-theme"></div>
    </div>
</template>

<script src="../scripts/GuardView.js">
</script>

<style scoped>

</style>