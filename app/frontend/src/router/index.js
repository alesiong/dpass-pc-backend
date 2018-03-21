import Vue from 'vue';
import Router from 'vue-router';
import MainView from '@c/MainView';
import SettingsView from '@c/SettingsView';

Vue.use(Router);

export default new Router({
  mode: 'history',
  routes: [
    {
      path: '/',
      name: 'All',
      component: MainView,
      props: {type: 'all'}
    },
    {
      path: '/password/',
      name: 'Password',
      component: MainView,
      props: {type: 'password'}
    },
    {
      path: '/secret-notes/',
      name: 'Secret Notes',
      component: MainView,
      props: {type: 'secret'}
    },
    {
      path: '/settings/',
      name: 'Settings',
      component: SettingsView
    },
    {
      path: '*',
      redirect: '/'
    }
  ]
});
