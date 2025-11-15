# SnailMail - Setup & Integration Guide

Complete guide to set up your backend API and integrate it with the frontend.

## Quick Start (5 minutes)

### 1. Backend Setup

```bash
# Navigate to backend directory
cd snailMail-Backend

# Install dependencies
npm install

# Copy environment template
cp .env.example .env

# Edit .env and add your API keys
# GOOGLE_MAPS_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Start the development server
npm run dev
```

Backend will be running at `http://localhost:3001`

### 2. Get API Keys

#### Google Maps API (Primary)
1. Visit: https://console.cloud.google.com/
2. Create a new project
3. Enable "Distance Matrix API"
4. Create credentials → API Key
5. Copy the key to `.env` file

#### Anthropic Claude API (Fallback)
1. Visit: https://console.anthropic.com/
2. Create an account
3. Navigate to API Keys
4. Create a new key
5. Copy the key to `.env` file

### 3. Test the API

```bash
# Check health
curl http://localhost:3001/api/distance/health

# Test distance calculation
curl -X POST http://localhost:3001/api/distance/calculate \
  -H "Content-Type: application/json" \
  -d '{
    "origin": {"address": "New York, NY"},
    "destination": {"address": "Los Angeles, CA"},
    "mode": "walking"
  }'
```

## Frontend Integration

### Option 1: Create an API Service Hook

Create `snailMail-Frontend/src/services/api.ts`:

```typescript
const API_BASE_URL = 'http://localhost:3001/api';

export interface Location {
  address?: string;
  lat?: number;
  lng?: number;
}

export interface DeliveryEstimate {
  distanceMeters: number;
  distanceText: string;
  durationSeconds: number;
  deliveryTimeSeconds: number;
  deliveryTimeText: string;
  origin: string;
  destination: string;
  transportMode: string;
  speedKmH: number;
  isEstimate: boolean;
  method: 'google-maps' | 'claude-estimate';
}

export async function calculateDeliveryTime(
  origin: Location,
  destination: Location,
  mode: 'walking' | 'swimming' | 'pigeon' | 'rock-climbing'
): Promise<DeliveryEstimate> {
  const response = await fetch(`${API_BASE_URL}/distance/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ origin, destination, mode }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to calculate delivery time');
  }

  const result = await response.json();
  return result.data;
}

export async function calculateAllDeliveryTimes(
  origin: Location,
  destination: Location
): Promise<Record<string, DeliveryEstimate>> {
  const response = await fetch(`${API_BASE_URL}/distance/calculate-all`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ origin, destination }),
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.message || 'Failed to calculate delivery times');
  }

  const result = await response.json();
  return result.data;
}
```

### Option 2: Update TransportMode Component

Update `TransportMode.tsx` to fetch and display actual delivery times:

```typescript
import { useState, useEffect } from 'react';
import './TransportMode.css';
import { calculateDeliveryTime, Location, DeliveryEstimate } from '../services/api';

export type TransportType = 'walking' | 'swimming' | 'pigeon' | 'rock-climbing';

interface TransportModeProps {
  type: TransportType;
  speed: string;
  description: string;
  origin?: Location;
  destination?: Location;
}

