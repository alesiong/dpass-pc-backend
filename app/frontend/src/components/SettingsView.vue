<template>
    <div>
        <button class="mdui-btn mdui-btn-raised mdui-ripple mdui-color-theme-accent"
                v-if="typeof(isMining) === 'boolean'"
                @click="toggleMining">
            {{isMining ? 'Stop Mining' : 'Start Mining'}}
        </button>
        <div>
            {{balance !== null ? balanceHuman : ''}}
        </div>
        <img v-bind:src="'/api/settings/private_key.png?q=' + Date.now()"
        />
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