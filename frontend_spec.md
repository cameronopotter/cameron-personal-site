# Frontend Specification - Digital Greenhouse
## Interactive React Application with 3D Garden Ecosystem

---

## 🏗️ Technical Stack

### Core Technologies
```json
{
  "react": "^18.2.0",
  "typescript": "^5.0.0",
  "@react-three/fiber": "^8.15.0",
  "@react-three/drei": "^9.88.0",
  "three": "^0.157.0",
  "framer-motion": "^10.16.0",
  "zustand": "^4.4.0",
  "@mui/material": "^5.14.0",
  "d3": "^7.8.0",
  "leva": "^0.9.35",
  "react-spring": "^9.7.0"
}
```

### Additional Libraries
- **@react-three/postprocessing** - Visual effects and shaders
- **@react-three/xr** - Future VR/AR support
- **react-intersection-observer** - Scroll-based animations
- **react-hotkeys-hook** - Keyboard navigation
- **workbox** - PWA capabilities

---

## 🎨 UI/UX Design System

### Visual Hierarchy

#### 1. **Immersive Canvas Layer** (z-index: 1)
```
🌍 3D Garden Environment
├── 🌱 Project Plants (Interactive 3D objects)
├── 🌤️ Weather System (Particle effects)
├── ⭐ Skill Constellations (Floating elements)
└── 🎭 Atmospheric Background (WebGL shaders)
```

#### 2. **Interface Overlay Layer** (z-index: 10)
```
🎯 Navigation & Controls
├── 🧭 Compass Navigation (Fixed position)
├── 🔍 Search & Filter Panel (Slide-in)
├── 📊 Stats Dashboard (Collapsible)
└── 💬 Interaction Tooltips (Context-aware)
```

#### 3. **Modal Content Layer** (z-index: 100)
```
📋 Detailed Views
├── 🏠 Project Deep-Dive Pods
├── 📜 Blog/Article Reader
├── 🎵 Music Mood Controller
└── 🛠️ Settings Panel
```

---

## 🌟 Component Architecture

### Core Layout Components

#### `<GardenCanvas />`
```tsx
interface GardenCanvasProps {
  season: Season;
  weatherState: WeatherState;
  projects: Project[];
  interactionMode: 'explore' | 'focus' | 'create';
}

// Features:
// - Three.js scene management
// - Camera controls and smooth transitions  
// - Lighting system that responds to mood/time
// - Particle systems for atmospheric effects
```

#### `<ProjectPlant />`
```tsx
interface ProjectPlantProps {
  project: Project;
  growthStage: 'seed' | 'sprout' | 'growing' | 'blooming' | 'mature';
  interactionLevel: number;
  position: [number, number, number];
  onInteract: (type: InteractionType) => void;
}

// Growth visualization:
// 🌰 Seed → 🌱 Sprout → 🌿 Growing → 🌸 Blooming → 🌳 Mature
```

#### `<WeatherSystem />`
```tsx
interface WeatherSystemProps {
  mood: 'stormy' | 'sunny' | 'cloudy' | 'aurora' | 'starry';
  intensity: number;
  timeOfDay: 'dawn' | 'day' | 'dusk' | 'night';
  seasonalInfluence: number;
}

// Weather effects:
// ⛈️ Stormy = Intense coding sessions
// ☀️ Sunny = Productive, happy periods  
// ☁️ Cloudy = Learning/research phases
// 🌌 Aurora = Creative breakthroughs
// ✨ Starry = Quiet reflection times
```

---

## 🎯 Interactive Features Implementation

### 1. **Seed Planting System**
```tsx
// User interaction creates new project ideas
const SeedPlanter = () => {
  const [isPlanting, setIsPlanting] = useState(false);
  const [seedPosition, setSeedPosition] = useState<Vector3>();
  
  const handlePlantSeed = (position: Vector3, idea: string) => {
    // Create floating seed animation
    // Store idea in backend
    // Begin growth simulation
  };
};
```

### 2. **Growth Animation System**
```tsx
// Projects grow based on real data
const useProjectGrowth = (project: Project) => {
  const growthStage = useMemo(() => {
    const commits = project.githubData?.commits || 0;
    const age = daysSince(project.createdDate);
    const engagement = project.analytics?.interactions || 0;
    
    return calculateGrowthStage(commits, age, engagement);
  }, [project]);
  
  const { size, opacity, complexity } = useSpring({
    size: growthStage * 0.2,
    opacity: Math.min(growthStage * 0.3, 1),
    complexity: growthStage,
  });
};
```

