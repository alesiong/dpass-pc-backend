import {encryptAndAuthenticate, ensureSession} from '@/utils';
import mdui from 'mdui';

export default {
  name: 'guard-view',
  props: ['state', 'verify'],
  data() {
    return {
      password: '',
      confirmPassword: ''
    };
  },
  computed: {
    validPassword() {
      return this.confirmPassword === '' ||
          (this.password === this.confirmPassword);
    }
  },
  updated() {
    mdui.mutation();
  },
  methods: {
    onAddMasterPassword() {
      ensureSession(this).then(() => {
        const [cipher, hmac] = encryptAndAuthenticate(this.password,
            this.globalData.sessionKey);
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
            this.password = '';
            this.confirmPassword = '';
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
        console.log(this.globalData.sessionKey);
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
    }
  }
};