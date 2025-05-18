import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
    },
    {
      path: '/resume',
      name: 'resume',
      component: () => import('@/views/ResumeView.vue'),
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true }
    },
    {
      path: '/blog',
      name: 'blog-list',
      component: () => import('@/views/BlogListView.vue'),
    },
    {
      path: '/blog/:year/:slug',
      name: 'blog-post',
      component: () => import('@/views/BlogPostView.vue'),
    },
    {
      path: '/post/:year/:slug',
      name: 'BlogPost',
      component: () => import('@/views/BlogPostView.vue'),
    },
    {
      path: '/post/:year/:slug/comment',
      name: 'AddComment',
      component: () => import('@/views/CommentFormView.vue'),
    },
    {
      path: '/admin',
      name: 'admin',
      component: () => import('@/views/admin/AdminTemplate.vue'),
      meta: { requiresAuth: true, requiresAdmin: true },
      children: [
        {
          path: '',  // default child route
          name: 'admin-dashboard',
          component: () => import('@/views/admin/DashboardView.vue'),
        },
        {
          path: 'series',
          name: 'admin-series',
          component: () => import('@/views/admin/SeriesListView.vue'),
        },
        {
          path: 'series/new',
          name: 'admin-series-new',
          component: () => import('@/views/admin/SeriesFormView.vue'),
        },
        {
          path: 'series/edit/:id',
          name: 'admin-series-edit',
          component: () => import('@/views/admin/SeriesFormView.vue'),
        },
        {
          path: 'posts',
          name: 'admin-posts',
          component: () => import('@/views/admin/PostsView.vue'),
        },
        {
          path: 'posts/new',
          name: 'admin-posts-new',
          component: () => import('@/views/admin/PostEditorView.vue'),
        },
        {
          path: 'posts/:id',
          name: 'admin-posts-edit',
          component: () => import('@/views/admin/PostEditorView.vue'),
        },
        {
          path: 'users',
          name: 'admin-users',
          component: () => import('@/views/admin/UsersView.vue'),
        },
        {
          path: 'users/:id',
          name: 'admin-users-edit',
          component: () => import('@/views/admin/UserEditorView.vue'),
        },
        {
          path: 'comments',
          name: 'admin-comments',
          component: () => import('@/views/admin/CommentsView.vue'),
        },
        {
          path: 'comments/:id',
          name: 'admin-comment-detail',
          component: () => import('@/views/admin/CommentDetailView.vue'),
        },
        {
          path: 'files',
          name: 'admin-files',
          component: () => import('@/views/admin/FilesView.vue'),
        }
      ]
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/PageNotFoundView.vue'),
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
