import React, { Suspense, useRef, useEffect, useMemo, useCallback } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { 
  PerspectiveCamera,
  OrbitControls,
  Environment,
  ContactShadows,
  Html,
  useProgress,
  Sky,
  Stars
} from '@react-three/drei'
// import { EffectComposer, Bloom, DepthOfField, Vignette } from '@react-three/postprocessing'
import { Vector3, Color, Fog } from 'three'
import { motion } from 'framer-motion'
import { Box, CircularProgress, Typography } from '@mui/material'
import { 
  useGardenStore, 
  useProjectsSelector, 
  useSkillsSelector, 
  useWeatherSelector, 
  useSettingsSelector,
  usePerformanceSelector
} from '@/stores/gardenStore'
import { ProjectPlant } from './ProjectPlant'
import { WeatherSystem } from './WeatherSystem'
import { SkillConstellation } from './SkillConstellation'
import { CameraController } from './CameraController'
import { Ground } from './Ground'
import { AtmosphereShader } from './shaders/AtmosphereShader'
import { LODManager } from './optimization/LODManager'
import { FrustumCulling } from './optimization/FrustumCulling'
import { PerformanceMonitor } from './optimization/PerformanceMonitor'
import type { GardenCanvasProps } from '@/types'

// Loading component for Suspense
const CanvasLoader: React.FC = () => {
  const { progress } = useProgress()
  
  return (
    <Html center>
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          gap: 2,
          p: 4,
          background: 'rgba(26, 26, 26, 0.9)',
          borderRadius: 2,
          backdropFilter: 'blur(10px)'
        }}
      >
        <CircularProgress 
          variant="determinate" 
          value={progress} 
          size={60}
          sx={{ color: '#4CAF50' }}
        />
        <Typography variant="body2" color="white">
          Growing garden... {Math.round(progress)}%
        </Typography>
      </Box>
    </Html>
  )
}

