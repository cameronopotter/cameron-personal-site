# 🌱 Digital Greenhouse - Interactive Personal Portfolio

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Frontend Tests](https://github.com/cameronopotter/digital-greenhouse/workflows/Frontend%20Tests/badge.svg)](https://github.com/cameronopotter/digital-greenhouse/actions)
[![Backend Tests](https://github.com/cameronopotter/digital-greenhouse/workflows/Backend%20Tests/badge.svg)](https://github.com/cameronopotter/digital-greenhouse/actions)
[![Performance Score](https://img.shields.io/badge/Performance-95%2B-brightgreen.svg)](https://web.dev/measure/)
[![Accessibility](https://img.shields.io/badge/Accessibility-WCAG%202.1%20AA-blue.svg)](https://www.w3.org/WAI/WCAG21/quickref/)

> **A living, breathing digital ecosystem where projects grow as living plants, weather responds to your mood, and visitors become part of your creative journey.**

![Digital Greenhouse Preview](./assets/garden-preview.png)

---

## ✨ **What Makes This Special**

The Digital Greenhouse isn't just a portfolio website—it's an **interactive 3D art piece** that tells your story through:

🌱 **Living Projects** - Your projects literally grow based on real GitHub activity  
🌤️ **Mood Weather** - Garden atmosphere changes with music, coding patterns, and real weather  
⭐ **Skill Constellations** - Navigate through 3D stars representing your technical abilities  
🎭 **Visitor Ecosystem** - Anonymous visitors become part of your garden's living community  
🎨 **Seasonal Evolution** - Visual themes that evolve with time and your career journey  

---

## 🎯 **Core Features**

### 🌿 **The Living Garden**
- **5 Growth Stages**: Projects evolve from seeds → sprouts → saplings → trees → ancient wisdom
- **Real-time Growth**: Every GitHub commit, star, or PR advances your project plants
- **Interactive Plants**: Click any project to dive into detailed 3D exploration pods
- **Growth Animations**: Smooth, organic animations with particle effects

### 🌦️ **Dynamic Weather System**
- **11 Atmospheric Types**: From serene mornings to stormy coding sessions
- **Multi-source Mood**: Blends music (40%), weather (30%), productivity (20%), time (10%)
- **Visual Effects**: 2000+ particles with rain, snow, sparkles, aurora, falling leaves
- **Smooth Transitions**: Weather changes create magical 4-second transformations

### ⭐ **Skill Constellation Navigation**
- **3D Star Map**: Skills as floating stars with brightness based on proficiency
- **Smart Connections**: Lines showing relationships between technologies
- **Interactive Journey**: Click constellations to explore skill development stories
- **Achievement Unlocks**: New skills appear as meteors with celebration effects

### 👥 **Social Garden Features**
- **Anonymous Visitor Tracking**: See other explorers as gentle particle trails
- **Seed Planting**: Visitors can plant idea seeds that you can nurture into projects
- **Real-time Interactions**: Live updates when someone explores your garden
- **Privacy-First**: GDPR compliant with no personal data collection

---

## 🚀 **Quick Start**

### Prerequisites
- **Node.js 18+** and **npm 9+**
- **Python 3.11+** with **pip**
- **Docker** and **Docker Compose**
- **PostgreSQL 15+** and **Redis 7+**

### 1. Clone and Setup
```bash
git clone https://github.com/cameronopotter/digital-greenhouse.git
cd digital-greenhouse

# Install all dependencies
npm run setup
```

### 2. Configure Environment
```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys (GitHub token required, others optional)
nano .env
```

### 3. Start the Garden
```bash
# Start with Docker (recommended)
docker-compose up -d

# Or start manually
npm run dev
```

### 4. Visit Your Garden
- 🌱 **Frontend**: http://localhost:3000
- 🔌 **API Docs**: http://localhost:8000/docs
- 📊 **Monitoring**: http://localhost:3001 (Grafana: admin/admin123)

---

## 🏗️ **Architecture Overview**

```
🌍 3D DIGITAL GARDEN ECOSYSTEM

┌─────────────────────────────────────────────────┐
│                Frontend                         │
│         React 18 + Three.js                    │
│    🎨 3D Garden  🌤️ Weather  ⭐ Constellations   │
└─────────────┬───────────────────────────────────┘
              │ WebSocket + REST API
┌─────────────▼───────────────────────────────────┐
│              FastAPI Backend                   │
│  📊 Analytics  🔄 Real-time  🌱 Growth Engine   │
└─────┬───────┬───────┬─────────────────────┬─────┘
      │       │       │                     │
   ┌──▼──┐ ┌─▼────┐ ┌─▼──────┐        ┌────▼─────┐
   │ DB  │ │Redis │ │External│        │Background│
   │     │ │Cache │ │  APIs  │        │  Tasks   │
   └─────┘ └──────┘ └────────┘        └──────────┘
```

### **Tech Stack**

**Frontend (3D Garden Interface)**
- **React 18** - Concurrent features with Suspense
- **Three.js/React Three Fiber** - 3D rendering and animations
- **TypeScript 5.0** - Type safety throughout
- **Vite** - Lightning fast development
- **Zustand** - Lightweight state management
- **Material-UI** - Accessible UI components
- **Framer Motion** - Smooth animations

**Backend (Garden Orchestrator)**
- **FastAPI** - Modern Python API framework
- **SQLAlchemy 2.0** - Async database ORM
- **PostgreSQL 15** - Robust data storage
- **Redis** - Multi-layer caching
- **WebSockets** - Real-time communication
- **Celery** - Background task processing

**External Integrations**
- **GitHub API** - Repository and commit data
- **Spotify API** - Music mood influence (optional)
- **OpenWeather API** - Real weather effects (optional)
- **WakaTime API** - Coding time tracking (optional)

---

## 🛠️ **Development Guide**

### **Project Structure**
```
digital-greenhouse/
├── frontend/                 # React 3D garden interface
│   ├── src/
│   │   ├── components/      # 3D components and UI
│   │   ├── stores/          # State management
│   │   ├── hooks/           # Custom React hooks
│   │   ├── services/        # API communication
│   │   └── types/           # TypeScript definitions
│   └── tests/               # Frontend testing
├── backend/                  # FastAPI garden orchestrator
│   ├── app/
│   │   ├── api/            # REST API endpoints
│   │   ├── models/         # Database models
│   │   ├── services/       # Business logic
│   │   ├── integrations/   # External API clients
│   │   └── core/           # Core configuration
│   └── tests/              # Backend testing
├── docker/                   # Container configurations
├── monitoring/               # Grafana dashboards
└── scripts/                  # Development utilities
```

### **Development Commands**
```bash
# Start development environment
npm run dev                   # Start both frontend and backend
npm run dev:frontend         # Frontend only
npm run dev:backend          # Backend only

# Testing
npm run test                 # Run all tests
npm run test:frontend        # Frontend tests only
npm run test:backend         # Backend tests only
npm run test:e2e            # End-to-end tests
npm run test:accessibility  # Accessibility tests

# Code Quality
npm run lint                 # Lint all code
npm run format              # Format all code
npm run type-check          # TypeScript type checking

# Database
npm run migrate             # Run database migrations
npm run seed                # Seed with sample data
```

---

## 🔌 **API Integration Setup**

### **Required: GitHub Integration**
1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Create token with `repo`, `user:read` permissions
3. Add to `.env`: `GITHUB_TOKEN=ghp_your_token_here`

### **Optional: Enhanced Features**

**Spotify Music Mood Integration**
```bash
# 1. Create Spotify App at https://developer.spotify.com
# 2. Add to .env:
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
```

**Weather Atmosphere Integration**
```bash
# 1. Get free API key from https://openweathermap.org
# 2. Add to .env:
OPENWEATHER_API_KEY=your_api_key
WEATHER_LOCATION=37.7749,-122.4194  # Your coordinates
```

**Coding Time Integration**
```bash
# 1. Sign up at https://wakatime.com
# 2. Add to .env:
WAKATIME_API_KEY=waka_your_key
```

---

## 🎨 **Customization Guide**

### **Garden Themes**
Customize your garden's visual identity:

```typescript
// frontend/src/stores/gardenStore.ts
const customTheme = {
  colors: {
    primary: '#your-brand-color',
    accent: '#your-accent-color',
    background: '#your-bg-color'
  },
  seasons: {
    spring: { /* custom spring palette */ },
    summer: { /* custom summer palette */ }
  }
}
```

### **Project Plant Types**
Define how different projects appear:

```python
# backend/app/models/project.py
PLANT_TYPE_MAPPING = {
    'web-app': 'flowering_tree',
    'library': 'oak_tree',
    'mobile-app': 'palm_tree',
    'api': 'vine',
    'documentation': 'grass'
}
```

### **Weather Moods**
Customize how activities influence garden atmosphere:

```python
# backend/app/services/mood_engine.py
MOOD_MAPPING = {
    'intense_coding': ('stormy', 0.8),
    'creative_flow': ('aurora', 0.9),
    'learning': ('cloudy', 0.6),
    'debugging': ('foggy', 0.5)
}
```

---

## 📊 **Analytics & Insights**

### **Built-in Analytics Dashboard**
Access comprehensive insights at http://localhost:3001:

- **Garden Health**: Project growth rates and engagement
- **Visitor Journey**: Anonymous interaction patterns
- **Performance Metrics**: 3D rendering and API response times
- **Growth Trends**: Project evolution and milestone tracking
- **Weather Patterns**: Mood and productivity correlations

### **Custom Analytics**
Add your own tracking:

```typescript
// frontend/src/services/analytics.ts
trackCustomEvent('project_interaction', {
  project_id: 'your-project',
  interaction_type: 'detailed_view',
  duration: 45000
});
```

---

## 🛡️ **Privacy & Security**

### **Privacy-First Design**
- **No Personal Data**: Only anonymous interaction tracking
- **IP Hashing**: Visitor IPs are cryptographically hashed
- **GDPR Compliant**: Built-in consent management
- **Data Retention**: Automatic cleanup after 365 days
- **Transparent**: Open source with auditable privacy practices

### **Security Features**
- **Rate Limiting**: Protect against abuse
- **CORS Protection**: Secure cross-origin requests
- **Input Validation**: Comprehensive data sanitization
- **Security Headers**: HTTPS, CSP, XSS protection
- **Vulnerability Scanning**: Automated security audits

---

## 🚀 **Deployment**

### **Production Deployment**
```bash
# 1. Configure production environment
cp .env.example .env.production
# Edit with production values

# 2. Build and deploy
docker-compose -f docker-compose.production.yml up -d

# 3. Run database migrations
docker-compose exec backend alembic upgrade head

# 4. Setup monitoring
./scripts/setup-monitoring.sh
```

### **Recommended Hosting**
- **Frontend**: Vercel, Netlify, or AWS CloudFront
- **Backend**: Railway, Heroku, or AWS ECS
- **Database**: Neon, Supabase, or AWS RDS
- **Cache**: Upstash Redis or AWS ElastiCache

---

## 🧪 **Testing**

### **Comprehensive Test Suite**
- **90%+ Coverage**: Critical components thoroughly tested
- **Performance Testing**: 3D rendering and API benchmarks
- **Accessibility Testing**: WCAG 2.1 AA compliance
- **Cross-browser Testing**: Chrome, Firefox, Safari, Edge
- **Mobile Testing**: iOS and Android compatibility
- **Load Testing**: 100+ concurrent users

### **Running Tests**
```bash
# Unit and integration tests
npm run test

# Performance benchmarks
npm run test:performance

# Accessibility compliance
npm run test:accessibility

# Visual regression
npm run test:visual

# Load testing
npm run test:load
```

---

## 🤝 **Contributing**

We welcome contributions to make the Digital Greenhouse even more magical!

### **Development Workflow**
1. **Fork** the repository
2. **Create** a feature branch: `git checkout -b feature/amazing-feature`
3. **Follow** the coding standards: `npm run lint && npm run format`
4. **Test** your changes: `npm run test`
5. **Commit** with conventional commits: `git commit -m "feat: add amazing feature"`
6. **Push** and create a **Pull Request**

### **Code Standards**
- **TypeScript** for all frontend code
- **Type hints** for all Python code
- **Test coverage** for new features
- **Accessibility** considerations
- **Performance** impact assessment

---

## 📈 **Performance**

### **Optimization Features**
- **Adaptive Quality**: Automatically adjusts based on device performance
- **Level of Detail**: Reduces complexity for distant objects  
- **Frustum Culling**: Only renders visible elements
- **Bundle Splitting**: Lazy loading for optimal initial load
- **Service Worker**: Offline functionality and caching
- **WebGL Optimization**: Efficient GPU usage

### **Performance Targets**
- ✅ **<2s Initial Load** - Optimized bundle and lazy loading
- ✅ **60fps Animations** - Smooth 3D rendering on desktop
- ✅ **30fps Mobile** - Adapted complexity for mobile devices
- ✅ **<100ms API Response** - Fast backend with caching
- ✅ **95+ Lighthouse Score** - Excellent Core Web Vitals

---

## 🎯 **Roadmap**

### **Phase 1: Foundation** ✅ *Complete*
- [x] 3D garden environment with project plants
- [x] Real-time GitHub integration and growth system
- [x] Weather mood system with particle effects
- [x] Skill constellation navigation
- [x] Privacy-compliant visitor tracking

### **Phase 2: Enhanced Interactivity** 🔄 *In Progress*
- [ ] AI-powered project recommendations
- [ ] Advanced visitor collaboration features
- [ ] VR/AR support for immersive exploration
- [ ] Advanced analytics and insights
- [ ] Mobile app companion

### **Phase 3: Community Features** 📋 *Planned*
- [ ] Multi-user garden networks
- [ ] Project collaboration visualization
- [ ] Mentorship and learning paths
- [ ] Garden template marketplace
- [ ] Advanced customization tools

---

## 📄 **License**

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 🙋 **Support & Community**

### **Getting Help**
- 📖 **Documentation**: Comprehensive guides and API docs
- 🐛 **Issues**: Bug reports and feature requests on GitHub
- 💬 **Discussions**: Community forum for questions and ideas
- 📧 **Email**: Direct support for complex issues

### **Community**
- 🌟 **Star** the repo if you find it interesting
- 🐦 **Share** on social media with #DigitalGreenhouse
- 🤝 **Contribute** to make it even more amazing
- 💡 **Suggest** new features and improvements

---

## 🎉 **Acknowledgments**

Special thanks to:
- **Three.js Community** - Amazing 3D web graphics framework
- **React Three Fiber** - Beautiful React integration for Three.js
- **FastAPI Community** - Modern Python web framework
- **Open Source Contributors** - Making the web more creative and accessible

---

<div align="center">

**🌱 Start Growing Your Digital Garden Today! 🌱**

[**🚀 Deploy Now**](https://vercel.com/import/project?template=https://github.com/cameronopotter/digital-greenhouse) • [**📖 Documentation**](./docs/) • [**🎮 Live Demo**](https://digital-greenhouse.vercel.app)

Made with ❤️ and ☕ by [Cameron Potter](https://github.com/cameronopotter)

</div>