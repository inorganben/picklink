const { defineUserConfig } = require('vuepress')
const { defaultTheme } = require('@vuepress/theme-default')

module.exports = defineUserConfig({
  lang: 'zh-TW',
  title: 'PickLink 知識庫',
  description: '自動收藏總結',
  theme: defaultTheme({
    docsDir: 'docs',
  }),
})
