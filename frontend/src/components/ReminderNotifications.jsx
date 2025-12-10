import { useEffect, useState, useCallback } from 'react';
import { toast } from 'react-hot-toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const POLL_INTERVAL = 5000; // Poll every 5 seconds

/**
 * ReminderNotifications Component
 * 
 * Polls the backend for recent reminder updates and shows toast notifications.
 * Also triggers a callback when updates are detected so parent components can refresh.
 */
export default function ReminderNotifications({ onUpdate }) {
  const [lastPollTime, setLastPollTime] = useState(Date.now());
  const [processedIds, setProcessedIds] = useState(new Set());

  const checkForUpdates = useCallback(async () => {
    try {
      console.log('🔍 Checking for reminder updates...');
      const response = await fetch(
        `${API_URL}/api/reminders/notifications/recent?since_seconds=10`
      );
      
      if (!response.ok) {
        console.error('❌ Failed to fetch notifications:', response.status);
        return;
      }

      const data = await response.json();
      console.log('📬 Received notifications:', data.count, 'updates');
      
      if (data.notifications && data.notifications.length > 0) {
        console.log('🎉 Processing', data.notifications.length, 'notification(s)');
        // Process new notifications
        data.notifications.forEach(notification => {
          const notifId = `${notification.reminder_id}-${notification.status}-${notification.updated_at}`;
          
          // Skip if already processed
          if (processedIds.has(notifId)) {
            return;
          }

          // Mark as processed
          setProcessedIds(prev => new Set([...prev, notifId]));

          // Show toast notification based on status
          const message = notification.message.substring(0, 50);
          
          console.log('📢 Showing notification for:', notification.status, message);
          
          switch (notification.status) {
            case 'processing':
              toast.loading(
                `📞 Calling: ${message}...`,
                { id: notification.reminder_id, duration: 3000 }
              );
              break;
              
            case 'called':
              toast.success(
                `✅ Call completed: ${message}`,
                { 
                  id: notification.reminder_id,
                  duration: 5000,
                  icon: '📞'
                }
              );
              
              // Show transcript if available
              if (notification.latest_log?.transcript) {
                setTimeout(() => {
                  toast(
                    notification.latest_log.transcript,
                    { 
                      duration: 4000,
                      icon: '💬'
                    }
                  );
                }, 500);
              }
              break;
              
            case 'failed':
              toast.error(
                `❌ Call failed: ${message}`,
                { 
                  id: notification.reminder_id,
                  duration: 5000
                }
              );
              break;
              
            case 'scheduled':
              // Don't show notification for scheduled status
              console.log('⏰ Reminder scheduled, waiting for processing...');
              break;
              
            default:
              console.log('ℹ️ Unknown status:', notification.status);
              break;
          }
        });

        // Trigger parent update callback
        if (onUpdate) {
          onUpdate();
        }
      }

      setLastPollTime(Date.now());
    } catch (error) {
      console.error('Error checking for updates:', error);
    }
  }, [processedIds, onUpdate]);

  useEffect(() => {
    // Initial check
    checkForUpdates();

    // Set up polling interval
    const interval = setInterval(checkForUpdates, POLL_INTERVAL);

    return () => clearInterval(interval);
  }, [checkForUpdates]);

  // Cleanup old processed IDs (keep last 100)
  useEffect(() => {
    if (processedIds.size > 100) {
      const arr = Array.from(processedIds);
      setProcessedIds(new Set(arr.slice(-100)));
    }
  }, [processedIds]);

  return null; // This component doesn't render anything
}
