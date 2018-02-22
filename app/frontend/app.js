// @flow
import 'mdui/dist/css/mdui.css';

import type {App} from './component';
import Component from './component';

import './index';
import {decryptAndVerify, encryptAndAuthenticate, getLocationHashValue, refreshSessionKey} from './utils';
import mdui from 'mdui';

declare var $$: mdui.jQueryStatic;

function createApp(callback: (App) => void) {
  let sessionKey = getLocationHashValue('key');
  location.hash = '';
  if (sessionKey === null) {
    sessionKey = localStorage.getItem('sessionKey');
    if (!sessionKey) {
      throw Error;
    }
  }
  const promise = refreshSessionKey(sessionKey);
  promise.then((sessionKey) => {
    callback({
      sessionKey: sessionKey
    });
  });
}

createApp(Component.init);
