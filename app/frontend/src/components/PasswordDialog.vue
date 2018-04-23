<template>
    <div v-if = "type==='password'"
         class="mdui-dialog" v-bind:id="id">
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
                <div class="mdui-col-xs-12">
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

            </div>
            <!--<div class="mdui">-->
            <div class="mdui-row option" >
                <div class="mdui-col-xs-3 sub-checkbox">
                    <label class="mdui-checkbox">
                        <input type="checkbox"
                               v-model:value="customizedOption.uppercase"/>
                        <i class="mdui-checkbox-icon"></i>
                        Upper Case
                    </label>
                </div>
                <div class="mdui-col-xs-3 sub-checkbox">
                    <label class="mdui-checkbox">
                        <input type="checkbox"
                               v-model:value="customizedOption.lowercase"/>
                        <i class="mdui-checkbox-icon"></i>
                        Lower Case
                    </label>
                </div>
                <div class="mdui-col-xs-4 password-length">Password Length : {{customizedOption.length}}</div>
                <div class="mdui-col-xs-2 sub-slide">
                    <label class="mdui-slider mdui-slider-discrete">
                        <input type="range" step="1" min="4" max="20"
                               v-model:value="customizedOption.length"/>
                    </label>
                </div>
                <div class="mdui-col-xs-2">
                    <button class="mdui-btn mdui-ripple generate-button"
                            mdui-tooltip="{content: 'Generate a Random Complicated Key in 4-20 Digits', position: 'top'}"
                            v-on:click="generateRandomPassword">
                        <!--<i class="mdui-icon mdui-icon-left material-icons ">autorenew</i>-->
                        generate
                    </button>
                </div>
            </div>
            <div class="mdui-row option2" >
                <div class="mdui-col-xs-3 sub-checkbox">
                <label class="mdui-checkbox">
                    <input type="checkbox"
                           v-model:value="customizedOption.digits"/>
                    <i class="mdui-checkbox-icon"></i>
                    Digits
                </label>
                </div>
                <div class="mdui-col-xs-3 sub-checkbox">
                <label class="mdui-checkbox">
                    <input type="checkbox"
                           v-model:value="customizedOption.symbols"/>
                    <i class="mdui-checkbox-icon"></i>
                    Symbols
                </label>
                </div>
                <div class="mdui-col-xs-5">
                <label class="mdui-checkbox">
                    <input type="checkbox"
                           v-model:value="customizedOption.obscureSymbols"/>
                    <i class="mdui-checkbox-icon"></i>
                    Obscure Symbols
                </label>
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
    <div v-else-if = "type==='secret'"
         class="mdui-dialog" v-bind:id="id">
        <div class="mdui-dialog-title">{{ title }}</div>

        <div class="mdui-dialog-content">
            <div class="mdui-textfield">
                <i class="mdui-icon material-icons">note_add</i>
                <label class="mdui-textfield-label">Name</label>
                <input class="mdui-textfield-input"
                       type="text"
                       autocomplete="off"
                       v-model="name"/>
            </div>



            <div class="mdui-textfield">
                <i class="mdui-icon material-icons sub-icon">account_circle</i>
                <label class="mdui-textfield-label">Secret Note</label>
                <textarea class="mdui-textfield-input"
                       type="text"
                       rows="12"
                       autocomplete="off"
                          v-model="password"></textarea>
            </div>


            <!--<div class="mdui">-->


        </div>
        <div class="mdui-dialog-actions">
                <span class="mdui-float-left dialog-warn mdui-text-color-red-a400"
                      v-if="!validSecret">
                    <i class="mdui-icon material-icons"
                       style="margin-top: -4px;">error_outline</i>
                    All entries should be filled.
                </span>

            <button class=" mdui-btn mdui-ripple" mdui-dialog-close>
                cancel
            </button>
            <button class="mdui-btn mdui-ripple" mdui-dialog-confirm
                    v-on:click="onClickAddSecret"
                    v-bind:disabled="!validSecret">
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
        margin-top: 0px;
    }

    .reveal-button {
        position: absolute;
        right: 8px;
        bottom: 8px;
    }
    .option{
        margin-top: 20px;
        margin-left: 43px;
    }
    .option2{
        margin-left: 43px;
    }
    .password-length{
        width:162px;
        margin-top: 7px;
        margin-left: 0px;
        padding-right: 0px;
        /*bottom:4px;*/
    }
    .sub-checkbox{
        width:131px;
    }
    .sub-slide{
        padding-left: 0px;
        margin-bottom: 2px;
    }
    .sub-icon{
        margin-bottom:224px;
    }

</style>