import { defineUserConfig } from 'vuepress'
import { viteBundler } from '@vuepress/bundler-vite'
import { defaultTheme } from '@vuepress/theme-default'

export default defineUserConfig({
  base: '/picklink/',
  lang: 'zh-TW',
  title: 'PickLink 知識庫',
  description: '自動收藏總結',
  bundler: viteBundler(),
  theme: defaultTheme({
    sidebar: 'auto',
  }),
})
