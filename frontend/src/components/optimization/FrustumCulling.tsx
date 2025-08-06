import React, { useRef, useMemo } from 'react'
import { useFrame, useThree } from '@react-three/fiber'
import { Frustum, Matrix4, Vector3, Group } from 'three'

interface FrustumCullingProps {
  children: React.ReactNode
  margin?: number // Extra margin around frustum for smoother transitions
}

interface CulledChild {
  element: React.ReactNode
  position: Vector3
  visible: boolean
  index: number
}

export const FrustumCulling: React.FC<FrustumCullingProps> = ({ 
  children, 
  margin = 5 
}) => {
  const groupRef = useRef<Group>(null!)
  const { camera, gl } = useThree()
  
  const frustum = useMemo(() => new Frustum(), [])
  const projScreenMatrix = useMemo(() => new Matrix4(), [])
  
  // Track children with their positions and visibility
  const culledChildren = useMemo(() => {
    return React.Children.map(children, (child, index) => {
      let position = new Vector3(0, 0, 0)
      
      if (React.isValidElement(child) && child.props.position) {
        if (Array.isArray(child.props.position)) {
          position.fromArray(child.props.position)
        } else if (child.props.position instanceof Vector3) {
          position.copy(child.props.position)
        }
      }
      
      return {
        element: child,
        position,
        visible: true,
        index
      }
    }) as CulledChild[]
  }, [children])

  useFrame(() => {
    // Update frustum from camera
    projScreenMatrix.multiplyMatrices(camera.projectionMatrix, camera.matrixWorldInverse)
    frustum.setFromProjectionMatrix(projScreenMatrix)
    
    // Check each child against frustum
    culledChildren.forEach((child) => {
      if (!child.element || !React.isValidElement(child.element)) {
        child.visible = true
        return
      }
      
      // Create a bounding sphere around the child position
      const testPoint = child.position.clone()
      const boundingSphereRadius = margin
      
      // Test if the point is within the frustum (with margin)
      let isVisible = frustum.containsPoint(testPoint)
      
      // If not visible, test nearby points for objects that might be partially visible
      if (!isVisible) {
        const testPoints = [
          testPoint.clone().add(new Vector3(boundingSphereRadius, 0, 0)),
          testPoint.clone().add(new Vector3(-boundingSphereRadius, 0, 0)),
          testPoint.clone().add(new Vector3(0, boundingSphereRadius, 0)),
          testPoint.clone().add(new Vector3(0, -boundingSphereRadius, 0)),
          testPoint.clone().add(new Vector3(0, 0, boundingSphereRadius)),
          testPoint.clone().add(new Vector3(0, 0, -boundingSphereRadius))
        ]
        
        isVisible = testPoints.some(point => frustum.containsPoint(point))
      }
      
      child.visible = isVisible
      
      // Notify child component about visibility change for optimization
      if (React.isValidElement(child.element) && typeof child.element.props.onVisibilityChange === 'function') {
        child.element.props.onVisibilityChange(isVisible)
      }
    })
  })

  return (
    <group ref={groupRef}>
      {culledChildren.map((child) => {
        // Only render visible children
        if (!child.visible) return null
        
        // Clone element with frustum culling information
        if (React.isValidElement(child.element)) {
          return React.cloneElement(child.element as React.ReactElement<any>, {
            ...child.element.props,
            key: child.index,
            isCulled: false,
            frustumVisible: true
          })
        }
        
        return child.element
      })}
    </group>
  )
}