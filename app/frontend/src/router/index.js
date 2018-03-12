import Vue from 'vue';
import Router from 'vue-router';
import MainView from '@c/MainView';
import PasswordView from '@c/PasswordView'

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'MainView',
      component: MainView
    },
    {
      path: '/password/',
      name: 'PasswordView',
      component: PasswordView
    },
    {
      path: '*',
      redirect: '/'
    }
  ]
});
