<template>
    <div>
        <button class="mdui-btn mdui-btn-raised mdui-ripple mdui-color-theme-accent"
                v-if="typeof(isMining) === 'boolean'"
                @click="toggleMining">
            {{isMining ? 'Stop Mining' : 'Start Mining'}}
        </button>
    </div>
</template>

<script>
  import {encryptAndAuthenticate, ensureSession} from '@/utils';

  export default {
    name: 'settings-view',
    data() {
      return {
        isMining: null
      };
    },
    mounted() {
      this.fetchMining();
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
      }
    }
  };
</script>

<style scoped>

</style>