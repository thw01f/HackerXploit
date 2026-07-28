import { defineStore } from 'pinia'
import axios from 'axios'

export const useClubStore = defineStore('club', {
  state: () => ({
    stats: null,
    courses: [],
    currentCourse: null,
    competitions: [],
    opportunities: [],
    members: [],
    loading: false
  }),
  actions: {
    async fetchStats() {
      try {
        const res = await axios.get('/api/club/stats')
        this.stats = res.data
      } catch (err) {
        console.error('Fetch stats failed', err)
      }
    },

    async fetchCourses() {
      try {
        const res = await axios.get('/api/academy/courses')
        this.courses = res.data.courses
      } catch (err) {
        console.error('Fetch courses failed', err)
      }
    },

    async fetchCourseDetail(id) {
      try {
        const res = await axios.get(`/api/academy/courses/${id}`)
        this.currentCourse = res.data
        return res.data
      } catch (err) {
        console.error('Fetch course detail failed', err)
      }
    },

    async fetchCompetitions() {
      try {
        const res = await axios.get('/api/competitions')
        this.competitions = res.data.competitions
      } catch (err) {
        console.error('Fetch competitions failed', err)
      }
    },

    async fetchOpportunities() {
      try {
        const res = await axios.get('/api/opportunities')
        this.opportunities = res.data.opportunities
      } catch (err) {
        console.error('Fetch opportunities failed', err)
      }
    },

    async fetchMembers() {
      try {
        const res = await axios.get('/api/club/members')
        this.members = res.data.members
      } catch (err) {
        console.error('Fetch members failed', err)
      }
    }
  }
})
