<template>
    <header class="mdui-appbar mdui-appbar-fixed mdui-color-theme-900">
        <div class="mdui-toolbar">
                <span class="mdui-btn mdui-btn-icon mdui-ripple mdui-ripple-white"
                      mdui-drawer="{target: '#left-drawer'}">
                    <i class="mdui-icon material-icons">menu</i>
                </span>

            <!--TODO: icon-->
            <a class="mdui-typo-title mdui-text-color-theme-grey-50">DPass</a>

        <div class="mdui-toolbar-spacer"></div>
            <div class="mdui-textfield search-bar"
                v-if="!guard">
                <i class="mdui-icon material-icons">search</i>
                <input class="mdui-textfield-input search-text" type="text"
                    placeholder="Search"
                    v-model="message"
                    v-on:input="onSearchChanged"/>
            </div>

            <span class="mdui-btn mdui-btn-icon mdui-ripple"
                  mdui-tooltip="{content: 'erase'}"
                  v-if="!guard"
                  v-on:click="offSearchChanged">
                <i class="mdui-icon material-icons">close</i>
            </span>

            <span class="mdui-btn mdui-btn-icon mdui-ripple"
                  mdui-tooltip="{content: 'Lock DPass'}"
                  v-if="!guard"
                  @click="lockDPass">
                <i class="mdui-icon material-icons">lock</i>
            </span>
        </div>
    </header>
</template>


<script>
  import {encryptAndAuthenticate, ensureSession} from '@/utils';

  export default {
    name: 'app-header',
    props: ['guard'],
    data() {
      return {
        message:''
      };
    },
    methods: {
      onSearchChanged(event) {
        this.$emit('search', event.target.value);
      },
      offSearchChanged:function() {
        this.$emit('search', '');
        this.message='';
      },
      lockDPass() {
        $$('.mdui-tooltip-open').remove();
        ensureSession(this).then(() => {
          const [cipher, hmac] = encryptAndAuthenticate(
              JSON.stringify({
                type: 'lock'
              }),
              this.globalData.sessionKey);
          $$.ajax({
            url: '/api/settings/',
            method: 'POST',
            dataType: 'json',
            data: JSON.stringify({
              data: cipher,
              hmac: hmac
            }),
            contentType: 'application/json',
            success: () => {
              this.$parent.verifyPassword();
            }
          });
        });
      }
    }
  };
</script>

<style scoped>
    .search-text {
        color: white;
        background: rgba(255, 255, 255, 0.2);
    }

    .search-bar {
        margin-right: 24px;
        width: calc(100% - 400px);
    }
</style>