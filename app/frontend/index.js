// @flow

import mdui from 'mdui';
import sha512 from 'js-sha512';
import Component from './component';
import type {App} from './component';

declare var $$: mdui.jQueryStatic;

export class IndexComponent extends Component {
  onAdd(value: string) {
    $$.ajax({
      url: '/api/demo/' + value,
      dataType: 'json',
      success: (data, status) => {
        console.log(status);
        mdui.alert(data.echo + '\n' + sha512(data.echo));
      },
      statusCode: {
        '404': () => {
          mdui.alert('Message cannot be empty');
        }
      }
    });
  }

  constructor(app: App) {
    super(app);
    const that = this;
    $$('#fab-add').on('click', () => {
      mdui.prompt('Enter a string', that.onAdd,
          () => {
          }, {
            modal: true
          });
    });
  }
}

Component.register(IndexComponent);
