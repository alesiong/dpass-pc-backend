// @flow

import mdui from 'mdui';
import Component from './component';
import type {App} from './component';
import {encryptAndAuthenticate} from './utils';

declare var $$: mdui.jQueryStatic;

export class IndexComponent extends Component {
  onAdd(value: string) {
    const [cipher, hmac] = encryptAndAuthenticate(value, this.app.sessionKey);
    $$.ajax({
      url: '/api/master_password/new/',
      method: 'POST',
      dataType: 'json',
      data: JSON.stringify({
        data: cipher,
        hmac: hmac
      }),
      contentType: 'application/json',
      success: () => {
        mdui.alert('Master Password Set');
      },
      statusCode: {
        '401': () => {
          mdui.alert('Session Key broken!');
        }
      }
    });
  }

  onVerify(value: string) {
    const [cipher, hmac] = encryptAndAuthenticate(value, this.app.sessionKey);
    $$.ajax({
      url: '/api/master_password/verify/',
      method: 'POST',
      dataType: 'json',
      data: JSON.stringify({
        data: cipher,
        hmac: hmac
      }),
      contentType: 'application/json',
      success: () => {
        mdui.alert('Master Password Verified');
      },
      statusCode: {
        '401': () => {
          mdui.alert('Verification failed or Session Key broken!');
        }
      }
    });
  }

  constructor(app: App) {
    super(app);
    const that = this;
    $$('#fab-add').on('click', () => {
      mdui.prompt('Enter master password:', that.onAdd.bind(that),
          () => {
          }, {
            modal: true
          });
    });
    $$('#fab-verify').on('click', () => {
      mdui.prompt('Verify master password:', that.onVerify.bind(that),
          () => {
          }, {
            modal: true
          });
    });
  }
}

Component.register(IndexComponent);
