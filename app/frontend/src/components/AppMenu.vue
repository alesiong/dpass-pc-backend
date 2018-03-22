<template>
    <!--TODO: here are the navigation menu-->
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
            <router-link class="mdui-list-item mdui-ripple"
                         to="/secret-notes/"
                         exact-active-class="mdui-list-item-active">
                Secret Notes
            </router-link>

            <li class="mdui-divider"></li>

            <li class="mdui-list-item mdui-ripple">
                <i class="mdui-icon material-icons mdui-m-r-2">
                    settings_backup_restore
                </i>
                Sync & Backup
            </li>
            <router-link class="mdui-list-item mdui-ripple"
                         to="/settings/"
                         exact-active-class="mdui-list-item-active">
                <i class="mdui-icon material-icons mdui-m-r-2">settings</i>
                Settings
            </router-link>
        </ul>
    </div>
</template>


<!--<template>
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
</template>-->

<script>
  export default {
    name: 'app-menu'
  };
</script>

<style scoped>

</style>