// TODO: import and register the components here like this:
import AppMenu from '@c/AppMenu';
import AppHeader from '@c/AppHeader';
import GuardView from '@c/GuardView';
import {refreshSessionKey} from '../utils';
import {getInitState} from '@/utils';

export default {
  components: {
    AppHeader,
    AppMenu,
    GuardView
  },
  data() {
    return {
      initState: 0,
      passwordVerification: false
    };
  },
  name: 'App',
  computed: {
    guard() {
      return this.initState !== 2 || this.passwordVerification;
    }
  },
  created: function() {
    let sessionKey = this.$route.query.key;
    if (sessionKey) {
      this.$router.replace('/');
    }
    if (!sessionKey || sessionKey.length !== 32) {
      sessionKey = localStorage.getItem('sessionKey');
      if (!sessionKey) {
        throw Error;
      }
    }
    const promise = refreshSessionKey(sessionKey);
    promise.then((sessionKey) => {
      this.globalData.sessionKey = sessionKey;
    });

    getInitState().then((state) => {
      this.initState = state;
    });
  },
  methods: {
    refreshState() {
      const id = window.setInterval(() => {
        getInitState().then((state) => {
          this.initState = state;
          if (state === 2) {
            window.clearInterval(id);
          }
        });
      }, 100);
    },
    verifyPassword() {
      this.passwordVerification = true;
    },
    onVerifiedPassword() {
      this.passwordVerification = false;
    }
  }
};