### 3. **Skill Constellation Navigation**
```tsx
// Skills as interactive star map
const SkillConstellation = ({ skills }: { skills: Skill[] }) => {
  const positions = useMemo(() => 
    generateConstellationLayout(skills), [skills]
  );
  
  return (
    <group>
      {skills.map((skill, index) => (
        <SkillStar
          key={skill.id}
          skill={skill}
          position={positions[index]}
          brightness={skill.proficiency}
          connections={getSkillConnections(skill, skills)}
        />
      ))}
    </group>
  );
};
```

---

## 🎨 Visual Design Specifications

### Color System Evolution
```css
/* Spring Theme */
:root[data-season="spring"] {
  --primary-green: #4CAF50;
  --accent-blue: #2196F3;
  --growth-light: #8BC34A;
  --soil-brown: #795548;
  --sky-gradient: linear-gradient(180deg, #87CEEB 0%, #98FB98 100%);
}

/* Summer Theme */
:root[data-season="summer"] {
  --primary-green: #2E7D32;
  --accent-orange: #FF9800;
  --bloom-purple: #9C27B0;
  --soil-brown: #6D4C41;
  --sky-gradient: linear-gradient(180deg, #FFD54F 0%, #FF8A65 100%);
}

/* Autumn Theme */
:root[data-season="autumn"] {
  --primary-gold: #FFC107;
  --accent-red: #F44336;
  --leaf-orange: #FF5722;
  --soil-brown: #8D6E63;
  --sky-gradient: linear-gradient(180deg, #FFAB91 0%, #BCAAA4 100%);
}

/* Winter Theme */
:root[data-season="winter"] {
  --primary-blue: #1976D2;
  --accent-silver: #9E9E9E;
  --snow-white: #FAFAFA;
  --soil-brown: #424242;
  --sky-gradient: linear-gradient(180deg, #B0BEC5 0%, #263238 100%);
}
```

### Typography System
```css
/* Variable font for growing headers */
@font-face {
  font-family: 'GrowingType';
  src: url('./fonts/GrowingType-Variable.woff2');
  font-variation-settings: 'wght' 400, 'grow' 0;
}

.project-title {
  font-family: 'GrowingType', sans-serif;
  font-variation-settings: 'grow' var(--growth-level);
  transition: font-variation-settings 0.8s ease;
}

/* Code blocks with garden theme */
.code-block {
  background: linear-gradient(135deg, #1a1a1a 0%, #2d3748 100%);
  border-left: 3px solid var(--primary-green);
  border-radius: 8px;
  font-family: 'JetBrains Mono', monospace;
}
```

---

## 🔄 State Management Architecture

### Zustand Store Structure
```tsx
interface GardenState {
  // Core garden state
  season: Season;
  weather: WeatherState;
  timeOfDay: TimeOfDay;
  
  // User interaction state
  selectedProject: Project | null;
  navigationMode: 'explore' | 'focus' | 'create';
  visitorSession: VisitorSession;
  
  // Real-time data
  projects: Project[];
  skills: Skill[];
  realtimeData: RealtimeData;
  
  // UI state
  isLoading: boolean;
  activeModal: string | null;
  cameraPosition: Vector3;
  
  // Actions
  updateWeather: (weather: WeatherState) => void;
  selectProject: (project: Project) => void;
  plantSeed: (position: Vector3, idea: string) => void;
  updateRealtimeData: (data: RealtimeData) => void;
}
```

### Data Flow Pattern
```
📡 External APIs → 🏪 Zustand Store → ⚛️ React Components → 🎨 Three.js Scene
     ↑                                                              ↓
📊 Backend API ← 🔄 WebSocket Updates ← 🎯 User Interactions ← 🖱️ Event Handlers
```

---

## 📱 Responsive Design Strategy

### Breakpoint System
```css
/* Mobile First Approach */
.garden-canvas {
  /* Mobile: Simplified 2D view with key interactions */
  @media (max-width: 768px) {
    transform-style: flat;
    --complexity-level: 1;
  }
  
  /* Tablet: Reduced 3D complexity */
  @media (min-width: 769px) and (max-width: 1024px) {
    --complexity-level: 2;
  }
  
  /* Desktop: Full 3D experience */
  @media (min-width: 1025px) {
    --complexity-level: 3;
  }
}
```

