import ModifyDialog from '@c/ModifyDialog';
import Item from '@c/Item';
import mdui from 'mdui';

import {copyToClickboard, decrypt} from '@/utils';

export default {
  name: 'item',
  props: ['type', 'data', 'search'],
  components: {
    ModifyDialog,
    Item,
  },
  data() {
    return {
      showPlain: false,
      items:[]
    };
  },
  filters: {
    formatDate(timestamp) {
      const date = new Date(timestamp);
      return date.getFullYear() + '/' + (date.getMonth() + 1) + '/' +
          date.getDate();
    },
      mduiTooltip(content) {
          return `{content: '${content}', position: 'left'}`;
      }
  },
  methods: {
    onToggleReveal() {
      this.showPlain = !this.showPlain;
    },
    getPassword(key) {
      return decrypt(this.$parent.localData.passwords[key], key);
    },
    onCopyPassword(key) {
      const password = decrypt(this.$parent.localData.passwords[key], key);
      if (!copyToClickboard(password)) {
        mdui.snackbar({message: 'Failed to copy the password'});
        return;
      }
      mdui.snackbar({message: 'Password copied to clipboard, and will be cleared in 1 minute'});

      this.$emit('copy-success');

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
                      mdui.snackbar({message: 'Successfully added password'});
                      this.fetchPasswords();
                  }
              });
          });
      },
      onRevise() {
          this.$refs.dialog.openDialog();
      },

      onRevise() {
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