const TransportMode = ({ type, speed, description, origin, destination }: TransportModeProps) => {
  const [estimate, setEstimate] = useState<DeliveryEstimate | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (origin && destination) {
      fetchDeliveryTime();
    }
  }, [origin, destination, type]);

  const fetchDeliveryTime = async () => {
    if (!origin || !destination) return;

    setLoading(true);
    setError(null);

    try {
      const result = await calculateDeliveryTime(origin, destination, type);
      setEstimate(result);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="transport-card">
      <h3 className="transport-title">
        {type.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
      </h3>
      
      <div className={`animation-container ${type}`}>
        {/* Your existing animation code */}
      </div>

      <div className="transport-info">
        <p className="transport-speed"><strong>Speed:</strong> {speed}</p>
        <p className="transport-description">{description}</p>
        
        {estimate && (
          <div className="delivery-estimate">
            <p><strong>Distance:</strong> {estimate.distanceText}</p>
            <p><strong>Delivery Time:</strong> {estimate.deliveryTimeText}</p>
            {estimate.isEstimate && (
              <p className="estimate-badge">⚠️ Estimated (using AI)</p>
            )}
          </div>
        )}

        {loading && <p className="loading">Calculating...</p>}
        {error && <p className="error">{error}</p>}
      </div>
    </div>
  );
};

export default TransportMode;
```

### Option 3: Create a Form Component

Create `snailMail-Frontend/src/components/DeliveryCalculator.tsx`:

```typescript
import { useState } from 'react';
import { calculateAllDeliveryTimes, Location, DeliveryEstimate } from '../services/api';
import TransportMode from './TransportMode';

const DeliveryCalculator = () => {
  const [origin, setOrigin] = useState<string>('');
  const [destination, setDestination] = useState<string>('');
  const [results, setResults] = useState<Record<string, DeliveryEstimate> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleCalculate = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResults(null);

    try {
      const originLoc: Location = { address: origin };
      const destLoc: Location = { address: destination };
      
      const estimates = await calculateAllDeliveryTimes(originLoc, destLoc);
      setResults(estimates);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="delivery-calculator">
      <form onSubmit={handleCalculate} className="calculator-form">
        <input
          type="text"
          placeholder="From (e.g., New York, NY)"
          value={origin}
          onChange={(e) => setOrigin(e.target.value)}
          required
        />
        <input
          type="text"
          placeholder="To (e.g., Los Angeles, CA)"
          value={destination}
          onChange={(e) => setDestination(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Calculating...' : 'Calculate Delivery Times'}
        </button>
      </form>

      {error && <div className="error">{error}</div>}

      {results && (
        <div className="transport-grid">
          <TransportMode
            type="walking"
            speed={`${results.walking.speedKmH} km/h`}
            description={`Delivery time: ${results.walking.deliveryTimeText}`}
          />
          <TransportMode
            type="swimming"
            speed={`${results.swimming.speedKmH} km/h`}
            description={`Delivery time: ${results.swimming.deliveryTimeText}`}
          />
          <TransportMode
            type="pigeon"
            speed={`${results.pigeon.speedKmH} km/h`}
            description={`Delivery time: ${results.pigeon.deliveryTimeText}`}
          />
          <TransportMode
            type="rock-climbing"
            speed={`${results['rock-climbing'].speedKmH} km/h`}
            description={`Delivery time: ${results['rock-climbing'].deliveryTimeText}`}
          />
        </div>
      )}
    </div>
  );
};

export default DeliveryCalculator;
```

## Testing the Integration

1. Start both servers:
```bash
# Terminal 1 - Backend
cd snailMail-Backend
npm run dev

# Terminal 2 - Frontend
cd snailMail-Frontend
npm run dev
```

2. Open browser to `http://localhost:5173`

3. Enter origin and destination addresses

4. View calculated delivery times for each transport mode!

## Common Issues & Solutions

### CORS Errors
**Problem:** Frontend can't connect to backend
**Solution:** Ensure `FRONTEND_URL` in `.env` matches your frontend URL

### Google Maps API Errors
**Problem:** "API key is not configured"
**Solution:** 
1. Check `.env` file has the key
2. Restart the backend server
3. Verify the key is valid in Google Cloud Console
4. Ensure Distance Matrix API is enabled

### Rate Limiting
**Problem:** Too many requests
**Solution:** 
- Google Maps has daily quotas
- Add request caching if needed
- Claude fallback will activate automatically

## Next Steps

1. **Add Email Functionality**: Integrate an email service (SendGrid, Mailgun)
2. **Add Queue System**: Use Redis + Bull for delayed email sending
3. **Add Database**: Store email delivery schedules (PostgreSQL, MongoDB)
4. **Add Authentication**: Protect API endpoints
5. **Deploy**: Host on Heroku, Railway, or DigitalOcean

## Architecture Overview

```
┌─────────────────┐
│     Frontend    │
│   (React/TS)    │
└────────┬────────┘
         │ HTTP
         ↓
┌─────────────────┐
│   Backend API   │
│   (Express/TS)  │
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌──────┐  ┌──────┐
│Google│  │Claude│
│ Maps │  │  AI  │
│ API  │  │ (FB) │
└──────┘  └──────┘
```

## Support

For issues or questions:
1. Check the backend logs in your terminal
2. Use the health endpoint: `GET /api/distance/health`
3. Verify API keys are correct
4. Check CORS configuration matches your frontend URL

Happy Hacking! 🐌📧
