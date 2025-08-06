import React, { useRef, useMemo } from 'react'
import { useFrame } from '@react-three/fiber'
import { ShaderMaterial, Vector3, Color, BackSide } from 'three'
import type { Season, WeatherState, TimeOfDay } from '@/types'

interface AtmosphereShaderProps {
  season: Season
  weather: WeatherState
  timeOfDay: TimeOfDay
}

const vertexShader = `
  varying vec3 vWorldPosition;
  varying vec3 vNormal;
  
  void main() {
    vNormal = normalize(normalMatrix * normal);
    vec4 worldPosition = modelMatrix * vec4(position, 1.0);
    vWorldPosition = worldPosition.xyz;
    
    gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
  }
`

const fragmentShader = `
  uniform float time;
  uniform float season;
  uniform float weather;
  uniform float timeOfDay;
  uniform vec3 fogColor;
  uniform float fogDensity;
  uniform vec3 lightDirection;
  
  varying vec3 vWorldPosition;
  varying vec3 vNormal;
  
  // Simplex noise function
  vec3 mod289(vec3 x) {
    return x - floor(x * (1.0 / 289.0)) * 289.0;
  }
  
  vec4 mod289(vec4 x) {
    return x - floor(x * (1.0 / 289.0)) * 289.0;
  }
  
  vec4 permute(vec4 x) {
    return mod289(((x*34.0)+1.0)*x);
  }
  
  vec4 taylorInvSqrt(vec4 r) {
    return 1.79284291400159 - 0.85373472095314 * r;
  }
  
  float snoise(vec3 v) {
    const vec2 C = vec2(1.0/6.0, 1.0/3.0);
    const vec4 D = vec4(0.0, 0.5, 1.0, 2.0);
    
    vec3 i = floor(v + dot(v, C.yyy));
    vec3 x0 = v - i + dot(i, C.xxx);
    
    vec3 g = step(x0.yzx, x0.xyz);
    vec3 l = 1.0 - g;
    vec3 i1 = min(g.xyz, l.zxy);
    vec3 i2 = max(g.xyz, l.zxy);
    
    vec3 x1 = x0 - i1 + C.xxx;
    vec3 x2 = x0 - i2 + C.yyy;
    vec3 x3 = x0 - D.yyy;
    
    i = mod289(i);
    vec4 p = permute(permute(permute(
               i.z + vec4(0.0, i1.z, i2.z, 1.0))
             + i.y + vec4(0.0, i1.y, i2.y, 1.0))
             + i.x + vec4(0.0, i1.x, i2.x, 1.0));
    
    float n_ = 0.142857142857;
    vec3 ns = n_ * D.wyz - D.xzx;
    
    vec4 j = p - 49.0 * floor(p * ns.z * ns.z);
    
    vec4 x_ = floor(j * ns.z);
    vec4 y_ = floor(j - 7.0 * x_);
    
    vec4 x = x_ *ns.x + ns.yyyy;
    vec4 y = y_ *ns.x + ns.yyyy;
    vec4 h = 1.0 - abs(x) - abs(y);
    
    vec4 b0 = vec4(x.xy, y.xy);
    vec4 b1 = vec4(x.zw, y.zw);
    
    vec4 s0 = floor(b0)*2.0 + 1.0;
    vec4 s1 = floor(b1)*2.0 + 1.0;
    vec4 sh = -step(h, vec4(0.0));
    
    vec4 a0 = b0.xzyw + s0.xzyw*sh.xxyy;
    vec4 a1 = b1.xzyw + s1.xzyw*sh.zzww;
    
    vec3 p0 = vec3(a0.xy, h.x);
    vec3 p1 = vec3(a0.zw, h.y);
    vec3 p2 = vec3(a1.xy, h.z);
    vec3 p3 = vec3(a1.zw, h.w);
    
    vec4 norm = taylorInvSqrt(vec4(dot(p0,p0), dot(p1,p1), dot(p2, p2), dot(p3,p3)));
    p0 *= norm.x;
    p1 *= norm.y;
    p2 *= norm.z;
    p3 *= norm.w;
    
    vec4 m = max(0.6 - vec4(dot(x0,x0), dot(x1,x1), dot(x2,x2), dot(x3,x3)), 0.0);
    m = m * m;
    return 42.0 * dot(m*m, vec4(dot(p0,x0), dot(p1,x1), dot(p2,x2), dot(p3,x3)));
  }
  
  void main() {
    vec3 worldPos = vWorldPosition * 0.01;
    
    // Create atmospheric noise
    float noise1 = snoise(worldPos + time * 0.1);
    float noise2 = snoise(worldPos * 2.0 + time * 0.05);
    float noise3 = snoise(worldPos * 4.0 + time * 0.02);
    
    float combinedNoise = noise1 * 0.5 + noise2 * 0.3 + noise3 * 0.2;
    
    // Calculate height-based gradient
    float heightGradient = 1.0 - clamp((vWorldPosition.y + 10.0) / 40.0, 0.0, 1.0);
    
    // Seasonal color variations
    vec3 springColor = vec3(0.4, 0.8, 0.4);
    vec3 summerColor = vec3(0.8, 0.6, 0.2);
    vec3 autumnColor = vec3(0.8, 0.4, 0.2);
    vec3 winterColor = vec3(0.6, 0.7, 0.9);
    
    vec3 seasonalColor = mix(
      mix(springColor, summerColor, smoothstep(0.0, 1.0, season)),
      mix(autumnColor, winterColor, smoothstep(1.0, 2.0, season - 1.0)),
      step(1.0, season)
    );
    
    // Time of day variations
    float dayFactor = sin(timeOfDay * 3.14159);
    vec3 dayColor = seasonalColor;
    vec3 nightColor = seasonalColor * 0.3 + vec3(0.1, 0.1, 0.3);
    vec3 timeColor = mix(nightColor, dayColor, dayFactor);
    
    // Weather influence
    vec3 stormyColor = timeColor * 0.5 + vec3(0.2, 0.2, 0.3);
    vec3 sunnyColor = timeColor * 1.2;
    vec3 cloudyColor = timeColor * 0.8 + vec3(0.2, 0.2, 0.2);
    
    vec3 weatherColor = mix(
      mix(stormyColor, sunnyColor, smoothstep(0.0, 1.0, weather)),
      cloudyColor,
      smoothstep(2.0, 3.0, weather)
    );
    
    // Final color calculation
    float alpha = heightGradient * (0.1 + combinedNoise * 0.05);
    alpha *= fogDensity;
    
    vec3 finalColor = weatherColor + combinedNoise * 0.1;
    
    gl_FragColor = vec4(finalColor, alpha);
  }
`

