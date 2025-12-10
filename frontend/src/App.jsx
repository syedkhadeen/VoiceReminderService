import { Routes, Route } from 'react-router-dom'
import { Toaster } from 'react-hot-toast'
import Layout from './components/layout/Layout'
import Dashboard from './pages/Dashboard'
import Users from './pages/Users'
import CreateReminder from './pages/CreateReminder'
import ReminderDetail from './pages/ReminderDetail'
import Reminders from './pages/Reminders'
import ReminderNotifications from './components/ReminderNotifications'

function App() {
    return (
        <>
            {/* Toast notifications container */}
            <Toaster 
                position="top-right"
                toastOptions={{
                    duration: 4000,
                    style: {
                        background: '#363636',
                        color: '#fff',
                        padding: '16px',
                        borderRadius: '8px',
                        fontSize: '14px',
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
                    loading: {
                        duration: 3000,
                        iconTheme: {
                            primary: '#3b82f6',
                            secondary: '#fff',
                        },
                    },
                }}
            />
            
            {/* Real-time notification listener */}
            <ReminderNotifications />
            
            {/* App routes */}
            <Routes>
                <Route path="/" element={<Layout />}>
                    <Route index element={<Dashboard />} />
                    <Route path="users" element={<Users />} />
                    <Route path="reminders" element={<Reminders />} />
                    <Route path="reminders/create" element={<CreateReminder />} />
                    <Route path="reminders/:id" element={<ReminderDetail />} />
                </Route>
            </Routes>
        </>
    )
}

export default App
