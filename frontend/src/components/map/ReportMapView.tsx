"use client";

import dynamic from "next/dynamic";

interface ReportMapViewProps {
  lat: number;
  lng: number;
}

const MapInner = dynamic(() => import("./ReportMapViewInner"), {
  ssr: false,
  loading: () => (
    <div className="flex h-[220px] w-full items-center justify-center rounded-lg bg-gray-100 text-sm text-gray-500">
      Loading map…
    </div>
  ),
});

export default function ReportMapView({ lat, lng }: ReportMapViewProps) {
  return <MapInner lat={lat} lng={lng} />;
}
