<!-- This view is used to create/verify the master password-->

<template>
    <!--Set the password-->
    <new-password-view
            v-if="state === 0"
            v-on:add-master-password="onAddMasterPassword"
            v-on:verify-with-account="onVerifyWithAccount"
            v-bind:verifying="verifying"/>

    <!--Loading-->
    <div v-else-if="state === 1">
        <p>Initializing</p>
        <div class="mdui-progress">
            <div class="mdui-progress-indeterminate"></div>
        </div>
    </div>
    <!--Verify the password-->
    <div v-else-if="verify">
        <div class="mdui-textfield " @keyup.13="onVerifyMasterPassword">
            <label class="mdui-textfield-label">Enter Master Password</label>
            <input class="mdui-textfield-input" type="password"
                   v-model="password"/>
        </div>
        <button class="mdui-btn mdui-btn-raised mdui-ripple mdui-color-theme-accent"
                v-on:click="onVerifyMasterPassword">
            Unlock DPass
        </button>
    </div>
    <div v-else></div>
</template>

<script src="../scripts/GuardView.js">
</script>

<style scoped>

</style>