"use client";

import { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, useMapEvents } from "react-leaflet";
import type { LatLngExpression } from "leaflet";

// Fix Leaflet default marker icons in Next.js
import L from "leaflet";
delete (L.Icon.Default.prototype as unknown as Record<string, unknown>)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

interface Props {
  position: [number, number] | null;
  onChange: (lat: number, lng: number) => void;
}

const DEFAULT_CENTER: LatLngExpression = [23.8103, 90.4125]; // Dhaka

function DraggableMarker({
  position,
  onChange,
}: {
  position: [number, number] | null;
  onChange: (lat: number, lng: number) => void;
}) {
  const [pos, setPos] = useState<[number, number] | null>(position);

  useEffect(() => {
    setPos(position);
  }, [position]);

  useMapEvents({
    click(e) {
      const newPos: [number, number] = [e.latlng.lat, e.latlng.lng];
      setPos(newPos);
      onChange(e.latlng.lat, e.latlng.lng);
    },
  });

  if (!pos) return null;

  return (
    <Marker
      position={pos}
      draggable
      eventHandlers={{
        dragend(e) {
          const m = e.target as L.Marker;
          const p = m.getLatLng();
          const newPos: [number, number] = [p.lat, p.lng];
          setPos(newPos);
          onChange(p.lat, p.lng);
        },
      }}
    />
  );
}

export default function LocationPickerInner({ position, onChange }: Props) {
  const center: LatLngExpression = position ?? DEFAULT_CENTER;

  return (
    <MapContainer
      center={center}
      zoom={13}
      style={{ height: 300, width: "100%" }}
      className="rounded-lg"
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
      />
      <DraggableMarker position={position} onChange={onChange} />
    </MapContainer>
  );
}
