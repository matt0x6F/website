import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import AboutView from '@/views/AboutView.vue'
import ProfileView from '@/views/ProfileView.vue'
import BlogListView from '@/views/BlogListView.vue'
import BlogPostView from '@/views/BlogPostView.vue'
import ResumeView from '@/views/ResumeView.vue'
import AdminTemplate from '@/views/admin/AdminTemplate.vue'
import DashboardView from '@/views/admin/DashboardView.vue'
import PostsView from '@/views/admin/PostsView.vue'
import PostEditor from '@/views/admin/PostEditor.vue'
import UsersView from '@/views/admin/UsersView.vue'
import UserEditor from '@/views/admin/UserEditor.vue'
import CommentsView from '@/views/admin/CommentsView.vue'
import FilesPage from '@/views/admin/FilesPage.vue'
import PageNotFoundView from '@/views/PageNotFoundView.vue'
import CommentDetailView from '@/views/admin/CommentDetailView.vue'
import { useAuthStore } from '@/stores/auth'
import SeriesListView from '@/views/admin/SeriesListView.vue'
import SeriesFormView from '@/views/admin/SeriesFormView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
    },
    {
      path: '/about',
      name: 'about',
      component: AboutView,
    },
    {
      path: '/resume',
      name: 'resume',
      component: ResumeView,
    },
    {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
    },
    {
      path: '/blog',
      name: 'blog-list',
      component: BlogListView
    },
    {
      path: '/blog/:year/:slug',
      name: 'blog-post',
      component: BlogPostView
    },
    {
      path: '/post/:year/:slug',
      name: 'BlogPost',
      component: () => import('@/views/BlogPostView.vue')
    },
    {
      path: '/post/:year/:slug/comment',
      name: 'AddComment',
      component: () => import('@/views/CommentFormView.vue')
    },
    {
      path: '/admin',
      name: 'admin',
      component: AdminTemplate,
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',  // default child route
          name: 'admin-dashboard',
          component: DashboardView,
        },
        {
          path: 'series',
          name: 'admin-series',
          component: SeriesListView
        },
        {
          path: 'series/new',
          name: 'admin-series-new',
          component: SeriesFormView
        },
        {
          path: 'series/edit/:id',
          name: 'admin-series-edit',
          component: SeriesFormView
        },
        {
          path: 'posts',
          name: 'admin-posts',
          component: PostsView,
        },
        {
          path: 'posts/new',
          name: 'admin-posts-new',
          component: PostEditor,
        },
        {
          path: 'posts/:id',
          name: 'admin-posts-edit',
          component: PostEditor,
        },
        {
          path: 'users',
          name: 'admin-users',
          component: UsersView,
        },
        {
          path: 'users/:id',
          name: 'admin-users-edit',
          component: UserEditor,
        },
        {
          path: 'comments',
          name: 'admin-comments',
          component: CommentsView,
        },
        {
          path: 'comments/:id',
          name: 'admin-comment-detail',
          component: CommentDetailView,
        },
        {
          path: 'files',
          name: 'admin-files',
          component: FilesPage,
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: PageNotFoundView,
    }
  ],
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    // Store the attempted URL for redirecting after login
    authStore.setRedirectUrl(to.fullPath)
    next({ 
      path: '/',
      query: { login: 'required' }  // This can trigger the login dialog
    })
  } else if (to.meta.requiresAdmin && !authStore.userData.isStaff) {
    // Redirect non-staff users to home page
    next({ path: '/' })
  } else {
    next()
  }
})

export default router
