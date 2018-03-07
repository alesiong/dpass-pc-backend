// TODO: import and register the components here like this:
import AppMenu from '@c/AppMenu';
import AppHeader from '@c/AppHeader';
import {refreshSessionKey} from '../utils';

export default {
  components: {
    AppHeader,
    AppMenu
  },
  name: 'App',
  created: function() {
    let sessionKey = this.$route.query.key;
    if (sessionKey) {
      this.$router.replace('/');
    }
    if (!sessionKey) {
      sessionKey = localStorage.getItem('sessionKey');
      if (!sessionKey) {
        throw Error;
      }
    }
    const promise = refreshSessionKey(sessionKey);
    promise.then((sessionKey) => {
      this.globalData.sessionKey = sessionKey;
    });
  }
};