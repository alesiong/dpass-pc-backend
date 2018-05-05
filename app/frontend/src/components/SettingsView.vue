<template>
    <div class="mdui-row">
        <div class="mdui-col-xs-4">
            <div class="mdui-card">

                <!-- 卡片头部，包含头像、标题、副标题 -->
                <div class="mdui-card-header">
                    <div class="mdui-card-header-title sychronize-font">Sychronization </div>
                    <div class="mdui-card-header-subtitles sychronize-font2">Scan QR-code below on your phone</div>
                </div>


                <div class="mdui-card-media">
                    <img v-bind:src="'/api/settings/private_key.png?q=' + Date.now()"/>

                    <!-- 卡片中可以包含一个或多个菜单按钮 -->
                </div>
                <div class="mdui-card-content mdui-typo qr-content">
                    <p class="qr-content2">Or copy the content:</p>
                    <p>{{this.account}}</p>
                </div>

                <!-- 卡片的标题和副标题 -->
                <div class="mdui-card-primary balance-position">
                    <div class="mdui-card-primary-title balance-title-font mdui-center">Balance</div>
                    <div class="mdui-card-primary-subtitle balance-font mdui-center">{{balance !== null ? balanceHuman : ''}}</div>
                </div>


                <!-- 卡片的按钮 -->
                <div class="mdui-card-actions">
                    <button class="mdui-center mdui-btn mdui-btn-raised mdui-ripple mdui-color-theme-accent mining-btn"
                            v-if="typeof(isMining) === 'boolean'"
                            @click="toggleMining">
                        {{isMining ? 'Stop Mining' : 'Start Mining'}}
                    </button>
                </div>

            </div>
        </div>

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
        balance: null,
        account:null
      };
    },
    mounted() {
      this.fetchMining();
      this.fetchBalance();
      this.fetchAccount();
    },
    computed: {
      balanceHuman() {
        return filesize(this.balance / 8);
      },
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
      },
      fetchAccount() {
        $$.ajax({
          url: '/api/settings/?type=account',
          dataType: 'json',
          success: (res) => {
            this.account = res.account;
          }
        });
      }
    }
  };
</script>

<style scoped>
    .sychronize-font{
        margin-left: 12px;
    }
    .sychronize-font2{
        font-weight: 300;
        margin-left: 12px;
    }

    .balance-title-font {
        text-align:center;
        font-size: 28px;
        font-weight: 300;
        padding-bottom: 12px;
    }

    .balance-font {
        text-align:center;
        font-weight: 300;
        font-size: 33px;
    }
    . balance-position{
        padding-top:0px;
    }
    .mining-btn{
        margin-bottom:16px;
    }
    .qr-content{
        padding-left: 30px;
        padding-right:30px;
        padding-bottom:0px;
    }
    .qr-content2{
        font-weight: 300;
    }

</style>