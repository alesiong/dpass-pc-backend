import {encryptAndAuthenticate} from '@/utils';
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
    },
    onVerifyMasterPassword() {
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
          '401': () => {
            mdui.alert('Verification failed or Session Key broken!');
          }
        }
      });
    }
  }
};