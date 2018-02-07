import test from 'unit.js';
import {encryptAndAuthenticate, decryptAndVerify} from '../utils';

const key = '30313233343536373839616263646566';
const hmacEncrypted = 'os/PLmm+3T8Hb0zZAEBH7A==';
const hmac = 'jGgscY5IRGtWkIdOApuLtsdpa8BzT5UrgtiWca283Kk=';

describe('Test encryptAndAuthenticate()', () => {
  it('encrypts in the right way', () => {
    const [ciphertext, hmac_] = encryptAndAuthenticate('test', key);
    test.string(ciphertext).is(hmacEncrypted);
    test.string(hmac_).is(hmac);
  });
});

describe('Test decryptAndVerify', () => {
  it('decrypts and verifies in the right way', () => {
    test.string(decryptAndVerify(hmacEncrypted, hmac, key)).is('test');
  });
  it('returns null if verification fails', () => {
    test.value(decryptAndVerify('os/PLmm+3T8Hb0zZAasd7A==', hmac, key)).isNull();
    test.value(decryptAndVerify(hmacEncrypted, 'asdf', key)).isNull();

  });
});