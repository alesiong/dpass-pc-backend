import mdui from 'mdui';

import {copyToClickboard, decrypt, encryptAndAuthenticate} from '@/utils';
import io from 'socket.io-client';

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
    this.fetchPersistence();
    this.socket = io();
    this.socket.on('persistence change', async (key) => {
      if (key === this.data.key) {
        this.fetchPersistence();
      }
    });
  },
  beforeDestroy() {
    // window.clearTimeout(this.persistenceWorker);
    this.socket.close();
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
      $$('.mdui-tooltip-open').removeClass('mdui-tooltip-open');
      this.$emit('click-hide', {
        key: this.data.key,
        hidden: !this.data.hidden
      });
    },
    onModify() {
      this.$emit('click-modify', this.data);
    },

    fetchPersistence() {
      const [cipher, hmac] = encryptAndAuthenticate(
          JSON.stringify({
            key: this.data.key
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
          this.persistence = res.result;
        }
      });
    }
  }
};