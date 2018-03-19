import mdui from 'mdui';
import {randPassword} from '../utils';
import {copyToClickboard, decrypt} from '@/utils';

export default {
    name: 'modify-dialog',
    props: ['type', 'data', 'search'],
    data() {
        return {
            url: '',
            siteName: '',
            userId: '',
            password: '',
            title: 'Modify',
            id: `modify-dialog-${this._uid}`
        };
    },
    updated() {
        mdui.mutation();
    },
    computed: {
        valid() {
            return this.url !== '' && this.userId !== '' && this.password !== '' && this.siteName !== '';
        },
        formatDate(timestamp) {
            const date = new Date(timestamp);
            return date.getFullYear() + '/' + (date.getMonth() + 1) + '/' +
                date.getDate();
        },
    },
    methods: {
        openDialog(options, initValue) {
            options = Object.assign({modal: true}, options);
            initValue = initValue || {};
            if (initValue) {
                this.url = initValue.url || '';
                this.siteName = initValue.siteName || '';
                this.userId = initValue.userId || '';
                this.password = initValue.password || '';
            }
            new mdui.Dialog('#' + this.id, options).open();
        },
        onClickAdd() {
            this.$emit('click-add', {
                url: this.url,
                siteName: this.siteName,
                userId: this.userId,
                password: this.password,
                type: 'password'
            });
            this.password = '';
        },
        generateRandomPassword() {
            this.password = randPassword();
        }
    }
};