// Scene setup component
const Scene: React.FC = () => {
  const { scene, camera, gl } = useThree()
  const frameRef = useRef(0)
  
  const projects = useProjectsSelector()
  const skills = useSkillsSelector()
  const weather = useWeatherSelector()
  const settings = useSettingsSelector()
  const performance = usePerformanceSelector()
  
  const {
    season,
    selectedProject,
    selectedSkill,
    camera: cameraState,
    updatePerformanceMetrics,
    trackInteraction
  } = useGardenStore()
  
  // Performance monitoring
  useFrame((state, delta) => {
    frameRef.current += 1
    
    // Update performance metrics every 60 frames
    if (frameRef.current % 60 === 0) {
      const fps = Math.round(1 / delta)
      const renderTime = delta * 1000
      
      updatePerformanceMetrics({ 
        fps, 
        renderTime,
        memoryUsage: (performance as any)?.memory?.usedJSHeapSize || 0
      })
    }
    
    // Adaptive quality based on performance
    if (settings.complexityLevel > 1 && (1 / delta) < 45) {
      // Performance is suffering, consider reducing quality
      useGardenStore.getState().enableOptimizedMode()
    }
  })
  
  // Configure scene fog and background
  useEffect(() => {
    const fogColor = weather.lighting.ambient
    scene.fog = new Fog(fogColor, 10, 100)
    scene.background = null // Let Sky component handle background
  }, [scene, weather.lighting.ambient])
  
  // Seasonal color adjustments
  const seasonalColors = useMemo(() => {
    const colorMaps = {
      spring: { primary: '#4CAF50', secondary: '#8BC34A', accent: '#2196F3' },
      summer: { primary: '#2E7D32', secondary: '#FF9800', accent: '#9C27B0' },
      autumn: { primary: '#FFC107', secondary: '#F44336', accent: '#FF5722' },
      winter: { primary: '#1976D2', secondary: '#9E9E9E', accent: '#FAFAFA' }
    }
    return colorMaps[season]
  }, [season])
  
  // Handle clicks on empty space (for seed planting)
  const handleSceneClick = useCallback((event: any) => {
    if (event.intersections.length === 0) {
      const position: [number, number, number] = [
        event.point.x,
        0,
        event.point.z
      ]
      
      trackInteraction({
        type: 'click',
        target: 'ground',
        position,
        metadata: { 
          potentialSeedLocation: true,
          season,
          weather: weather.mood 
        }
      })
      
      // Could trigger seed planting UI here
    }
  }, [trackInteraction, season, weather.mood])
  
  return (
    <>
      {/* Lighting Setup */}
      <ambientLight 
        intensity={weather.lighting.ambient ? 0.4 : 0.6} 
        color={weather.lighting.ambient || '#ffffff'} 
      />
      <directionalLight
        position={[10, 20, 10]}
        intensity={1.2}
        color={weather.lighting.directional || '#ffffff'}
        castShadow={weather.lighting.shadows && settings.complexityLevel > 2}
        shadow-mapSize={settings.complexityLevel > 3 ? 2048 : 1024}
        shadow-camera-near={1}
        shadow-camera-far={50}
        shadow-camera-left={-20}
        shadow-camera-right={20}
        shadow-camera-top={20}
        shadow-camera-bottom={-20}
      />
      
      {/* Sky and Environment */}
      {settings.complexityLevel > 1 && (
        <>
          <Sky
            distance={450000}
            sunPosition={[0, 1, 0]}
            inclination={weather.timeOfDay === 'night' ? 0.8 : 0.1}
            azimuth={0.25}
          />
          {weather.timeOfDay === 'night' && (
            <Stars
              radius={300}
              depth={60}
              count={5000}
              factor={7}
              saturation={0}
              fade
              speed={1}
            />
          )}
        </>
      )}
      
      {/* Environment Map */}
      {settings.complexityLevel > 2 && (
        <Environment
          preset={weather.timeOfDay === 'night' ? 'night' : 'dawn'}
          background={false}
        />
      )}
      
      {/* Ground */}
      <Ground 
        size={100}
        season={season}
        weather={weather}
        complexityLevel={settings.complexityLevel}
        onClick={handleSceneClick}
      />
      
      {/* Contact Shadows */}
      {settings.complexityLevel > 2 && (
        <ContactShadows
          position={[0, -0.1, 0]}
          opacity={0.4}
          scale={50}
          blur={2}
          far={10}
        />
      )}
      
      {/* Performance-aware rendering */}
      <LODManager complexityLevel={settings.complexityLevel}>
        <FrustumCulling>
          {/* Project Plants */}
          {projects.map((project) => (
            <ProjectPlant
              key={project.id}
              project={project}
              isSelected={selectedProject?.id === project.id}
              level={settings.complexityLevel}
              onInteract={(type) => {
                trackInteraction({
                  type,
                  target: project.id,
                  position: project.position,
                  metadata: { 
                    projectName: project.name,
                    growthStage: project.growthStage 
                  }
                })
                
                if (type === 'click') {
                  useGardenStore.getState().selectProject(project)
                }
              }}
            />
          ))}
          
          {/* Skill Constellation */}
          <SkillConstellation
            skills={skills}
            selectedSkill={selectedSkill}
            onSkillSelect={(skill) => useGardenStore.getState().selectSkill(skill)}
            visible={settings.complexityLevel > 1}
          />
        </FrustumCulling>
      </LODManager>
      
      {/* Weather Effects */}
      {settings.particlesEnabled && (
        <WeatherSystem
          weather={weather}
          enabled={settings.particlesEnabled}
          intensity={weather.intensity * (settings.complexityLevel / 4)}
        />
      )}
      
      {/* Atmosphere Shader */}
      {settings.complexityLevel > 3 && (
        <AtmosphereShader
          season={season}
          weather={weather}
          timeOfDay={weather.timeOfDay}
        />
      )}
      
      {/* Post-processing Effects - Disabled for compatibility */}
      {/* {settings.complexityLevel > 2 && (
        <EffectComposer>
          <Bloom
            intensity={0.5}
            luminanceThreshold={0.9}
            luminanceSmoothing={0.9}
            height={300}
          />
          {selectedProject && (
            <DepthOfField
              focusDistance={0.02}
              focalLength={0.005}
              bokehScale={3}
            />
          )}
          <Vignette
            offset={0.5}
            darkness={0.5}
          />
        </EffectComposer>
      )} */}
    </>
  )
}

