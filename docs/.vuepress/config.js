const { defineUserConfig } = require('vuepress')
const { viteBundler } = require('@vuepress/bundler-vite')
const { defaultTheme } = require('@vuepress/theme-default')

module.exports = defineUserConfig({
  lang: 'zh-TW',
  title: 'PickLink 知識庫',
  description: '自動收藏總結',
  bundler: viteBundler(),
  theme: defaultTheme({
    docsDir: 'docs',
  }),
})
