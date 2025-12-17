# OmniVoIP Frontend

React-based frontend for OmniVoIP Contact Center.

## Structure

```
frontend/
├── public/
├── src/
│   ├── components/        # Reusable components
│   ├── pages/             # Page components
│   ├── features/          # Feature modules
│   │   ├── auth/
│   │   ├── campaigns/
│   │   ├── contacts/
│   │   ├── calls/
│   │   ├── agents/
│   │   ├── dashboard/
│   │   └── reports/
│   ├── services/          # API services
│   ├── store/             # Redux store
│   ├── hooks/             # Custom hooks
│   ├── utils/             # Utilities
│   ├── App.jsx
│   └── main.jsx
├── package.json
├── vite.config.js
├── Dockerfile
└── nginx.conf
```

## Features

- **React 18**: Modern React with hooks
- **Redux Toolkit**: State management
- **React Router**: SPA routing
- **Material-UI**: Component library
- **WebSocket**: Real-time updates
- **WebRTC**: Softphone integration (JsSIP)
- **Charts**: Recharts for analytics
- **Forms**: Formik + Yup validation

## Development

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint

# Format code
npm run format
```

## Key Features

### Agent Desktop
- Softphone (WebRTC)
- Call controls
- Contact information
- Call scripts
- Disposition codes
- Notes

### Dashboard
- Real-time metrics
- Agent status
- Queue statistics
- Call volume charts

### Campaign Management
- Create/edit campaigns
- Contact list upload
- Schedule campaigns
- Monitor progress

### Reports
- Call history
- Agent performance
- Campaign results
- Export to Excel/CSV

## WebRTC Softphone

Uses JsSIP library for SIP over WebSocket:

```javascript
import JsSIP from 'jssip';

const socket = new JsSIP.WebSocketInterface('wss://domain.com/ws/sip');
const ua = new JsSIP.UA({ 
  sockets: [socket],
  uri: 'sip:agent@domain.com',
  password: 'password'
});

ua.start();
```

## Environment Variables

Create `.env` file:

```
VITE_API_URL=https://api.omnivoip.com
VITE_WS_URL=wss://api.omnivoip.com/ws
VITE_WEBRTC_SERVER=wss://domain.com/ws/sip
```
