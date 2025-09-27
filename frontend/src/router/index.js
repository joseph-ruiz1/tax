import { createRouter, createWebHistory } from 'vue-router'
import LoginView from '../views/LoginView.vue'
import UsersView from '../views/UsersView.vue'
import DashboardView from '../views/DashboardView.vue'
import DatasetDetail from '../views/DatasetDetail.vue'
import DataEntryView from '@/views/DataEntryView.vue'
import ResultsView from '@/views/ResultsView.vue'


const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {path: '/', component: DashboardView},
    {path: '/login', component: LoginView},
    {path: '/users/me', component: UsersView},
    {path: '/datasets/:id', name: 'Dataset Detail', component: DatasetDetail},
    {path: '/datasets/:id/new', name:'New dataset', component: DataEntryView},
    {path: '/datasets/:id/results', name:'Calculation results', component: ResultsView}
  ],
})

export default router
