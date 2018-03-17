import mdui from 'mdui';

export default {
  name: 'new-password-view',
  props: ['verifying'],
  data() {
    return {
      password: '',
      confirmPassword: '',
      account: ''
    };
  },
  computed: {
    validPassword() {
      return this.confirmPassword === '' ||
          (this.password === this.confirmPassword);
    }
  },
  updated() {
    mdui.mutation();
  },
  methods: {
    onAddMasterPassword() {
      this.$emit('add-master-password', this.password);
      this.password = '';
      this.confirmPassword = '';
      this.account = '';
    },
    onVerifyWithAccount() {
      this.$emit('verify-with-account', this.account, this.password);
    }
  }
};