import PasswordDialog from '@c/PasswordDialog';
import {copyToClickboard, decrypt, decryptAndVerify, encrypt, encryptAndAuthenticate, ensureSession} from '@/utils';

import mdui from 'mdui';

export default {
  name: 'main-view',
  components: {
    PasswordDialog
  },
  data() {
    return {
      items: []
    };
  },
  mounted() {
    console.log('mounted');
    this.fetchPasswords();
    const fetchingInterval = window.setInterval(this.fetchPasswords.bind(this), 30000);
    this.localData = {
      fetchingInterval,
      clearClipboardTimeout: null,
      passwords: {}
    };
  },

  beforeDestroy() {
    console.log('destroying');
    window.clearInterval(this.localData.fetchingInterval);
  },

  methods: {
    addItem(data) {
      data.date = Date.now();
      ensureSession(this).then(() => {
        const passwordEntry = JSON.stringify(data);
        const [cipher, hmac] = encryptAndAuthenticate(passwordEntry, this.globalData.sessionKey);
        $$.ajax({
          url: '/api/password/new/',
          method: 'POST',
          dataType: 'json',
          data: JSON.stringify({
            data: cipher,
            hmac: hmac
          }),
          contentType: 'application/json',
          success: () => {
            mdui.snackbar({message: 'Successfully added password'});
            this.fetchPasswords();
          },
          statusCode: {
            '401': () => {
              // FIXME: this may disturb user (e.g. user may just submit the password)
              this.$parent.verifyPassword();
            }
          }
        });
      });
    },
    onAddPassword() {
      this.$refs.dialog.openDialog();
    },
    fetchPasswords() {
      ensureSession(this).then(() => {
        $$.ajax({
          url: '/api/password/',
          dataType: 'json',
          success: (res) => {
            let passwords = decryptAndVerify(res.data, res.hmac, this.globalData.sessionKey);
            passwords = JSON.parse(passwords);
            const newPasswords = [];
            for (const p of passwords) {
              newPasswords.push(Object.assign({
                    key: p.key,
                    hide: false,
                    isShow: false
                  },
                  p.metadata
              ));

              this.getPassword(p.key, true).then(password => {
                this.localData.passwords[p.key] = encrypt(password, p.key);
              });
            }
            this.items = newPasswords;
          },
          statusCode: {
            '401': () => {
              // FIXME: this may disturb user (e.g. user may be inputting the passwords)
              this.$parent.verifyPassword();
            }
          }
        });
      });
    },
    formatDate(timestamp) {
      const date = new Date(timestamp);
      return date.getFullYear() + '/' + (date.getMonth() + 1) + '/' + date.getDate();
    },
    showToggle: function(index) {
      const item = this.items[index];
      item.isShow = !item.isShow;
      this.isShow = !this.isShow;
    },
    onAddPassword() {
      this.$refs.dialog.openDialog();
    },
    getPass(key) {
      return decrypt(this.localData.passwords[key], key);
    },

    copyPassword(key) {
      const password = decrypt(this.localData.passwords[key], key);
      if (!copyToClickboard(password)) {
        mdui.snackbar({message: 'Failed to copy the password'});
        return;
      }
      mdui.snackbar({message: 'Password copied to clipboard, and will be cleared in 1 minute'});

      window.clearTimeout(this.localData.clearClipboardTimeout);
      this.localData.clearClipboardTimeout = window.setTimeout(() => {
        const [cipher, hmac] = encryptAndAuthenticate('clear', this.globalData.sessionKey);
        $$.ajax({
          url: '/api/clear_clipboard/',
          method: 'POST',
          data: JSON.stringify({
            data: cipher,
            hmac: hmac
          }),
          contentType: 'application/json'
        });
      }, 60000);
    },
    getPassword(key, inSesion = false) {
      const func = resolve => {
        const [cipher, hmac] = encryptAndAuthenticate(
            JSON.stringify({
              key
            }),
            this.globalData.sessionKey);
        $$.ajax({
          url: '/api/password/get/',
          method: 'POST',
          dataType: 'json',
          data: JSON.stringify({
            data: cipher,
            hmac: hmac
          }),
          contentType: 'application/json',
          success: (res) => {
            let entry = decryptAndVerify(res.data, res.hmac, this.globalData.sessionKey);
            entry = JSON.parse(entry);
            resolve(entry.password);
          },
          statusCode: {
            '401': () => {
              // FIXME: this may disturb user (e.g. user may be inputting the passwords)
              this.$parent.verifyPassword();
            }
          }
        });
      };
      return new Promise(resolve => {
        if (inSesion) {
          func(resolve);
        } else {
          ensureSession(this).then(func.bind(this, resolve));
        }
      });
    }
  }
};