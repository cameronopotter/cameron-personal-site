import React, { useRef, useEffect } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import { Vector3 } from 'three'
import type { CameraControllerProps, CameraState } from '@/types'

export const CameraController: React.FC<CameraControllerProps> = ({
  state,
  onStateChange,
  autoRotate
}) => {
  const controlsRef = useRef<any>(null!)
  const { camera } = useThree()

  // Update camera position when state changes
  useEffect(() => {
    if (controlsRef.current) {
      controlsRef.current.object.position.copy(state.position)
      controlsRef.current.target.copy(state.target)
      controlsRef.current.update()
    }
  }, [state.position, state.target])

  // Handle camera mode changes
  useEffect(() => {
    if (controlsRef.current) {
      const controls = controlsRef.current
      
      switch (state.mode) {
        case 'orbit':
          controls.enableRotate = true
          controls.enablePan = true
          controls.enableZoom = true
          controls.autoRotate = autoRotate
          controls.autoRotateSpeed = 0.5
          break
          
        case 'fly':
          controls.enableRotate = true
          controls.enablePan = true
          controls.enableZoom = true
          controls.autoRotate = false
          break
          
        case 'focus':
          controls.enableRotate = false
          controls.enablePan = false
          controls.enableZoom = true
          controls.autoRotate = false
          break
          
        case 'cinematic':
          controls.enableRotate = false
          controls.enablePan = false
          controls.enableZoom = false
          controls.autoRotate = true
          controls.autoRotateSpeed = 0.2
          break
      }
    }
  }, [state.mode, autoRotate])

  // Sync state changes back to parent
  const handleChange = () => {
    if (controlsRef.current && onStateChange) {
      const controls = controlsRef.current
      onStateChange({
        position: controls.object.position.clone(),
        target: controls.target.clone()
      })
    }
  }

  return (
    <OrbitControls
      ref={controlsRef}
      makeDefault
      minDistance={state.constraints.minDistance}
      maxDistance={state.constraints.maxDistance}
      enablePan={state.constraints.enablePan}
      enableZoom={state.constraints.enableZoom}
      enableRotate={state.constraints.enableRotate}
      enableDamping
      dampingFactor={0.05}
      screenSpacePanning={false}
      minPolarAngle={Math.PI / 6}
      maxPolarAngle={Math.PI - Math.PI / 6}
      onChange={handleChange}
      onEnd={handleChange}
    />
  )
}