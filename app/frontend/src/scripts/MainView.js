import PasswordDialog from '@c/PasswordDialog';
import Item from '@c/Item';

import {decrypt, decryptAndVerify, encrypt, encryptAndAuthenticate, ensureSession} from '@/utils';

import mdui from 'mdui';
import io from 'socket.io-client';

export default {
  name: 'main-view',
  props: ['type', 'search'],
  components: {
    PasswordDialog,
    Item
  },
  data() {
    return {
      items: [],
      sortBy: '1',
      showHidden: false
    };
  },
  mounted() {
    this.fetchPasswords();
    const fetchingInterval = window.setInterval(this.fetchPasswords.bind(this), 60000);
    this.localData = {
      fetchingInterval,
      clearClipboardTimeout: null,
      passwords: {},
      socket: io()
    };
    this.localData.socket.on('refresh password', this.fetchPasswords.bind(this));
  },

  beforeDestroy() {
    window.clearInterval(this.localData.fetchingInterval);
    this.localData.socket.close();
  },

  computed: {
    filteredItems() {
      function comparator(keyFuncs) {
        const cmp = (a, b) => a < b ? -1 : (a === b ? 0 : 1);
        return (a, b) => {
          const result = cmp(keyFuncs[0](a), keyFuncs[0](b));
          return result === 0 && keyFuncs.length > 1 ? comparator(keyFuncs.slice(1))(a, b) : result;
        };
      }

      let keys = [a => a.hidden];
      if (this.sortBy === '1') {
        keys.push(a => a.siteName);
      } else {
        keys.push(a => -a.date);
      }
      return this.items.filter(this.shown.bind(this)).sort(comparator(keys));
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
    mduiTooltip(content) {
      return `{content: '${content}', position: 'left'}`;
    }
  },

  methods: {
    // listeners
    onDeleteItem(key) {
      ensureSession(this).then(() => {
        const passwordEntry = JSON.stringify({key});
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
            mdui.snackbar({message: 'Successfully deleted one password'});
            this.fetchPasswords();
          }
        });
      });
    },
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
            mdui.snackbar({message: 'Successfully added one password'});
            this.fetchPasswords();
          }
        });
      });
    },
    onConfirmModifyItem(data) {
      data.date = Date.now();
      if (data.url) data.url = this.processUrl(data.url);
      ensureSession(this).then(() => {
        const key = data.key;
        delete data.key;
        const passwordEntry = JSON.stringify({
          key: key,
          modified: data
        });
        const [cipher, hmac] = encryptAndAuthenticate(passwordEntry, this.globalData.sessionKey);
        $$.ajax({
          url: '/api/password/modify/',
          method: 'POST',
          dataType: 'json',
          data: JSON.stringify({
            data: cipher,
            hmac: hmac
          }),
          contentType: 'application/json',
          success: () => {
            mdui.snackbar({message: 'Successfully modified one password'});
            this.fetchPasswords();
          }
        });
      });
    },
    onHideItem(data) {
      data = Object.assign({hidden: true}, data);
      ensureSession(this).then(() => {
        const passwordEntry = JSON.stringify(data);
        const [cipher, hmac] = encryptAndAuthenticate(passwordEntry, this.globalData.sessionKey);
        $$.ajax({
          url: '/api/password/mark/',
          method: 'POST',
          dataType: 'json',
          data: JSON.stringify({
            data: cipher,
            hmac: hmac
          }),
          contentType: 'application/json',
          success: () => {
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
    onModifyItem(data) {
      data.password = decrypt(this.localData.passwords[data.key], data.key);
      this.$refs.dialog.openDialog(data, 'modify');
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
      const notHidden = this.showHidden || !item.hidden;
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
          url: '/api/password/?hidden=1',
          dataType: 'json',
          success: (res) => {
            let passwords = decryptAndVerify(res.data, res.hmac, this.globalData.sessionKey);
            passwords = JSON.parse(passwords);
            const newPasswords = [];
            for (const p of passwords) {
              newPasswords.push(Object.assign({
                    key: p.key,
                    hidden: p.hidden
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