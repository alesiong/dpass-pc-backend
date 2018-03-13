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
      title: 'Enter New Password',
      id: `password-dialog-${this._uid}`
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
    openDialog(options, initValue) {
      options = Object.assign({modal: true}, options);
      if (initValue) {
        this.url = initValue.url || '';
        this.siteName = initValue.siteName || '';
        this.userId = initValue.userId || '';
        this.password = initValue.password || '';
      }
      new mdui.Dialog('#' + this.id, options).open();
    },
    onClickAdd() {
      this.$emit('click-add', {
        url: this.url,
        siteName: this.siteName,
        userId: this.userId,
        password: this.password,
        type: 'password'
      });
      this.password = '';
    },
    generateRandomPassword() {
      this.password = randPassword();
    }
  }
};