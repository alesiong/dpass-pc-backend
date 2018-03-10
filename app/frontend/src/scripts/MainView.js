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
          hide: false,
          message: '********',
          btnText:"REVEAL",
          isShow:false
        },
        {
          url: 'http://www.taobao.com',
          siteName: 'Taobao',
          userId: 'StFrank',
          date: '2018/3/7',
          hide: false,
        }
      ],
      message: '********',
      btnText:"REVEAL",
      isShow:false
    };
  },
  // mounted() {
  //   this.$refs.dialog.openDialog();
  // },

  methods: {
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
      var xmlhttp;
      if (window.XMLHttpRequest)
      {
        xmlhttp=new XMLHttpRequest();
      }
      else
      {
        xmlhttp=new ActiveXObject("Microsoft.XMLHTTP");
      }
      xmlhttp.onreadystatechange=function()
      {
        if (xmlhttp.readyState==4 && xmlhttp.status==200)
        {
          document.getElementById("myDiv").innerHTML=xmlhttp.responseText;
        }
      }
      xmlhttp.open("GET","http://localhost:5000/test.html",true);
      xmlhttp.send();
    }
    // addPassword: function() {
    //   mdui.prompt('Enter master password:', this.onAdd.bind(this),
    //       () => {
    //       }, {
    //         modal: true,
    //         histroy: false // TODO: remember to add this, or vue's router may fail
    //       });
    // },
    // verifyPassword: function() {
    //   mdui.prompt('Verify master password:', this.onVerify.bind(this),
    //       () => {
    //       }, {
    //         modal: true,
    //         histroy: false
    //       });
    // },
    // onAdd: function(value) {
    //   const [cipher, hmac] = encryptAndAuthenticate(value, this.globalData.sessionKey);
    //   $$.ajax({
    //     url: '/api/master_password/new/',
    //     method: 'POST',
    //     dataType: 'json',
    //     data: JSON.stringify({
    //       data: cipher,
    //       hmac: hmac
    //     }),
    //     contentType: 'application/json',
    //     success: () => {
    //       mdui.alert('Master Password Set');
    //     },
    //     statusCode: {
    //       '401': () => {
    //         mdui.alert('Session Key broken!');
    //       }
    //     }
    //   });
    // },
    // onVerify: function(value) {
    //   const [cipher, hmac] = encryptAndAuthenticate(value, this.globalData.sessionKey);
    //   $$.ajax({
    //     url: '/api/master_password/verify/',
    //     method: 'POST',
    //     dataType: 'json',
    //     data: JSON.stringify({
    //       data: cipher,
    //       hmac: hmac
    //     }),
    //     contentType: 'application/json',
    //     success: () => {
    //       mdui.alert('Master Password Verified');
    //     },
    //     statusCode: {
    //       '401': () => {
    //         mdui.alert('Verification failed or Session Key broken!');
    //       }
    //     }
    //   });
    // }
  }
};