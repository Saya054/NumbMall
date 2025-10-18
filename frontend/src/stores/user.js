import { defineStore } from 'pinia'
import { ref } from 'vue'
import api from '@/utils/api'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const userInfo = ref(JSON.parse(localStorage.getItem('userInfo') || 'null'))
  
  // 登录
  const login = async (username, password) => {
    const res = await api.post('/auth/login', { username, password })
    token.value = res.data.token
    userInfo.value = res.data.user
    localStorage.setItem('token', token.value)
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    return res
  }
  
  // 登出
  const logout = () => {
    token.value = ''
    userInfo.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('userInfo')
  }
  
  // 获取用户信息
  const getUserInfo = async () => {
    const res = await api.get('/auth/info')
    userInfo.value = res.data
    localStorage.setItem('userInfo', JSON.stringify(userInfo.value))
    return res
  }
  
  // 是否是管理员
  const isAdmin = () => {
    return userInfo.value?.role === 'admin'
  }
  
  return {
    token,
    userInfo,
    login,
    logout,
    getUserInfo,
    isAdmin
  }
})