// Main Canvas Component
export const GardenCanvas: React.FC<GardenCanvasProps> = ({
  className,
  onProjectSelect,
  onSkillSelect
}) => {
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const settings = useSettingsSelector()
  const performance = usePerformanceSelector()
  
  // Handle project selection callback
  useEffect(() => {
    if (onProjectSelect) {
      const unsubscribe = useGardenStore.subscribe(
        (state) => state.selectedProject,
        (project) => project && onProjectSelect(project)
      )
      return unsubscribe
    }
  }, [onProjectSelect])
  
  // Handle skill selection callback  
  useEffect(() => {
    if (onSkillSelect) {
      const unsubscribe = useGardenStore.subscribe(
        (state) => state.selectedSkill,
        (skill) => skill && onSkillSelect(skill)
      )
      return unsubscribe
    }
  }, [onSkillSelect])
  
  // Canvas configuration based on complexity level
  const canvasConfig = useMemo(() => {
    const configs = {
      1: { 
        shadows: false, 
        antialias: false, 
        alpha: false, 
        powerPreference: 'high-performance',
        pixelRatio: Math.min(window.devicePixelRatio, 1)
      },
      2: { 
        shadows: true, 
        antialias: false, 
        alpha: true, 
        powerPreference: 'high-performance',
        pixelRatio: Math.min(window.devicePixelRatio, 1.5)
      },
      3: { 
        shadows: true, 
        antialias: true, 
        alpha: true, 
        powerPreference: 'high-performance',
        pixelRatio: Math.min(window.devicePixelRatio, 2)
      },
      4: { 
        shadows: true, 
        antialias: true, 
        alpha: true, 
        powerPreference: 'high-performance',
        pixelRatio: Math.min(window.devicePixelRatio, 3),
        toneMapping: true
      }
    }
    return configs[settings.complexityLevel as keyof typeof configs] || configs[3]
  }, [settings.complexityLevel])
  
  return (
    <motion.div
      className={className}
      style={{ 
        width: '100vw', 
        height: '100vh', 
        position: 'relative',
        overflow: 'hidden'
      }}
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1.5, ease: 'easeOut' }}
    >
      <Canvas
        ref={canvasRef}
        {...canvasConfig}
        gl={{ 
          antialias: canvasConfig.antialias,
          alpha: canvasConfig.alpha,
          powerPreference: canvasConfig.powerPreference as WebGLPowerPreference,
          stencil: false,
          depth: true,
          premultipliedAlpha: true,
          preserveDrawingBuffer: false
        }}
        camera={{
          fov: 75,
          near: 0.1,
          far: 1000,
          position: [0, 10, 15]
        }}
        dpr={canvasConfig.pixelRatio}
        performance={{ min: 0.5 }}
        frameloop={performance.isOptimizedMode ? 'demand' : 'always'}
      >
        {/* Camera Controls */}
        <CameraController
          state={useGardenStore.getState().camera}
          onStateChange={(newState) => {
            useGardenStore.getState().setCameraPosition(
              newState.position!,
              newState.target
            )
            if (newState.mode) {
              useGardenStore.getState().setCameraMode(newState.mode)
            }
          }}
          autoRotate={settings.autoRotate}
        />
        
        {/* Main Scene */}
        <Suspense fallback={<CanvasLoader />}>
          <Scene />
        </Suspense>
        
        {/* Performance Monitor Component */}
        <PerformanceMonitor />
      </Canvas>
      
      {/* Canvas overlay for accessibility */}
      <div
        style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          pointerEvents: 'none',
          zIndex: 1
        }}
        aria-hidden="true"
      />
    </motion.div>
  )
}