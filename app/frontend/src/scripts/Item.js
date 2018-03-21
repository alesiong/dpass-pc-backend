import mdui from 'mdui';

import {copyToClickboard, decrypt, encryptAndAuthenticate} from '@/utils';

export default {
  name: 'item',
  props: ['type', 'data'],
  data() {
    return {
      showPlain: false,
      persistence: null
    };
  },

  mounted() {
    this.persistenceWorker = window.setTimeout(this.persistenceWorkerFunction.bind(this), 1000);
  },
  beforeDestroy() {
    window.clearTimeout(this.persistenceWorker);
  },

  updated() {
    mdui.mutation();
  },
  filters: {
    formatDate(timestamp) {
      const date = new Date(timestamp);
      return date.getFullYear() + '/' + (date.getMonth() + 1) + '/' +
          date.getDate();
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
    onDelete() {
      mdui.confirm('Deleting password from blockchain will cost storage space!', 'Do you really want to delete?',
          () => {
            this.$emit('click-delete', this.data.key);
          });
    },
    onHide() {
      this.$emit('click-hide', {
        key: this.data.key,
        hidden: !this.data.hidden
      });
    },
    onModify() {
      this.$emit('click-modify', this.data);
    },

    fetchPersistence(key) {
      return new Promise(resolve => {
        const [cipher, hmac] = encryptAndAuthenticate(
            JSON.stringify({
              key
            }),
            this.globalData.sessionKey);
        $$.ajax({
          url: '/api/password/persistent/',
          method: 'POST',
          dataType: 'json',
          data: JSON.stringify({
            data: cipher,
            hmac: hmac
          }),
          contentType: 'application/json',
          success: (res) => {
            resolve(res.result);
          }
        });
      });
    },

    async persistenceWorkerFunction() {
      this.persistence = await this.fetchPersistence(this.data.key);
      if (this.persistence) {
        window.setTimeout(this.persistenceWorkerFunction.bind(this), 5000);
      } else {
        window.setTimeout(this.persistenceWorkerFunction.bind(this), 1000);
      }
    }
  }
};