"use client";

import dynamic from "next/dynamic";
import { useState, useEffect } from "react";

interface LocationPickerProps {
  onChange: (lat: number, lng: number) => void;
  initialPosition?: [number, number];
}

// Dynamically import the actual map to avoid SSR issues
const MapInner = dynamic(() => import("./LocationPickerInner"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[300px] w-full items-center justify-center rounded-lg bg-gray-100 text-sm text-gray-500">
      Loading map…
    </div>
  ),
});

export default function LocationPicker({
  onChange,
  initialPosition,
}: LocationPickerProps) {
  const [gpsActive, setGpsActive] = useState(false);
  const [position, setPosition] = useState<[number, number] | null>(
    initialPosition ?? null
  );

  useEffect(() => {
    if (initialPosition) {
      setPosition(initialPosition);
      setGpsActive(true);
    }
  }, [initialPosition]);

  function handleChange(lat: number, lng: number) {
    setPosition([lat, lng]);
    onChange(lat, lng);
  }

  return (
    <div className="space-y-2">
      {gpsActive && (
        <p className="flex items-center gap-1.5 text-xs text-green-700">
          <svg className="h-3.5 w-3.5" fill="currentColor" viewBox="0 0 20 20">
            <path fillRule="evenodd"
              d="M5.05 4.05a7 7 0 119.9 9.9L10 18.9l-4.95-4.95a7 7 0 010-9.9zM10 11a2 2 0 100-4 2 2 0 000 4z"
              clipRule="evenodd" />
          </svg>
          Using your location — drag the pin to adjust
        </p>
      )}
      <MapInner
        position={position}
        onChange={handleChange}
      />
      {position && (
        <p className="text-xs text-gray-500">
          Selected: {position[0].toFixed(6)}, {position[1].toFixed(6)}
        </p>
      )}
    </div>
  );
}
