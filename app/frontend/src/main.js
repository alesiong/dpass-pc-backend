import 'mdui/dist/css/mdui.css';

import Vue from 'vue';
import App from './App';
import router from './router';

Vue.config.productionTip = false;
Vue.prototype.globalData = {
  sessionKey: null,
  sessionKeyExpiry: null
};

new Vue({
  el: '#app',
  router,
  render: h => h(App)
});
