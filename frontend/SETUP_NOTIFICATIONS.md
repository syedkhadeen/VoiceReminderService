# Real-Time Notifications Setup - Complete! ✅

## What Was Added

### 1. Toaster Component
Added to `src/App.jsx`:
- Position: top-right
- Custom styling with dark theme
- Different durations for success/error/loading
- Custom icons and colors

### 2. ReminderNotifications Component
Added to `src/App.jsx`:
- Polls backend every 5 seconds
- Shows toast notifications automatically
- Handles all reminder status changes

## Already Installed ✅

`react-hot-toast` is already in your `package.json`, so no installation needed!

## How to Test

### 1. Start All Services

**Terminal 1 - Backend API:**
```bash
cd backend-api
venv\Scripts\python.exe app\main.py
```

**Terminal 2 - Worker Service:**
```bash
cd worker-service
venv\Scripts\python.exe app\main.py
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

### 2. Create a Test Reminder

Open your browser to `http://localhost:5173` and:

1. Go to "Create Reminder" page
2. Select a user
3. Enter phone number: `+1234567890`
4. Enter message: `Test notification system`
5. Set scheduled time to **1 minute ago** (past time)
6. Click "Create Reminder"

### 3. Watch the Magic! 🎉

Within 10-30 seconds, you'll see toast notifications appear:

1. **Loading Toast** (blue):
   ```
   📞 Calling: Test notification system...
   ```

2. **Success Toast** (green):
   ```
   ✅ Call completed: Test notification system
   ```

3. **Transcript Toast** (gray):
   ```
   💬 [MOCK TRANSCRIPT] Your reminder: Test notification system. Call duration: 15 seconds.
   ```

## Notification Types

### Processing (Loading)
- Icon: 📞
- Color: Blue
- Duration: 3 seconds
- Message: "Calling: {message}..."

### Called (Success)
- Icon: ✅
- Color: Green
- Duration: 5 seconds
- Message: "Call completed: {message}"
- Followed by transcript toast

### Failed (Error)
- Icon: ❌
- Color: Red
- Duration: 5 seconds
- Message: "Call failed: {message}"

## Customization

### Change Position
In `src/App.jsx`:
```jsx
<Toaster position="bottom-right" />  // or "top-left", "bottom-center", etc.
```

### Change Colors
```jsx
toastOptions={{
    style: {
        background: '#1f2937',  // Darker background
        color: '#f9fafb',       // Lighter text
    },
    success: {
        iconTheme: {
            primary: '#22c55e',  // Different green
        },
    },
}}
```

### Change Duration
```jsx
toastOptions={{
    duration: 6000,  // 6 seconds default
    success: {
        duration: 8000,  // 8 seconds for success
    },
}}
```

## Troubleshooting

### Notifications Not Showing

1. **Check Browser Console**
   - Open DevTools (F12)
   - Look for errors
   - Should see: "Checking for updates..."

2. **Check Backend is Running**
   ```bash
   curl http://localhost:8000/health
   ```
   Should return: `{"status":"healthy"}`

3. **Check Worker is Running**
   ```bash
   curl http://localhost:8001/health
   ```
   Should return: `{"status":"healthy","scheduler":"running"}`

4. **Check Notifications Endpoint**
   ```bash
   curl http://localhost:8000/api/reminders/notifications/recent?since_seconds=30
   ```
   Should return JSON with notifications

### Notifications Showing Multiple Times

This is normal! The component prevents duplicates, but you might see:
1. Initial "Calling" notification
2. "Call completed" notification
3. Transcript notification

All three are intentional and show the complete flow.

### Worker Not Processing Reminders

1. **Check Worker Logs**
   Look for:
   ```
   🎭 Infobip Voice running in MOCK mode
   Scheduler: Checking for due reminders...
   ```

2. **Check Scheduler Interval**
   In `.env`:
   ```env
   SCHEDULER_INTERVAL_SECONDS=20
   ```
   Worker checks every 20 seconds by default.

3. **Check Reminder Time**
   Make sure `scheduled_at` is in the **past**:
   ```json
   {
     "scheduled_at": "2025-12-10T10:00:00Z"  // Must be before current time
   }
   ```

## Advanced Usage

### Refresh List on Update

If you want to refresh your reminders list when a notification arrives:

```jsx
// In your Reminders page component
import { useState, useEffect } from 'react';
import ReminderNotifications from '../components/ReminderNotifications';

function Reminders() {
    const [refreshKey, setRefreshKey] = useState(0);

    const handleUpdate = () => {
        setRefreshKey(prev => prev + 1);
    };

    useEffect(() => {
        // Fetch reminders
        fetchReminders();
    }, [refreshKey]);

    return (
        <div>
            <ReminderNotifications onUpdate={handleUpdate} />
            {/* Your reminders list */}
        </div>
    );
}
```

### Filter by User

To only show notifications for a specific user:

```jsx
<ReminderNotifications 
    userId={currentUser.id}
    onUpdate={handleUpdate}
/>
```

Then update `ReminderNotifications.jsx`:
```jsx
const checkForUpdates = useCallback(async () => {
    const url = userId 
        ? `${API_URL}/api/users/${userId}/reminders?status=all`
        : `${API_URL}/api/reminders/notifications/recent?since_seconds=10`;
    
    // ... rest of the code
}, [userId]);
```

## Testing with Multiple Reminders

Create multiple reminders at once to see batch processing:

```bash
# Run this test script
python test_mock_system.py
```

Or manually create 5 reminders:
1. Go to Create Reminder page
2. Create 5 reminders with past times
3. Wait 20-30 seconds
4. Watch all notifications appear in sequence

## Production Considerations

### 1. Polling Interval
For production with many users, increase the interval:

In `ReminderNotifications.jsx`:
```jsx
const POLL_INTERVAL = 10000; // 10 seconds instead of 5
```

### 2. WebSocket Alternative
For better performance with >100 concurrent users, consider WebSocket:

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

### 3. Rate Limiting
Add rate limiting to the notifications endpoint in production.

## What's Next?

1. ✅ Notifications are working
2. ✅ Mock mode is enabled
3. ⏭️ Test with multiple reminders
4. ⏭️ Customize toast appearance
5. ⏭️ Add user-specific filtering
6. ⏭️ Deploy to staging
7. ⏭️ Switch to real Infobip calls

## Support

If you encounter issues:
1. Check this guide
2. Check browser console
3. Check worker service logs
4. Check backend API logs
5. Run `python test_mock_system.py`

## Success! 🎉

Your real-time notification system is now fully integrated and working!

Create a reminder and watch the magic happen! ✨
