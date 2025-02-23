import React, { memo } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { Location } from '../../types/project';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for default marker icon in Leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

type LocationPickerProps = {
  onLocationSelect: (lat: number, lng: number) => void;
};

type ProjectMapProps = {
  location: Location;
  onLocationChange: (lat: number, lng: number) => void;
};

const LocationPicker = memo(({ onLocationSelect }: LocationPickerProps) => {
  useMapEvents({
    click(e: L.LeafletMouseEvent) {
      onLocationSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
});

LocationPicker.displayName = 'LocationPicker';

const ProjectMap = memo(({ location, onLocationChange }: ProjectMapProps) => {
  return (
    <MapContainer
      center={[location.latitude, location.longitude]}
      zoom={13}
      style={{ height: '100%', width: '100%' }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
      />
      <Marker position={[location.latitude, location.longitude]} />
      <LocationPicker onLocationSelect={onLocationChange} />
    </MapContainer>
  );
});

ProjectMap.displayName = 'ProjectMap';

export default ProjectMap;
