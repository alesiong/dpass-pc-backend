<template>
    <div class="mdui-drawer mdui-color-theme-800" id="left-drawer">
        <ul class="mdui-list" id="menu">
            <router-link class="mdui-list-item mdui-ripple"
                         to="/"
                         exact-active-class="mdui-list-item-active">
                All
            </router-link>
            <router-link class="mdui-list-item mdui-ripple"
                         to="/password/"
                         exact-active-class="mdui-list-item-active">
                Passwords
            </router-link>
            <li class="mdui-list-item mdui-ripple">
                Secret Notes
            </li>
        </ul>
    </div>
</template>

<script>
  export default {
    name: 'app-menu'
  };
</script>

<style scoped>

</style>