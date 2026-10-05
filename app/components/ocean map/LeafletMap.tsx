"use client";

import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  Circle,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";

const markerIcon = new L.Icon({
  iconUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png",
  iconRetinaUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png",
  shadowUrl:
    "https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
});

function ClickHandler({
  onLocation,
}: {
  onLocation: (lat: number, lon: number) => void;
}) {
  useMapEvents({
    click(e) {
      onLocation(e.latlng.lat, e.latlng.lng);
    },
  });

  return null;
}

export default function LeafletMap({
  onLocation,
}: {
  onLocation: (lat: number, lon: number) => void;
}) {
  const latitude = 15.5;
  const longitude = 72.5;

  return (
    <MapContainer
      center={[latitude, longitude]}
      zoom={5}
      scrollWheelZoom={true}
      style={{
        width: "100%",
        height: "520px",
      }}
    >
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution="&copy; OpenStreetMap contributors"
      />

      <ClickHandler onLocation={onLocation} />

      <Marker
        position={[latitude, longitude]}
        icon={markerIcon}
      >
        <Popup>
          <b>OceanEmbed Observation Point</b>
          <br />
          15.5° N, 72.5° E
        </Popup>
      </Marker>

      <Circle
        center={[latitude, longitude]}
        radius={50000}
        pathOptions={{
          color: "#22d3ee",
          fillColor: "#22d3ee",
          fillOpacity: 0.15,
        }}
      />
    </MapContainer>
  );
} 