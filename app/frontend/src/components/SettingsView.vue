<template>
    <div>
        <div class="mdui-row">
            <div class="mdui-col-xs-3">
                <span class="mdui-typo-title"> Balance </span>
                <span class="mdui-typo-subheading">{{balance !== null ? balanceHuman : ''}}</span>
            </div>
            <button class="mdui-col-xs-2 mdui-btn mdui-btn-raised mdui-ripple mdui-color-theme-accent"
                    v-if="typeof(isMining) === 'boolean'"
                    @click="toggleMining">
                {{isMining ? 'Stop Mining' : 'Start Mining'}}
            </button>
        </div>
        <div class="mdui-row">
            <span class="mdui-typo-title"> Scan the QR code on your phone </span>
        </div>
        <img class="mdui-row"
             v-bind:src="'/api/settings/private_key.png?q=' + Date.now()"/>
    </div>
</template>

<script>
  import {encryptAndAuthenticate, ensureSession} from '@/utils';
  import * as filesize from 'filesize';

  export default {
    name: 'settings-view',
    data() {
      return {
        isMining: null,
        balance: null
      };
    },
    mounted() {
      this.fetchMining();
      this.fetchBalance();
    },
    computed: {
      balanceHuman() {
        return filesize(this.balance / 8);
      }
    },
    methods: {
      toggleMining() {
        ensureSession(this).then(() => {
          const [cipher, hmac] = encryptAndAuthenticate(
              JSON.stringify({
                type: 'mining',
                args: !this.isMining
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
              this.fetchMining();
            }
          });
        });
      },
      fetchMining() {
        $$.ajax({
          url: '/api/settings/?type=mining',
          dataType: 'json',
          success: (res) => {
            this.isMining = res.mining;
          }
        });
      },
      fetchBalance() {
        $$.ajax({
          url: '/api/settings/?type=balance',
          dataType: 'json',
          success: (res) => {
            this.balance = res.balance;
          }
        });
      }
    }
  };
</script>

<style scoped>

</style>