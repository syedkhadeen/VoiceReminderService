"""
Complete test script for mock voice reminder system.
Tests the entire flow from reminder creation to notification.
"""
import asyncio
import httpx
from datetime import datetime, timedelta
import time

API_URL = "http://localhost:8000"
WORKER_URL = "http://localhost:8001"

async def test_complete_flow():
    """Test the complete reminder flow with mock calls."""
    
    print("="*70)
    print("MOCK VOICE REMINDER SYSTEM - COMPLETE TEST")
    print("="*70)
    print()
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Check if services are running
        print("Step 1: Checking services...")
        try:
            api_health = await client.get(f"{API_URL}/health")
            worker_health = await client.get(f"{WORKER_URL}/health")
            
            if api_health.status_code == 200 and worker_health.status_code == 200:
                print("Backend API: Running")
                print("Worker Service: Running")
                print()
            else:
                print("Services not healthy")
                return
        except Exception as e:
            print(f"Error connecting to services: {e}")
            print("Make sure both backend-api and worker-service are running!")
            return
        
        # Step 2: Create or get a test user
        print("Step 2: Creating test user...")
        try:
            user_response = await client.post(
                f"{API_URL}/api/users",
                json={"email": f"test_{int(time.time())}@example.com"}
            )
            
            if user_response.status_code == 201:
                user = user_response.json()
                user_id = user["id"]
                print(f"User created: {user['email']}")
                print(f"   User ID: {user_id}")
                print()
            else:
                print(f"Failed to create user: {user_response.text}")
                return
        except Exception as e:
            print(f"Error creating user: {e}")
            return
        
        # Step 3: Create a reminder with past time (will be processed immediately)
        print("Step 3: Creating reminder with past time...")
        past_time = (datetime.utcnow() - timedelta(minutes=1)).isoformat() + "Z"
        
        try:
            reminder_response = await client.post(
                f"{API_URL}/api/reminders",
                json={
                    "user_id": user_id,
                    "phone_number": "+1234567890",
                    "message": "This is a test reminder for mock system",
                    "scheduled_at": past_time
                }
            )
            
            if reminder_response.status_code == 201:
                reminder = reminder_response.json()
                reminder_id = reminder["id"]
                print(f" Reminder created: {reminder_id}")
                print(f"   Message: {reminder['message']}")
                print(f"   Status: {reminder['status']}")
                print(f"   Scheduled: {reminder['scheduled_at']}")
                print()
            else:
                print(f" Failed to create reminder: {reminder_response.text}")
                return
        except Exception as e:
            print(f" Error creating reminder: {e}")
            return
        
        # Step 4: Wait for worker to process (scheduler runs every 20-30 seconds)
        print("Step 4: Waiting for worker to process reminder...")
        print("   (Worker checks every 20-30 seconds)")
        print()
        
        max_wait = 60  # Wait up to 60 seconds
        check_interval = 5
        elapsed = 0
        
        while elapsed < max_wait:
            await asyncio.sleep(check_interval)
            elapsed += check_interval
            
            # Check reminder status
            try:
                status_response = await client.get(
                    f"{API_URL}/api/reminders/{reminder_id}"
                )
                
                if status_response.status_code == 200:
                    current_reminder = status_response.json()
                    current_status = current_reminder["status"]
                    
                    print(f"   [{elapsed}s] Status: {current_status}")
                    
                    if current_status in ["called", "failed"]:
                        print()
                        print(f" Reminder processed! Final status: {current_status}")
                        print()
                        
                        # Show call logs
                        if current_reminder.get("call_logs"):
                            print(" Call Logs:")
                            for log in current_reminder["call_logs"]:
                                print(f"   - Status: {log['status']}")
                                print(f"     Time: {log['received_at']}")
                                if log.get('transcript'):
                                    print(f"     Transcript: {log['transcript'][:100]}...")
                            print()
                        
                        break
                    elif current_status == "processing":
                        print("    Call in progress...")
                        
            except Exception as e:
                print(f"    Error checking status: {e}")
        
        if elapsed >= max_wait:
            print()
            print("  Timeout waiting for reminder to be processed")
            print("   Check worker service logs for errors")
            print()
        
        # Step 5: Test notifications endpoint
        print("Step 5: Testing notifications endpoint...")
        try:
            notif_response = await client.get(
                f"{API_URL}/api/reminders/notifications/recent?since_seconds=120"
            )
            
            if notif_response.status_code == 200:
                notif_data = notif_response.json()
                print(f" Notifications endpoint working")
                print(f"   Found {notif_data['count']} recent update(s)")
                
                if notif_data['notifications']:
                    print()
                    print("📬 Recent Notifications:")
                    for notif in notif_data['notifications'][:3]:
                        print(f"   - Reminder: {notif['message'][:50]}...")
                        print(f"     Status: {notif['status']}")
                        print(f"     Updated: {notif['updated_at']}")
                        if notif.get('latest_log'):
                            print(f"     Log: {notif['latest_log']['status']}")
                        print()
            else:
                print(f" Notifications endpoint failed: {notif_response.text}")
        except Exception as e:
            print(f" Error testing notifications: {e}")
        
        # Step 6: Get stats
        print("Step 6: Getting reminder statistics...")
        try:
            stats_response = await client.get(f"{API_URL}/api/reminders/stats")
            
            if stats_response.status_code == 200:
                stats = stats_response.json()
                print(f" Statistics:")
                print(f"   Total: {stats['total']}")
                print(f"   Scheduled: {stats['scheduled']}")
                print(f"   Processing: {stats['processing']}")
                print(f"   Called: {stats['called']}")
                print(f"   Failed: {stats['failed']}")
                print()
        except Exception as e:
            print(f" Error getting stats: {e}")
    
    print("="*70)
    print("TEST COMPLETE!")
    print("="*70)
    print()
    print("Next steps:")
    print("1. Open your frontend application")
    print("2. The ReminderNotifications component will show toast notifications")
    print("3. Create more reminders and watch them get processed automatically")
    print()
    print("To see mock calls in action:")
    print("- Check worker-service logs for [MOCK] messages")
    print("- Watch the frontend for toast notifications")
    print("- Poll /api/reminders/notifications/recent for updates")

if __name__ == "__main__":
    asyncio.run(test_complete_flow())
