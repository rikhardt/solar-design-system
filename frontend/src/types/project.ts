export interface Location {
  latitude: number;
  longitude: number;
  address: string;
}

export interface ConsumptionProfile {
  hourly: number[];
  monthly: number[];
  annual: number;
}

export interface SystemConstraints {
  availableArea: number;
  roofType: string;
  orientation: number;
  tilt: number;
  obstacles: Obstacle[];
}

export interface Obstacle {
  type: string;
  dimensions: {
    width: number;
    height: number;
    depth: number;
  };
  position: {
    x: number;
    y: number;
    z: number;
  };
}

export interface Component {
  id: string;
  type: 'panel' | 'inverter' | 'battery';
  manufacturer: string;
  model: string;
  specifications: {
    [key: string]: number | string;
  };
}

export interface Project {
  id: string;
  name: string;
  location: Location;
  consumptionProfile: ConsumptionProfile;
  systemConstraints: SystemConstraints;
  selectedComponents: Component[];
  createdAt: string;
  updatedAt: string;
}
