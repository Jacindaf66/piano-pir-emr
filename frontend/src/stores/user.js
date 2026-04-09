// import { defineStore } from 'pinia'
// import axios from 'axios'

// export const useUserStore = defineStore('user', {
//   state: () => ({
//     token: localStorage.getItem('token') || '',
//     userInfo: {},
//     role: '',
//     name: '',
//     department: ''
//   }),

//   actions: {
//     async login(form) {
//       const res = await axios.post('http://127.0.0.1:8000/login', form)
//       this.token = res.data.token
//       this.role = res.data.role
//       this.name = res.data.name
//       this.department = res.data.department
//       this.userInfo = res.data
//       localStorage.setItem('token', this.token)
//       axios.defaults.headers.common['Authorization'] = `Bearer ${this.token}`
//     },

//     logout() {
//       this.token = ''
//       this.userInfo = {}
//       this.role = ''
//       localStorage.removeItem('token')
//       delete axios.defaults.headers.common['Authorization']
//     }
//   }
// })