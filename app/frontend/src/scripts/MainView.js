import PasswordDialog from '@c/PasswordDialog';

export default {
  name: 'main-view',
  components: {
    PasswordDialog
  },
  data() {
    return {
      url: '',
      siteName: '',
      userId: '',
      password: '',
      items: [
        {
          url: 'http://www.amazon.com',
          siteName: 'Amazon',
          userId: 'JoeStalin',
          date: '2018/3/7',
          hide: false
        },
        {
          url: 'http://www.taobao.com',
          siteName: 'Taobao',
          userId: 'StFrank',
          date: '2018/3/7',
          hide: false
        }
      ]
    };
  },
  mounted() {
    this.$refs.dialog.openDialog();
  },

  methods: {
    addItem(data) {
      console.log(data);
    },
    onAddPassword() {
      this.$refs.dialog.openDialog();
    }

  }
};