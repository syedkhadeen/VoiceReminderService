import { Outlet, Link, useLocation } from 'react-router-dom'
import { useTheme } from '../../context/ThemeContext'
import {
    Home,
    Users,
    Bell,
    PlusCircle,
    Sun,
    Moon,
    Menu,
    X,
    Phone
} from 'lucide-react'
import { useState } from 'react'

const navigation = [
    { name: 'Dashboard', href: '/', icon: Home },
    { name: 'Users', href: '/users', icon: Users },
    { name: 'Reminders', href: '/reminders', icon: Bell },
    { name: 'Create Reminder', href: '/reminders/create', icon: PlusCircle },
]

export default function Layout() {
    const { isDark, toggleTheme } = useTheme()
    const location = useLocation()
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false)

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-slate-100 to-slate-50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900">
            {/* Background decoration */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/10 dark:bg-primary-500/5 rounded-full blur-3xl" />
                <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-accent-500/10 dark:bg-accent-500/5 rounded-full blur-3xl" />
            </div>

            {/* Sidebar - Desktop */}
            <aside className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-72 lg:flex-col">
                <div className="flex grow flex-col gap-y-5 overflow-y-auto glass-card m-4 px-6 py-8">
                    {/* Logo */}
                    <div className="flex items-center gap-3">
                        <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-accent-500 shadow-lg shadow-primary-500/30">
                            <Phone className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <h1 className="text-xl font-bold gradient-text">VoiceRemind</h1>
                            <p className="text-xs text-slate-500 dark:text-slate-400">AI-Powered Reminders</p>
                        </div>
                    </div>

                    {/* Navigation */}
                    <nav className="flex flex-1 flex-col mt-8">
                        <ul className="flex flex-1 flex-col gap-y-2">
                            {navigation.map((item) => {
                                const isActive = location.pathname === item.href
                                return (
                                    <li key={item.name}>
                                        <Link
                                            to={item.href}
                                            className={`group flex items-center gap-x-3 rounded-xl px-4 py-3 text-sm font-medium transition-all duration-200 ${isActive
                                                    ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white shadow-lg shadow-primary-500/30'
                                                    : 'text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50'
                                                }`}
                                        >
                                            <item.icon className={`h-5 w-5 flex-shrink-0 ${isActive ? 'text-white' : 'text-slate-400 group-hover:text-primary-500'}`} />
                                            {item.name}
                                        </Link>
                                    </li>
                                )
                            })}
                        </ul>
                    </nav>

                    {/* Theme toggle */}
                    <div className="pt-4 border-t border-slate-200 dark:border-slate-700">
                        <button
                            onClick={toggleTheme}
                            className="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-medium text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-700/50 transition-all duration-200"
                        >
                            {isDark ? (
                                <>
                                    <Sun className="h-5 w-5 text-yellow-500" />
                                    Light Mode
                                </>
                            ) : (
                                <>
                                    <Moon className="h-5 w-5 text-slate-500" />
                                    Dark Mode
                                </>
                            )}
                        </button>
                    </div>
                </div>
            </aside>

            {/* Mobile header */}
            <div className="sticky top-0 z-40 lg:hidden">
                <div className="flex items-center justify-between gap-x-6 glass px-4 py-4 shadow-sm">
                    <div className="flex items-center gap-3">
                        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-primary-500 to-accent-500">
                            <Phone className="h-5 w-5 text-white" />
                        </div>
                        <span className="text-lg font-bold gradient-text">VoiceRemind</span>
                    </div>
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700"
                    >
                        {mobileMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
                    </button>
                </div>

                {/* Mobile menu */}
                {mobileMenuOpen && (
                    <div className="glass border-t border-slate-200 dark:border-slate-700 px-4 py-4 space-y-2">
                        {navigation.map((item) => {
                            const isActive = location.pathname === item.href
                            return (
                                <Link
                                    key={item.name}
                                    to={item.href}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium ${isActive
                                            ? 'bg-gradient-to-r from-primary-500 to-primary-600 text-white'
                                            : 'text-slate-600 dark:text-slate-300'
                                        }`}
                                >
                                    <item.icon className="h-5 w-5" />
                                    {item.name}
                                </Link>
                            )
                        })}
                        <button
                            onClick={toggleTheme}
                            className="flex items-center gap-3 w-full px-4 py-3 rounded-xl text-sm font-medium text-slate-600 dark:text-slate-300"
                        >
                            {isDark ? <Sun className="h-5 w-5 text-yellow-500" /> : <Moon className="h-5 w-5" />}
                            {isDark ? 'Light Mode' : 'Dark Mode'}
                        </button>
                    </div>
                )}
            </div>

            {/* Main content */}
            <main className="lg:pl-72">
                <div className="px-4 py-8 sm:px-6 lg:px-8">
                    <Outlet />
                </div>
            </main>
        </div>
    )
}
