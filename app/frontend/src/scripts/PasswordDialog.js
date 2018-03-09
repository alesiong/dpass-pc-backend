import mdui from 'mdui'
import {randPassword} from '../utils';

export default {
  name: 'password-dialog',
  props: ['initUrl', 'initSiteName', 'initUserId', 'initTitle'],
  data() {
    return {
      url: this.initUrl || '',
      siteName: this.initSiteName || '',
      userId: this.initUserId || '',
      password: '',
      title: this.initTitle || 'Enter New Password',
      id: `password-dialog-${this._uid}`
    };
  },
  computed: {
    valid() {
      return this.url !== '' && this.userId !== '' && this.password !== '' && this.siteName !== '';
    }
  },
  methods: {
    openDialog(options) {
      options = Object.assign({modal: true}, options);
      new mdui.Dialog('#' + this.id, options).open();
    },
    onClickAdd() {
      this.$emit('click-add', {
        url: this.url,
        siteName: this.siteName,
        userId: this.userId,
        password: this.password
      });
      this.url='';this.siteName='';this.userId='';this.password='';
    },
    generateRandomPassword(){
      this.password=randPassword();
    }
  }
};