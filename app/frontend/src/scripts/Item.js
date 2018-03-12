import mdui from 'mdui';

import {copyToClickboard, decrypt} from '@/utils';

export default {
  name: 'item',
  props: ['type', 'data'],
  data() {
    return {
      showPlain: false
    };
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
      console.log(this.$parent.passwords);
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

    }
  }
};