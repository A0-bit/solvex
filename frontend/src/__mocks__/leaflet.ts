// Stub for Leaflet — avoids canvas/DOM errors in Jest
const L = {
  map: jest.fn(() => ({ setView: jest.fn(), remove: jest.fn() })),
  tileLayer: jest.fn(() => ({ addTo: jest.fn() })),
  marker: jest.fn(() => ({ addTo: jest.fn(), on: jest.fn() })),
  Icon: { Default: { prototype: {}, mergeOptions: jest.fn() } },
};
export default L;
module.exports = L;