### Progressive Enhancement
1. **Level 1 (Mobile)** - 2D garden with essential interactions
2. **Level 2 (Tablet)** - Limited 3D with touch optimizations
3. **Level 3 (Desktop)** - Full 3D experience with advanced effects
4. **Level 4 (High-end)** - Enhanced shaders and particle systems

---

## 🎮 Interaction Design Patterns

### Gesture Controls
```tsx
// Touch/mouse interaction patterns
const InteractionGestures = {
  // Plant selection
  tap: (position) => selectPlant(position),
  
  // Camera navigation  
  drag: (delta) => rotateCameraAround(delta),
  pinch: (scale) => adjustCameraZoom(scale),
  
  // Seed planting
  longPress: (position) => showSeedPlantingInterface(position),
  
  // Quick actions
  doubleTab: (plant) => enterProjectDeepDive(plant),
  swipe: (direction) => navigateToNextProject(direction),
};
```

### Keyboard Navigation
```tsx
const useKeyboardControls = () => {
  useHotkeys('space', () => toggleNavigationMode());
  useHotkeys('enter', () => enterSelectedProject());
  useHotkeys('escape', () => exitCurrentView());
  useHotkeys('arrow keys', (key) => navigateGarden(key));
  useHotkeys('1-9', (num) => quickSelectProject(num));
};
```

---

## 🌈 Animation & Transition System

### Micro-Interactions
```tsx
// Hover effects for plants
const PlantHoverEffect = {
  scale: { from: 1, to: 1.1, duration: 0.3 },
  glow: { from: 0, to: 0.8, duration: 0.2 },
  particles: { spawn: 'growth-sparkles', duration: 1.0 },
  sound: 'gentle-rustle.wav'
};

// Seasonal transition animations
const SeasonTransition = {
  duration: 4000, // 4 seconds
  easing: 'cubic-bezier(0.4, 0, 0.2, 1)',
  stages: [
    { percent: 0, effect: 'fade-current-season' },
    { percent: 25, effect: 'shift-lighting' },
    { percent: 50, effect: 'change-colors' },
    { percent: 75, effect: 'update-particles' },
    { percent: 100, effect: 'reveal-new-season' }
  ]
};
```

### Performance Optimizations
```tsx
// Level-of-detail system for 3D objects
const useLOD = (distance: number, complexity: number) => {
  return useMemo(() => {
    if (distance > 50) return 'low'; // Simple geometry
    if (distance > 20) return 'medium'; // Moderate detail  
    return 'high'; // Full detail
  }, [distance, complexity]);
};

// Frustum culling for off-screen elements
const useVisibilityOptimization = () => {
  // Only render objects visible to camera
  // Reduce animation complexity for distant objects
  // Pause animations for hidden elements
};
```

---

## 🎯 Accessibility Features

### WCAG 2.1 AA Compliance
```tsx
// Screen reader support for 3D garden
const GardenA11y = () => (
  <div role="application" aria-label="Interactive project garden">
    <div aria-live="polite" id="garden-announcements">
      {selectedProject && `Now viewing ${selectedProject.name}`}
    </div>
    
    {/* Keyboard-accessible project list */}
    <nav aria-label="Project navigation" className="sr-only">
      {projects.map(project => (
        <button
          key={project.id}
          onClick={() => focusProject(project)}
          aria-describedby={`project-${project.id}-desc`}
        >
          {project.name}
        </button>
      ))}
    </nav>
  </div>
);

// High contrast mode support
const useA11yMode = () => {
  const [highContrast, setHighContrast] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(
    window.matchMedia('(prefers-reduced-motion: reduce)').matches
  );
  
  // Adapt 3D complexity based on accessibility preferences
  const complexityLevel = reducedMotion ? 1 : 3;
};
```

---

## 🚀 Performance Targets

### Core Web Vitals
- **LCP (Largest Contentful Paint)** < 2.5s
- **FID (First Input Delay)** < 100ms  
- **CLS (Cumulative Layout Shift)** < 0.1
- **Frame Rate** Consistent 60fps (30fps on mobile)

### Bundle Size Optimization
- **Initial Bundle** < 200KB gzipped
- **3D Assets** Lazy loaded, < 500KB total
- **Code Splitting** Route-based + component-based
- **Tree Shaking** Eliminate unused Three.js modules

This frontend specification creates a truly unique, interactive experience that stands out from traditional portfolio sites while maintaining excellent performance and accessibility standards.