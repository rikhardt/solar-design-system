import React from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid } from '@react-three/drei';
import { SystemConstraints } from '../../types/project';

interface ThreeJSViewerProps {
  systemConstraints?: SystemConstraints;
}

const SolarPanel: React.FC<{ position: [number, number, number] }> = ({ position }) => {
  return (
    <mesh position={position} rotation={[-Math.PI / 2, 0, 0]}>
      <boxGeometry args={[1, 1.6, 0.05]} />
      <meshStandardMaterial color="#1976d2" />
    </mesh>
  );
};

const RoofArea: React.FC<{ width: number; length: number }> = ({ width, length }) => {
  return (
    <mesh position={[0, -0.1, 0]} rotation={[-Math.PI / 2, 0, 0]}>
      <planeGeometry args={[width, length]} />
      <meshStandardMaterial color="#e0e0e0" transparent opacity={0.5} />
    </mesh>
  );
};

const ThreeJSViewer: React.FC<ThreeJSViewerProps> = ({ systemConstraints }) => {
  const defaultArea = { width: 10, length: 10 };

  return (
    <div style={{ width: '100%', height: '100%', minHeight: '400px' }}>
      <Canvas
        camera={{ position: [5, 5, 5], fov: 60 }}
        style={{ background: '#f5f5f5' }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={1} />
        
        {/* Área del techo */}
        <RoofArea 
          width={systemConstraints?.availableArea ? Math.sqrt(systemConstraints.availableArea) : defaultArea.width}
          length={systemConstraints?.availableArea ? Math.sqrt(systemConstraints.availableArea) : defaultArea.length}
        />

        {/* Ejemplo de paneles solares */}
        <SolarPanel position={[-2, 0, -2]} />
        <SolarPanel position={[-2, 0, 0]} />
        <SolarPanel position={[0, 0, -2]} />
        <SolarPanel position={[0, 0, 0]} />

        {/* Grid helper */}
        <Grid
          infiniteGrid
          cellSize={1}
          sectionSize={3}
          fadeDistance={30}
          fadeStrength={1}
        />

        {/* Controles de cámara */}
        <OrbitControls 
          enableDamping
          dampingFactor={0.05}
          minDistance={3}
          maxDistance={20}
          maxPolarAngle={Math.PI / 2.1}
        />
      </Canvas>
    </div>
  );
};

export default ThreeJSViewer;
