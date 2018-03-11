import AppMenu from '@c/AppMenu';
import AppHeader from '@c/AppHeader';
import GuardView from '@c/GuardView';
import {refreshSessionKey} from '../utils';
import {getInitState, nextMinutes} from '@/utils';

export default {
  components: {
    AppHeader,
    AppMenu,
    GuardView
  },
  data() {
    return {
      initState: null,
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
      this.globalData.sessionKeyExpiry = nextMinutes(10);
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