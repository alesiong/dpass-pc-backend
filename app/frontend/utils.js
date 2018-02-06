// @flow

import CryptoJS from 'crypto-js';
import AES from 'crypto-js/aes';
import hmacSHA256 from 'crypto-js/hmac-sha256';
import mdui from 'mdui';

declare var $$: mdui.jQueryStatic;

const fixedIV = 'Kv7OoDnecCsU11N2WTbNow==';


/**
 * Get the hash tag (the string after # in the url) with `key`
 */
export function getLocationHashValue(key: string): string | null {
  const matches = location.hash.match(new RegExp(key + '=([^&]*)'));
  return matches ? matches[1] : null;
}

/**
 * Use AES and HMAC to encrypt the `message` and generates the authentication token. `message` should be Base64 encoded.
 * `key` should be a Hex encoded session key.
 */
export function encryptAndAuthenticate(message: string, key: string): [string, string] {
  key = CryptoJS.enc.Hex.parse(key);
  const cipher = AES.encrypt(message, key, {
    iv: CryptoJS.enc.Base64.parse(fixedIV),
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  }).ciphertext;

  const hmac = hmacSHA256(cipher, key);

  return [cipher.toString(CryptoJS.enc.Base64), hmac.toString(CryptoJS.enc.Base64)];
}

/**
 * Decrypt and verify the HMAC authentication token. If verification failed, returns `null`. `ciphertext` and `hmac`
 * should be Base64 encoded.
 */
export function decryptAndVerify(ciphertext: string, hmac: string, key: string): ?string {
  key = CryptoJS.enc.Hex.parse(key);
  if (hmacSHA256(CryptoJS.enc.Base64.parse(ciphertext), key).toString(CryptoJS.enc.Base64) === hmac) {
    const cipher = AES.decrypt(ciphertext, key, {
      iv: CryptoJS.enc.Base64.parse(fixedIV),
      mode: CryptoJS.mode.CBC,
      padding: CryptoJS.pad.Pkcs7
    });
    return cipher.toString(CryptoJS.enc.Utf8);
  }
  return null;
}

function toPromise(obj: Object) {
  const func = obj.func;
  return new Promise((resolve, reject) => {
    Object.assign(obj, {
      success: (res) => resolve(res),
      error: (res) => reject(res)
    });
    func(obj);
  });

}

/**
 * Ask the backend for a new session key. `sessionKey` is the old one.
 */
export async function refreshSessionKey(sessionKey: string): Promise<string> {
  const [cipher, hmac] = encryptAndAuthenticate('refresh', sessionKey);

  try {
    const res = await toPromise({
      func: $$.ajax,
      url: '/api/session/refresh/',
      method: 'POST',
      dataType: 'json',
      data: JSON.stringify({
        data: cipher,
        hmac: hmac
      }),
      contentType: 'application/json'
    });
    const newSessionKey = decryptAndVerify(res.data, res.hmac, sessionKey);
    if (newSessionKey) {
      localStorage.setItem('sessionKey', newSessionKey);
      return newSessionKey;
    }
  } catch (e) {
  }

  return sessionKey;
}