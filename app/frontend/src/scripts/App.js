import AppMenu from '@c/AppMenu';
import AppHeader from '@c/AppHeader';
import GuardView from '@c/GuardView';
import {refreshSessionKey} from '../utils';
import {getInitState, nextMinutes} from '@/utils';
import io from 'socket.io-client';

export default {
  components: {
    AppHeader,
    AppMenu,
    GuardView
  },
  data() {
    return {
      initState: null,
      passwordVerification: false,
      search: ''
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

    $$(document).ajaxError((_, xhr) => {
      if (xhr.status === 401) {
        const res = JSON.parse(xhr.response);
        switch (res.error) {
          case 'Master Password Expired':
            // FIXME: this may disturb user (e.g. user may just submit/inputting the password)
            this.verifyPassword();
            console.log('password expired');
            break;
        }
      }
    });
    const socket = io();
    socket.on('state change', (state) => {
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
      }, 500);
    },
    verifyPassword() {
      this.passwordVerification = true;
    },
    onVerifiedPassword() {
      this.passwordVerification = false;
    },
    onSearch(value) {
      this.search = value;
    }
  }
};