import {encryptAndAuthenticate} from '../utils';
import mdui from 'mdui';

export default {
  name: 'main-view',
  methods: {
    addPassword: function() {
      mdui.prompt('Enter master password:', this.onAdd.bind(this),
          () => {
          }, {
            modal: true,
            histroy: false // TODO: remember to add this, or vue's router may fail
          });
    },
    verifyPassword: function() {
      mdui.prompt('Verify master password:', this.onVerify.bind(this),
          () => {
          }, {
            modal: true,
            histroy: false
          });
    },
    onAdd: function(value) {
      const [cipher, hmac] = encryptAndAuthenticate(value, this.globalData.sessionKey);
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
          mdui.alert('Master Password Set');
        },
        statusCode: {
          '401': () => {
            mdui.alert('Session Key broken!');
          }
        }
      });
    },
    onVerify: function(value) {
      const [cipher, hmac] = encryptAndAuthenticate(value, this.globalData.sessionKey);
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
          mdui.alert('Master Password Verified');
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