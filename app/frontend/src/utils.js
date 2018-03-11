// @flow

import CryptoJS from 'crypto-js';
import AES from 'crypto-js/aes';
import hmacSHA256 from 'crypto-js/hmac-sha256';
import mdui from 'mdui';
import Vue from 'vue';

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
 * Use AES and HMAC to encrypt the `message` and generates the authentication token. `message` should be in plaintext.
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

export function encrypt(message: string, key: string): [string, string] {
  key = CryptoJS.enc.Hex.parse(key + key);
  const cipher = AES.encrypt(message, key, {
    iv: CryptoJS.enc.Base64.parse(fixedIV),
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  }).ciphertext;

  return cipher.toString(CryptoJS.enc.Base64);
}

export function decrypt(ciphertext: string, key: string): ?string {
  key = CryptoJS.enc.Hex.parse(key + key);
  const cipher = AES.decrypt(ciphertext, key, {
    iv: CryptoJS.enc.Base64.parse(fixedIV),
    mode: CryptoJS.mode.CBC,
    padding: CryptoJS.pad.Pkcs7
  });
  return cipher.toString(CryptoJS.enc.Utf8);
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
    console.log(e);
  }

  return sessionKey;
}

export async function getInitState(): Promise<number> {
  let state = 0;
  try {
    const res = await toPromise({
      func: $$.ajax,
      url: '/api/settings/?type=init_state',
      dataType: 'json'
    });
    state = res.state;
  } catch (e) {
    console.log(e);
  }
  return state;
}

export async function ensureSession(component: Vue): Promise<void> {
  if (Date.now() > component.globalData.sessionKeyExpiry) {
    component.globalData.sessionKey = await refreshSessionKey(component.globalData.sessionKey);
    component.globalData.sessionKeyExpiry = nextMinutes(10);
    console.log('session refreshed');
  }
  console.log('in session');
}

export function nextMinutes(minutes: number): number {
  return Date.now() + minutes * 60 * 1000;
}

// FIXME: need rewrite
export function randPassword(): string {
  const text = ['abcdefghijklmnopqrstuvwxyz', 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', '1234567890', '~!@#$%^&*()_+";",./?<>'];
  const rand = function(min, max) {
    return Math.floor(Math.max(min, Math.random() * (max + 1)));
  };
  const len = rand(10, 16);
  let pw = '';
  for (let i = 0; i < len; ++i) {
    const strpos = rand(0, 3);
    pw += text[strpos].charAt(rand(0, text[strpos].length));
  }
  return pw;
}

export function copyToClickboard(value: string) {
  const clickboard = document.getElementById('clickboard');
  if (clickboard) {
    // $FlowFixMe
    clickboard.value = value;
    clickboard.setAttribute('type', '');
    // $FlowFixMe
    clickboard.select();
    const success = document.execCommand('copy');
    clickboard.setAttribute('type', 'hidden');
    // $FlowFixMe
    clickboard.value = '';
    return success;
  }
}