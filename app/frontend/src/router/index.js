import Vue from 'vue';
import Router from 'vue-router';
import MainView from '@c/MainView';

Vue.use(Router);

// TODO: add each page in router like this (don't forget to import)
export default new Router({
  routes: [
    {
      path: '/',
      name: 'MainView',
      component: MainView
    }
  ]
});
