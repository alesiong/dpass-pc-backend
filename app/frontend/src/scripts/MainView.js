import PasswordDialog from '@c/PasswordDialog';
import Item from '@c/Item';

import {decryptAndVerify, encrypt, encryptAndAuthenticate, ensureSession} from '@/utils';

import mdui from 'mdui';

export default {
  name: 'main-view',
  props: ['type', 'search'],
  components: {
    PasswordDialog,
    Item
  },
  data() {
    return {
      items: []
    };
  },
  mounted() {
    this.fetchPasswords();
    const fetchingInterval = window.setInterval(this.fetchPasswords.bind(this), 30000);
    this.localData = {
      fetchingInterval,
      clearClipboardTimeout: null,
      passwords: {}
    };
  },

  beforeDestroy() {
    window.clearInterval(this.localData.fetchingInterval);
  },

  computed: {
    length() {
      return this.items.filter(this.shown.bind(this)).length;
    },
    title() {
      switch (this.type) {
        case 'all':
          return 'All';
        case 'password':
          return 'Passwords';
        case 'secret':
          return 'Secret Notes';
      }
    },
    typeName() {
      switch (this.type) {
        case 'password':
          return 'Password';
        case 'secret':
          return 'Secret Note';
      }
    }
  },

  filters: {
    mduiToolbar(content) {
      return `{content: '${content}', position: 'left'}`;
    }
  },

  methods: {
   //  indexOf(val) {
   //  for (var i = 0; i < this.items.length; i++) {
   //    if (this.items[i] == val) return i;
   //  }
   //  return -1;
   //  },
   //  remove(val) {
   //  var index = this.items.indexOf(val);
   //  if (index > -1) {
   //    this.items.splice(index, 1);
   //  }
   // },
    onConfirmDelete(data) {
      ensureSession(this).then(() => {
        const passwordEntry = JSON.stringify(data);
        const [cipher, hmac] = encryptAndAuthenticate(passwordEntry, this.globalData.sessionKey);
        $$.ajax({
          url: '/api/password/delete/',
          method: 'POST',
          dataType: 'json',
          data: JSON.stringify({
            data: cipher,
            hmac: hmac
          }),
          contentType: 'application/json',
          success: () => {
            mdui.snackbar({message: 'Successfully deleted password'});
            this.fetchPasswords();
          }
        });
      });
    },
    // listeners
    onConfirmAddItem(data) {
      data.date = Date.now();
      data.url = this.processUrl(data.url);
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
            mdui.snackbar({message: 'Successfully deleted password'});
            this.fetchPasswords();
          }
        });
      });
    },
    onAddPassword() {
      this.$refs.dialog.openDialog();
    },
    onAddSecretNote() {

    },
    onToggleReveal: function(index) {
      const item = this.items[index];
      item.showPlain = !item.showPlain;
    },
    onAddPassword() {
      this.$refs.dialog.openDialog();
    },
    onCopiedPassword() {
      window.clearTimeout(this.localData.clearClipboardTimeout);
      this.localData.clearClipboardTimeout = window.setTimeout(() => {
        ensureSession(this).then(() => {
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
        });
      }, 60000);
    },

    // utils
    processUrl(url) {
      const urlWithProtocol = /^.*:\/\/.*$/g;
      if (!url.match(urlWithProtocol)) {
        return 'http://' + url;
      }
      return url;
    },

    fetchPassword(key, inSession = false) {
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
          }
        });
      };
      return new Promise(resolve => {
        if (inSession) {
          func(resolve);
        } else {
          ensureSession(this).then(func.bind(this, resolve));
        }
      });
    },

    shown(item) {
      const notHidden = !item.hidden;
      const type = this.type === 'all' ? true : item.type === this.type;
      // FIXME: these may not apply to secret notes
      const regexSearch = new RegExp(this.search, 'i');
      const matchSearch = item.siteName.match(regexSearch) || item.url.match(regexSearch);
      return notHidden && type && matchSearch;
    },

    // workers
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
                    hidden: false
                  },
                  p.metadata
              ));

              this.fetchPassword(p.key, true).then(password => {
                this.localData.passwords[p.key] = encrypt(password, p.key);
              });
            }
            this.items = newPasswords;
          }
        });
      });
    }
  }
};