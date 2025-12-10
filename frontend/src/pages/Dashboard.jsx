import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
    Bell,
    Clock,
    CheckCircle,
    XCircle,
    Loader2,
    Users,
    TrendingUp,
    Phone,
    ArrowRight,
    Sparkles
} from 'lucide-react'
import { remindersApi, usersApi } from '../services/api'
import { format } from 'date-fns'

// Stat card component
function StatCard({ title, value, icon: Icon, color, gradient }) {
    return (
        <div className="glass-card p-6 hover-lift">
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm font-medium text-slate-500 dark:text-slate-400">{title}</p>
                    <p className="text-3xl font-bold mt-2 text-slate-900 dark:text-white">{value}</p>
                </div>
                <div className={`p-4 rounded-2xl bg-gradient-to-br ${gradient}`}>
                    <Icon className="h-6 w-6 text-white" />
                </div>
            </div>
        </div>
    )
}

// Status badge component
function StatusBadge({ status }) {
    const config = {
        scheduled: { icon: Clock, class: 'status-scheduled', label: 'Scheduled' },
        processing: { icon: Loader2, class: 'status-processing', label: 'Processing' },
        called: { icon: CheckCircle, class: 'status-called', label: 'Called' },
        failed: { icon: XCircle, class: 'status-failed', label: 'Failed' },
    }

    const { icon: Icon, class: className, label } = config[status] || config.scheduled

    return (
        <span className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${className}`}>
            <Icon className={`h-3.5 w-3.5 ${status === 'processing' ? 'animate-spin' : ''}`} />
            {label}
        </span>
    )
}

// Skeleton loader
function SkeletonCard() {
    return (
        <div className="glass-card p-6 animate-pulse">
            <div className="flex items-center justify-between">
                <div className="space-y-3">
                    <div className="h-4 w-24 bg-slate-200 dark:bg-slate-700 rounded" />
                    <div className="h-8 w-16 bg-slate-200 dark:bg-slate-700 rounded" />
                </div>
                <div className="h-14 w-14 bg-slate-200 dark:bg-slate-700 rounded-2xl" />
            </div>
        </div>
    )
}

export default function Dashboard() {
    const [stats, setStats] = useState(null)
    const [recentReminders, setRecentReminders] = useState([])
    const [usersCount, setUsersCount] = useState(0)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [statsData, remindersData, usersData] = await Promise.all([
                    remindersApi.getStats(),
                    remindersApi.getAll(1, 5),
                    usersApi.getAll(1, 1),
                ])
                setStats(statsData)
                setRecentReminders(remindersData.items)
                setUsersCount(usersData.total)
            } catch (error) {
                console.error('Error fetching dashboard data:', error)
            } finally {
                setLoading(false)
            }
        }

        fetchData()
    }, [])

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                        Dashboard
                    </h1>
                    <p className="mt-1 text-slate-500 dark:text-slate-400">
                        Welcome back! Here's what's happening with your reminders.
                    </p>
                </div>
                <Link to="/reminders/create" className="btn-primary inline-flex items-center gap-2">
                    <Sparkles className="h-5 w-5" />
                    Create Reminder
                </Link>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
                {loading ? (
                    <>
                        <SkeletonCard />
                        <SkeletonCard />
                        <SkeletonCard />
                        <SkeletonCard />
                    </>
                ) : (
                    <>
                        <StatCard
                            title="Total Reminders"
                            value={stats?.total || 0}
                            icon={Bell}
                            gradient="from-primary-500 to-primary-600"
                        />
                        <StatCard
                            title="Scheduled"
                            value={stats?.scheduled || 0}
                            icon={Clock}
                            gradient="from-blue-500 to-blue-600"
                        />
                        <StatCard
                            title="Completed"
                            value={stats?.called || 0}
                            icon={CheckCircle}
                            gradient="from-green-500 to-green-600"
                        />
                        <StatCard
                            title="Failed"
                            value={stats?.failed || 0}
                            icon={XCircle}
                            gradient="from-red-500 to-red-600"
                        />
                    </>
                )}
            </div>

            {/* Secondary Stats */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="glass-card p-6 hover-lift">
                    <div className="flex items-center gap-4">
                        <div className="p-4 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600">
                            <Users className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Total Users</p>
                            <p className="text-2xl font-bold text-slate-900 dark:text-white">{usersCount}</p>
                        </div>
                    </div>
                </div>

                <div className="glass-card p-6 hover-lift">
                    <div className="flex items-center gap-4">
                        <div className="p-4 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600">
                            <Loader2 className="h-6 w-6 text-white animate-spin" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Processing</p>
                            <p className="text-2xl font-bold text-slate-900 dark:text-white">{stats?.processing || 0}</p>
                        </div>
                    </div>
                </div>

                <div className="glass-card p-6 hover-lift">
                    <div className="flex items-center gap-4">
                        <div className="p-4 rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600">
                            <TrendingUp className="h-6 w-6 text-white" />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-slate-500 dark:text-slate-400">Success Rate</p>
                            <p className="text-2xl font-bold text-slate-900 dark:text-white">
                                {stats?.total > 0
                                    ? Math.round((stats.called / stats.total) * 100)
                                    : 0}%
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Recent Reminders */}
            <div className="glass-card p-6">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-lg font-semibold text-slate-900 dark:text-white">
                        Recent Reminders
                    </h2>
                    <Link
                        to="/reminders"
                        className="text-sm font-medium text-primary-500 hover:text-primary-600 inline-flex items-center gap-1"
                    >
                        View all
                        <ArrowRight className="h-4 w-4" />
                    </Link>
                </div>

                {loading ? (
                    <div className="space-y-4">
                        {[...Array(3)].map((_, i) => (
                            <div key={i} className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 animate-pulse">
                                <div className="h-10 w-10 bg-slate-200 dark:bg-slate-700 rounded-full" />
                                <div className="flex-1 space-y-2">
                                    <div className="h-4 w-48 bg-slate-200 dark:bg-slate-700 rounded" />
                                    <div className="h-3 w-32 bg-slate-200 dark:bg-slate-700 rounded" />
                                </div>
                                <div className="h-6 w-20 bg-slate-200 dark:bg-slate-700 rounded-full" />
                            </div>
                        ))}
                    </div>
                ) : recentReminders.length === 0 ? (
                    <div className="text-center py-12">
                        <Bell className="h-12 w-12 mx-auto text-slate-300 dark:text-slate-600" />
                        <p className="mt-4 text-slate-500 dark:text-slate-400">No reminders yet</p>
                        <Link to="/reminders/create" className="btn-primary mt-4 inline-flex items-center gap-2">
                            <Sparkles className="h-5 w-5" />
                            Create your first reminder
                        </Link>
                    </div>
                ) : (
                    <div className="space-y-3">
                        {recentReminders.map((reminder) => (
                            <Link
                                key={reminder.id}
                                to={`/reminders/${reminder.id}`}
                                className="flex items-center gap-4 p-4 rounded-xl bg-slate-50 dark:bg-slate-800/50 hover:bg-slate-100 dark:hover:bg-slate-700/50 transition-colors"
                            >
                                <div className="flex-shrink-0 h-10 w-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                                    <Phone className="h-5 w-5 text-white" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                                        {reminder.message.substring(0, 50)}...
                                    </p>
                                    <p className="text-xs text-slate-500 dark:text-slate-400">
                                        {reminder.phone_number} • {format(new Date(reminder.scheduled_at), 'MMM d, yyyy h:mm a')}
                                    </p>
                                </div>
                                <StatusBadge status={reminder.status} />
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </div>
    )
}
