import { render, screen } from '@testing-library/react';
import App from './App';
import { useWebSocket } from './hooks/useWebSocket';

jest.mock('./hooks/useWebSocket', () => ({
  useWebSocket: jest.fn(),
}));

beforeEach(() => {
  useWebSocket.mockReturnValue({ data: null, status: 'connecting' });
});

test('renders the OT Digital Twin dashboard shell and synthetic-data notice', () => {
  render(<App />);
  expect(screen.getByRole('heading', { name: /OT Digital Twin/i })).toBeInTheDocument();
  expect(screen.getByText(/SYNTHETIC DATA.*computer-generated simulation outputs/i)).toBeInTheDocument();
});

test('renders the baseline Unity stream sensor fields for WP-007', async () => {
  useWebSocket.mockReturnValue({
    status: 'connected',
    data: {
      assets: [{
        asset_id: 'GDC-WP-007',
        asset_label: 'Well Pump WP-07',
        status: 'WARNING',
        failure_probability: 0.34,
        sensors: {
          temperature_c: 208.5,
          pressure_bar: 19.1,
          vibration_mm_s: 4.2,
          flow_rate_kg_s: 115.0,
          rotation_rpm: 3650,
        },
      }],
    },
  });

  render(<App />);

  expect(await screen.findByText('Well Pump WP-07')).toBeInTheDocument();
  expect(screen.getByText('Temperature')).toBeInTheDocument();
  expect(screen.getByText('Pressure')).toBeInTheDocument();
  expect(screen.getByText('Flow Rate')).toBeInTheDocument();
  expect(screen.getByText('Rotation')).toBeInTheDocument();
  expect(screen.getAllByText('34.0%').length).toBeGreaterThanOrEqual(1);
});
