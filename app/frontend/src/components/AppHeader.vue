<template>
    <header class="mdui-appbar mdui-appbar-fixed mdui-color-theme-900">
        <div class="mdui-toolbar">
            <button class="mdui-btn mdui-btn-icon"
                    mdui-drawer="{target: '#left-drawer'}">
                <i class="mdui-icon material-icons">menu</i>
            </button>
        </div>
    </header>
</template>

<script>
  export default {
    name: 'app-header'
  };
</script>

<style scoped>

</style>