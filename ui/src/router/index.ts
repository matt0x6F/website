import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import type { RouteLocation } from 'vue-router'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/HomeView.vue'),
      meta: { title: 'ooo-yay.com – Home' }
    },
    {
      path: '/about',
      name: 'about',
      component: () => import('@/views/AboutView.vue'),
      meta: { title: 'About – ooo-yay.com' }
    },
    {
      path: '/resume',
      name: 'resume',
      component: () => import('@/views/ResumeView.vue'),
      meta: { title: 'Resume – ooo-yay.com' }
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/ProfileView.vue'),
      meta: { requiresAuth: true, title: 'Profile – ooo-yay.com' }
    },
    {
      path: '/blog',
      name: 'blog-list',
      component: () => import('@/views/BlogListView.vue'),
      meta: { title: 'Blog – ooo-yay.com' }
    },
    {
      path: '/blog/:year/:slug',
      name: 'blog-post',
      component: () => import('@/views/BlogPostView.vue'),
      meta: { title: (route: RouteLocation) => `Blog Post – ooo-yay.com` }
    },
    {
      path: '/post/:year/:slug',
      name: 'BlogPost',
      component: () => import('@/views/BlogPostView.vue'),
      meta: { title: (route: RouteLocation) => `Blog Post – ooo-yay.com` }
    },
    {
      path: '/post/:year/:slug/comment',
      name: 'AddComment',
      component: () => import('@/views/CommentFormView.vue'),
      meta: { title: (route: RouteLocation) => `Add Comment – ooo-yay.com` }
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
      meta: { title: '404 – Page Not Found – ooo-yay.com' }
    }
  ],
})

router.beforeEach(async (to, from, next) => {
  const authStore = useAuthStore()

  // Wait for auth store to initialize
  if (!authStore.isInitialized) {
    try {
      await authStore.init()
    } catch (e) {
      // Optionally handle errors
    }
  }

  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    authStore.setRedirectUrl(to.fullPath)
    next({ 
      path: '/',
      query: { login: 'required' }
    })
  } else if (to.meta.requiresAdmin && !authStore.userData.isStaff) {
    next({ path: '/' })
  } else {
    next()
  }
})

export default router
