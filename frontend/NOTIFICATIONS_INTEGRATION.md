# Real-Time Notifications Integration Guide

## Overview
The `ReminderNotifications` component provides real-time updates for reminder status changes using polling.

## Installation

### 1. Install react-hot-toast (if not already installed)
```bash
npm install react-hot-toast
```

### 2. Add Toaster to your App

In your main `App.jsx` or `main.jsx`:

```jsx
import { Toaster } from 'react-hot-toast';
import ReminderNotifications from './components/ReminderNotifications';

function App() {
  const handleReminderUpdate = () => {
    // Refresh your reminders list here
    console.log('Reminder updated - refresh your list!');
  };

  return (
    <div className="App">
      {/* Add the Toaster component */}
      <Toaster 
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 5000,
            iconTheme: {
              primary: '#10b981',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
      
      {/* Add the notification listener */}
      <ReminderNotifications onUpdate={handleReminderUpdate} />
      
      {/* Your app content */}
      <YourRoutes />
    </div>
  );
}
```

## Usage in Reminder List Component

```jsx
import { useState, useEffect } from 'react';
import ReminderNotifications from './components/ReminderNotifications';

function RemindersList() {
  const [reminders, setReminders] = useState([]);
  const [refreshKey, setRefreshKey] = useState(0);

  const fetchReminders = async () => {
    const response = await fetch('http://localhost:8000/api/reminders');
    const data = await response.json();
    setReminders(data.items);
  };

  useEffect(() => {
    fetchReminders();
  }, [refreshKey]);

  const handleUpdate = () => {
    // Trigger refresh when notification received
    setRefreshKey(prev => prev + 1);
  };

  return (
    <div>
      <ReminderNotifications onUpdate={handleUpdate} />
      
      <h1>Reminders</h1>
      {reminders.map(reminder => (
        <div key={reminder.id}>
          <p>{reminder.message}</p>
          <span className={`status-${reminder.status}`}>
            {reminder.status}
          </span>
        </div>
      ))}
    </div>
  );
}
```

## Notification Types

The component shows different notifications based on reminder status:

### 1. Processing (Loading)
```
📞 Calling: Your reminder message...
```

### 2. Called (Success)
```
✅ Call completed: Your reminder message
💬 [MOCK TRANSCRIPT] Your reminder: ...
```

### 3. Failed (Error)
```
❌ Call failed: Your reminder message
```

## Customization

### Change Poll Interval
Edit `POLL_INTERVAL` in `ReminderNotifications.jsx`:
```jsx
const POLL_INTERVAL = 3000; // Poll every 3 seconds
```

### Customize Toast Appearance
Modify the toast options in your App component:
```jsx
<Toaster 
  position="bottom-center"
  toastOptions={{
    duration: 3000,
    style: {
      background: '#1f2937',
      color: '#f3f4f6',
      borderRadius: '8px',
    },
  }}
/>
```

### Filter Notifications by User
Pass a userId prop to only show notifications for specific user:
```jsx
<ReminderNotifications 
  userId={currentUser.id}
  onUpdate={handleUpdate} 
/>
```

Then update the component to filter:
```jsx
const response = await fetch(
  `${API_URL}/api/users/${userId}/reminders?status=all`
);
```

## Testing

### 1. Create a reminder with a past time
```bash
POST http://localhost:8000/api/reminders
{
  "user_id": "your-user-id",
  "phone_number": "+1234567890",
  "message": "Test notification",
  "scheduled_at": "2025-12-10T10:00:00Z"  // Past time
}
```

### 2. Watch for notifications
- Within 5-10 seconds, you should see:
  - Loading toast: "📞 Calling..."
  - Success toast: "✅ Call completed..."
  - Transcript toast: "💬 [MOCK TRANSCRIPT]..."

### 3. Check browser console
The component logs polling activity:
```
Checking for updates...
Found 1 new notification(s)
```

## API Endpoint

The component polls this endpoint:
```
GET /api/reminders/notifications/recent?since_seconds=10
```

Response format:
```json
{
  "count": 1,
  "since_seconds": 10,
  "notifications": [
    {
      "reminder_id": "uuid",
      "user_id": "uuid",
      "phone_number": "+1234567890",
      "message": "Your reminder",
      "status": "called",
      "updated_at": "2025-12-10T10:00:00",
      "external_call_id": "mock-uuid",
      "latest_log": {
        "status": "completed",
        "transcript": "[MOCK TRANSCRIPT] ...",
        "received_at": "2025-12-10T10:00:05"
      }
    }
  ]
}
```

## Troubleshooting

### Notifications not showing
1. Check browser console for errors
2. Verify API_URL is correct in .env
3. Check backend is running on port 8000
4. Verify worker service is running and processing reminders

### Duplicate notifications
- The component tracks processed notifications by ID
- If you see duplicates, check the `processedIds` logic

### Performance issues
- Increase `POLL_INTERVAL` to reduce server load
- Implement WebSocket for more efficient real-time updates

## Future Enhancements

### WebSocket Implementation
For production, consider using WebSocket instead of polling:

```jsx
useEffect(() => {
  const ws = new WebSocket('ws://localhost:8001/ws/notifications');
  
  ws.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    showNotification(notification);
  };
  
  return () => ws.close();
}, []);
```

### Server-Sent Events (SSE)
Alternative to WebSocket:

```jsx
useEffect(() => {
  const eventSource = new EventSource(
    `${API_URL}/api/reminders/notifications/stream`
  );
  
  eventSource.onmessage = (event) => {
    const notification = JSON.parse(event.data);
    showNotification(notification);
  };
  
  return () => eventSource.close();
}, []);
```
