import 'mdui/dist/css/mdui.css';

import Vue from 'vue';
import VueClipboard from 'vue-clipboard2';
import App from './App';
import router from './router';

Vue.config.productionTip = false;
Vue.use(VueClipboard);
Vue.prototype.globalData = {
  sessionKey: null,
  sessionKeyExpiry: null
};

new Vue({
  el: '#app',
  router,
  render: h => h(App)
});
