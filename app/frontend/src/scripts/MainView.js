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
      items: [],
      passwords: {}
    };
  },
  mounted() {
  },
  created() {
    this.fetchPasswords();
    window.setInterval(this.fetchPasswords.bind(this), 30000);
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

            this.getPassword(p.key, (password) => {
              this.passwords[p.key] = encrypt(password, p.key);
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
    },
    formatDate(timestamp) {
      // FIXME: local time string
      const date = new Date(timestamp);
      return date.getFullYear() + '/' + (date.getMonth() + 1) + '/' + date.getDate();
    },
    showToggle: function() {
      this.isShow = !this.isShow;
      if (this.isShow) {
        this.message = '12345678';
        this.btnText = 'HIDE';
      } else {
        this.message = '********';
        this.btnText = 'REVEAL';
      }
    },
    onAddPassword() {
      this.$refs.dialog.openDialog();
    },

    copyPassword(key) {
      window.encrypt = encrypt;
      window.decrypt = decrypt;
      const password = decrypt(this.passwords[key], key);
      copyToClickboard(password);
      mdui.snackbar({message: 'Password copied to clipboard, and will be cleared in 1 minute'});
      // TODO: only clear clipboard once if copy more
      window.setTimeout(() => {
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
    getPassword(key, cb) {
      ensureSession(this).then(() => {
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
            cb(entry.password);
          },
          statusCode: {
            '401': () => {
              // FIXME: this may disturb user (e.g. user may be inputting the passwords)
              this.$parent.verifyPassword();
            }
          }
        });
      });
    }
  }
};