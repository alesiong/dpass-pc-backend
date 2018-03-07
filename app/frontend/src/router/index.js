import Vue from 'vue';
import Router from 'vue-router';
import MainView from '@c/MainView';
import PasswordView from '@c/PasswordView'

Vue.use(Router);

// TODO: add each page in router like this (don't forget to import)
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