export const AtmosphereShader: React.FC<AtmosphereShaderProps> = ({
  season,
  weather,
  timeOfDay
}) => {
  const materialRef = useRef<ShaderMaterial>(null!)

  const uniforms = useMemo(() => ({
    time: { value: 0 },
    season: { value: getSeasonValue(season) },
    weather: { value: getWeatherValue(weather.mood) },
    timeOfDay: { value: getTimeValue(timeOfDay) },
    fogColor: { value: weather.lighting.ambient || new Color('#87CEEB') },
    fogDensity: { value: weather.lighting.fogDensity || 0.01 },
    lightDirection: { value: new Vector3(1, 1, 1).normalize() }
  }), [season, weather, timeOfDay])

  useFrame((state) => {
    if (materialRef.current) {
      materialRef.current.uniforms.time.value = state.clock.getElapsedTime()
      materialRef.current.uniforms.season.value = getSeasonValue(season)
      materialRef.current.uniforms.weather.value = getWeatherValue(weather.mood)
      materialRef.current.uniforms.timeOfDay.value = getTimeValue(timeOfDay)
    }
  })

  return (
    <mesh>
      <sphereGeometry args={[80, 32, 32]} />
      <shaderMaterial
        ref={materialRef}
        vertexShader={vertexShader}
        fragmentShader={fragmentShader}
        uniforms={uniforms}
        transparent
        side={BackSide}
        depthWrite={false}
      />
    </mesh>
  )
}

// Helper functions to convert enums to numbers for shaders
function getSeasonValue(season: Season): number {
  const seasonMap = { spring: 0, summer: 1, autumn: 2, winter: 3 }
  return seasonMap[season]
}

function getWeatherValue(mood: string): number {
  const weatherMap = { stormy: 0, sunny: 1, cloudy: 2, aurora: 3, starry: 4 }
  return (weatherMap as any)[mood] || 0
}

function getTimeValue(time: TimeOfDay): number {
  const timeMap = { dawn: 0, day: 1, dusk: 0.5, night: 0 }
  return timeMap[time]
}