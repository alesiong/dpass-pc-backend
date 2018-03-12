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
                         to="/secretNote/"
                         exact-active-class="mdui-list-item-active">
                Secret Notes
            </router-link>
            <li class="mdui-divider mdui-color-white"  ></li>
            <li class="mdui-menu-item mdui-ripple"style="margin-top:2.5em" >
                <i class="mdui-menu-item-icon mdui-icon material-icons">settings_backup_restore
                </i>Sync & Backup
            </li>
            <li class="mdui-menu-item mdui-ripple"style="margin-top:1.0em">
                <i class="mdui-menu-item-icon mdui-icon material-icons">settings</i>Setting

            </li>
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