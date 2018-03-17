<template>
    <div>
        <div class="mdui-tab mdui-tab-full-width" mdui-tab>
            <a href="#create-password" class="mdui-ripple">create account</a>
            <a href="#sign-in" class="mdui-ripple">sign in</a>
        </div>

        <div id="create-password">
            <div class="mdui-textfield mdui-m-t-2">
                <label class="mdui-textfield-label">Enter Master
                    Password</label>
                <input class="mdui-textfield-input" type="password"
                       v-model="password"/>
            </div>

            <div class="mdui-textfield mdui-m-t-2"
                 v-bind:class="{'mdui-textfield-invalid': !validPassword}">
                <label class="mdui-textfield-label">Confirm Master
                    Password</label>
                <input class="mdui-textfield-input" type="password"
                       v-model="confirmPassword"/>
                <div class="mdui-textfield-error">
                    Two passwords are not the same!
                </div>
            </div>

            <button class="mdui-btn mdui-btn-raised mdui-ripple mdui-color-theme-accent confirm-button"
                    v-bind:disabled="confirmPassword === '' || !validPassword"
                    v-on:click="onAddMasterPassword">
                Set Master Password
            </button>
        </div>
        <div id="sign-in">
            <div class="mdui-textfield mdui-m-t-2">
                <label class="mdui-textfield-label">Ethereum Account</label>
                <input class="mdui-textfield-input"
                       v-model="account"/>
            </div>

            <div class="mdui-textfield mdui-m-t-2">
                <label class="mdui-textfield-label">Master Password</label>
                <input class="mdui-textfield-input" type="password"
                       v-model="password"/>
            </div>

            <button class="mdui-btn mdui-btn-raised mdui-ripple mdui-color-theme-accent confirm-button"
                    v-on:click="onVerifyWithAccount"
                    v-bind:disabled="verifying">
                Confirm
            </button>
            <div class="mdui-spinner confirm-spinner"
                 v-if="verifying"></div>
        </div>
    </div>
</template>

<script src="../scripts/NewPasswordView.js">
</script>

<style scoped>
    .confirm-button, .confirm-spinner {
        top: 304px;
        position: absolute;
    }

    .confirm-spinner {
        left: 160px;
    }

</style>