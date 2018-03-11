import PasswordDialog from '@c/PasswordDialog';
import {decryptAndVerify, encryptAndAuthenticate, ensureSession} from '@/utils';

export default {
  name: 'main-view',
  components: {
    PasswordDialog
  },
  data() {
    return {
      items: []
    };
  },
  mounted() {
  },
  created() {
    this.fetchPasswords();
    window.setInterval(this.fetchPasswords.bind(this), 30000);
  },

  methods: {
    addItem(data) {
      data.date = Date.now();
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
            mdui.snackbar('Successfully added password');
            this.fetchPasswords();
          },
          statusCode: {
            '401': () => {
              // FIXME: this may disturb user (e.g. user may just submit the password)
              this.$parent.verifyPassword();
            }
          }
        });
      });
    },
    onAddPassword() {
      this.$refs.dialog.openDialog();
    },
    fetchPasswords() {
      $$.ajax({
        url: '/api/password/',
        dataType: 'json',
        success: (res) => {
          let passwords = decryptAndVerify(res.data, res.hmac, this.globalData.sessionKey);
          passwords = JSON.parse(passwords);
          const newPasswords = [];
          for (const p of passwords) {
            newPasswords.push(Object.assign({
                  hide: false
                },
                p.metadata
            ));
          }
          this.items = newPasswords;
          console.log(this.items)
        },
        statusCode: {
          '401': () => {
            // FIXME: this may disturb user (e.g. user may be inputting the passwords)
            this.$parent.verifyPassword();
          }
        }
      });
    },
    addItem(data) {
      var myDate=new Date();
      this.items.push({url:data.url,siteName:data.siteName,userId:data.userId,
        date:myDate.getFullYear()+'/'+(myDate.getMonth()+1)+'/'+myDate.getDate(),
        hide:false}
        );
      },
    showToggle:function(){
      this.isShow = !this.isShow
      if(this.isShow){
        this.message='12345678'
        this.btnText = "HIDE"
      }else{
        this.message='********'
        this.btnText = "REVEAL"
      }
    },
    onAddPassword() {
      this.$refs.dialog.openDialog();
    },
    // onCopy(){
    //     var Url2=document.getElementById("mainViewPassword");
    //     Url2.select(); // 选择对象
    //     document.execCommand("Copy"); // 执行浏览器复制命令
    //     alert("已复制好，可贴粘。");
    // },

    onCopy: function (e){
      console.log('You just copied: ' + e.text);
    },
    onError: function (e){
      console.log('Failed to copy texts');
    },

    getPassword(){

    }

  }
};