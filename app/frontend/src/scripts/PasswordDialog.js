import mdui from 'mdui';
import {randPassword} from '../utils';

export default {
  name: 'password-dialog',
  data() {
    return {
      url: '',
      siteName: '',
      userId: '',
      password: '',
      title: '',
      confirmButton: '',
      id: `password-dialog-${this._uid}`,
      showPlain: false,
      customizedOption: {
        length: 8,
        uppercase: true,
        lowercase: true,
        digits: true,
        symbols: false,
        obscureSymbols: false,
        extra: ''
      }
    };
  },
  updated() {
    mdui.mutation();
  },
  computed: {
    valid() {
      return this.url !== '' && this.userId !== '' && this.password !== '' && this.siteName !== '';
    }
  },
  methods: {
    openDialog(initValue, mode = 'add', options) {
      options = Object.assign({modal: true}, options);
      initValue = initValue || {};
      this.url = initValue.url || '';
      this.siteName = initValue.siteName || '';
      this.userId = initValue.userId || '';
      this.password = initValue.password || '';
      if (mode === 'add') {
        this.title = 'Enter New Password';
        this.confirmButton = 'Add';
      } else {
        this.title = 'Modify Password';
        this.confirmButton = 'Modify';
        this.origin = initValue;
        this.key = initValue.key;
      }
      this.mode = mode;
      this.showPlain = false;
      this.dialog = new mdui.Dialog('#' + this.id, options);
      this.dialog.open();
      $$('#' + this.id).on('opened.mdui.dialog', () => {
        this.dialog.handleUpdate();
      });
    },
    onClickAdd() {
      if (this.mode === 'add') {
        this.$emit('click-add', {
          url: this.url,
          siteName: this.siteName,
          userId: this.userId,
          password: this.password,
          type: 'password'
        });
      } else {
        const data = {};
        if (this.url !== this.origin.url) data.url = this.url;
        if (this.siteName !== this.origin.siteName) data.siteName = this.siteName;
        if (this.userId !== this.origin.userId) data.userId = this.userId;
        if (this.password !== this.origin.password) data.password = this.password;

        if (Object.keys(data).length > 0) {
          data.key = this.key;
          this.$emit('click-modify', data);
        }

      }
      this.password = '';
    },
    generateRandomPassword() {
      this.password = randPassword(this.customizedOption);
    }
  }
};