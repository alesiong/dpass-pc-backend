import {encryptAndAuthenticate, ensureSession} from '@/utils';
import mdui from 'mdui';
import NewPasswordView from '@c/NewPasswordView';

export default {
  name: 'guard-view',
  props: ['state', 'verify'],
  data() {
    return {
      password: '',
      verifying: false
    };
  },
  components: {
    NewPasswordView
  },
  updated() {
    mdui.mutation();
  },
  methods: {
    onAddMasterPassword(password) {
      ensureSession(this).then(() => {
        const [cipher, hmac] = encryptAndAuthenticate(password, this.globalData.sessionKey);
        $$.ajax({
          url: '/api/master_password/new/',
          method: 'POST',
          dataType: 'json',
          data: JSON.stringify({
            data: cipher,
            hmac: hmac
          }),
          contentType: 'application/json',
          success: () => {
            this.$emit('added-password');
          },
          statusCode: {
            '401': () => {
              // Fixme: general bad situation
              mdui.alert('Session Key broken!');
            }
          }
        });
      });
    },
    warnClose() {
      new mdui.Dialog('#warn').close();
    },
    onVerifyMasterPassword() {
      ensureSession(this).then(() => {
        const [cipher, hmac] = encryptAndAuthenticate(this.password, this.globalData.sessionKey);
        $$.ajax({
          url: '/api/master_password/verify/',
          method: 'POST',
          dataType: 'json',
          data: JSON.stringify({
            data: cipher,
            hmac: hmac
          }),
          contentType: 'application/json',
          success: () => {
            this.$emit('verified-password');
            this.password = '';
          },
          statusCode: {
            '401': (res) => {
              res = JSON.parse(res.response);
              if (res.error === 'Master Password Wrong') {
                // mdui.Dialog('#warn').open();
                mdui.snackbar({
                  message: 'Verification Failed'
                });
              } else {
                // Fixme: general bad situation
                // mdui.alert('Session Key broken!');
                mdui.snackbar({
                  message: 'Session Key broken'
                });
              }
            }
          }
        });
      });
    },
    onVerifyWithAccount(account, password) {
      this.verifying = true;
      ensureSession(this).then(() => {
        const [cipher, hmac] = encryptAndAuthenticate(JSON.stringify(
            {
              password,
              account
            }
        ), this.globalData.sessionKey);
        $$.ajax({
          url: '/api/master_password/verify_with_account/',
          method: 'POST',
          dataType: 'json',
          data: JSON.stringify({
            data: cipher,
            hmac: hmac
          }),
          contentType: 'application/json',
          success: () => {
            this.$emit('verified-with-account');
          },
          statusCode: {
            '400': () => {
              mdui.alert('Blockchain Account Wrong!');
            },
            '401': (res) => {
              res = JSON.parse(res.response);
              if (res.error === 'Master Password Wrong') {
                mdui.alert('Verification failed');
              } else {
                // Fixme: general bad situation
                mdui.alert('Session Key broken!');
              }
            }
          },
          complete: () => {
            this.verifying = false;
          }
        });
      });
    }
  }
};