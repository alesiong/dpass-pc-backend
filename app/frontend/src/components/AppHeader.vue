<template>
    <header class="mdui-appbar mdui-appbar-fixed mdui-color-theme-900">
        <div class="mdui-toolbar">
                <span class="mdui-btn mdui-btn-icon mdui-ripple mdui-ripple-white"
                      mdui-drawer="{target: '#left-drawer'}">
                    <i class="mdui-icon material-icons">menu</i>
                </span>

            <!--TODO: icon-->
            <a class="mdui-typo-title mdui-text-color-theme-grey-50">DPass</a>

            <div class="mdui-toolbar-spacer"></div>

            <div class="mdui-textfield search-bar"
                 v-if="!guard">
                <i class="mdui-icon material-icons">search</i>
                <input class="mdui-textfield-input search-text" type="text"
                       placeholder="Search"
                       v-on:input="onSearchChanged"/>
            </div>
            <!--TODO: lock storage-->
            <!--<span class="mdui-textfield mdui-textfield-expandable"-->
            <!--style="max-width: 480px;">-->
            <!--<button class="mdui-textfield-icon mdui-btn mdui-btn-icon ">-->
            <!--<i class="mdui-icon material-icons">search</i></button>-->
            <!--<input class="mdui-textfield-input mdui-color-white"-->
            <!--type="text" placeholder="Search"/>-->
            <!--<button class="mdui-textfield-close mdui-btn mdui-btn-icon">-->
            <!--<i class="mdui-icon material-icons">close</i></button>-->
            <!--</span>-->

            <!--<span class="mdui-btn mdui-btn-icon mdui-ripple mdui-ripple-white"-->
            <!--mdui-menu="{target: '#example-2'}">-->
            <!--<i class="mdui-icon material-icons">account_circle</i>-->
            <!--</span>-->

            <!--<ul class="mdui-menu" id="example-2">-->
            <!--<li class="mdui-menu-item">-->
            <!--<a href="javascript:;" class="mdui-ripple">-->
            <!--<i class="mdui-menu-item-icon mdui-icon material-icons">power_settings_new</i>log-->
            <!--in-->
            <!--</a>-->
            <!--</li>-->
            <!--<li class="mdui-menu-item">-->
            <!--<a href="javascript:;" class="mdui-ripple">-->
            <!--<i class="mdui-menu-item-icon mdui-icon material-icons">settings_power</i>log-->
            <!--out-->
            <!--</a>-->
            <!--</li>-->
            <!--</ul>-->
        </div>
    </header>
</template>


<!--<template>
    <header class="mdui-appbar mdui-appbar-fixed mdui-color-theme-900">
        <div class="mdui-toolbar">
            <button class="mdui-btn mdui-btn-icon"
                    mdui-drawer="{target: '#left-drawer'}">
                <i class="mdui-icon material-icons">menu</i>
            </button>
        </div>
    </header>
</template>-->

<script>
  export default {
    name: 'app-header',
    props: ['guard'],
    methods: {
      onSearchChanged(event) {
        this.$emit('search', event.target.value);
      }
    }
  };
</script>

<style scoped>
    .search-text {
        color: white;
        background: rgba(255, 255, 255, 0.2);
    }

    .search-bar {
        margin-right: 40px;
        width: calc(100% - 280px);
    }
</style>