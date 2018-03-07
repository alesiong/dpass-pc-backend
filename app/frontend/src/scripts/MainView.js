import {encryptAndAuthenticate} from '../utils';
import mdui from 'mdui';

export default {
  name: 'main-view',
  data() {
    return {
      url: '',
      siteName:'',
      userId: '',
      password: '',
      items:[
        {
          url:'http://www.amazon.com',
          siteName:'Amazon',
          userId:'JoeStalin',
          date:'2018/3/7',
          hide:false
        },
        {
          url:'http://www.taobao.com',
          siteName:'Taobao',
          userId:'StFrank',
          date:'2018/3/7',
          hide:false
        }
      ]
    };
  },
  mounted() {
    this.onAddPassword();
  },

  methods: {
    checkIsInvalid() {
      return !(this.url !== '' && this.userId !== '' && this.password !== '' && this.siteName !== '');
    },
    addItem() {
      const urlTest = '';
      console.log(this.url);
      // if (!this.checkIsInvalid()) {
      //   new mdui.Dialog('#AddDialog').close();
      // }
    },
    onAddPassword() {
      this.url = '';
      this.userId = '';
      this.password = '';
      this.siteName='';
      new mdui.Dialog('#AddDialog',{modal:true}).open();
    },
    addPassword: function() {
      mdui.prompt('Enter master password:', this.onAdd.bind(this),
          () => {
          }, {
            modal: true,
            histroy: false // TODO: remember to add this, or vue's router may fail
          });
    },
    verifyPassword: function() {
      mdui.prompt('Verify master password:', this.onVerify.bind(this),
          () => {
          }, {
            modal: true,
            histroy: false
          });
    },
    onAdd: function(value) {
      const [cipher, hmac] = encryptAndAuthenticate(value, this.globalData.sessionKey);
      $$.ajax({
        url: '/api/master_password/new/',
        method: 'POST',
        dataType: 'json',
        data: JSON.stringify({
          data: cipher,
          hmac: hmac
        }),
        contentType: 'application/json',
        success: () => {
          mdui.alert('Master Password Set');
        },
        statusCode: {
          '401': () => {
            mdui.alert('Session Key broken!');
          }
        }
      });
    },
    onVerify: function(value) {
      const [cipher, hmac] = encryptAndAuthenticate(value, this.globalData.sessionKey);
      $$.ajax({
        url: '/api/master_password/verify/',
        method: 'POST',
        dataType: 'json',
        data: JSON.stringify({
          data: cipher,
          hmac: hmac
        }),
        contentType: 'application/json',
        success: () => {
          mdui.alert('Master Password Verified');
        },
        statusCode: {
          '401': () => {
            mdui.alert('Verification failed or Session Key broken!');
          }
        }
      });
    }
  }
};