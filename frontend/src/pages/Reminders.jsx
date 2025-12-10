import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
    Bell,
    Clock,
    CheckCircle,
    XCircle,
    Loader2,
    Phone,
    Filter,
    Eye
} from 'lucide-react'
import { remindersApi } from '../services/api'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

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

export default function Reminders() {
    const [reminders, setReminders] = useState([])
    const [loading, setLoading] = useState(true)
    const [statusFilter, setStatusFilter] = useState('all')
    const [page, setPage] = useState(1)
    const [totalPages, setTotalPages] = useState(1)

    const fetchReminders = async () => {
        try {
            setLoading(true)
            const data = await remindersApi.getAll(page, 10)
            setReminders(data.items)
            setTotalPages(data.pages)
        } catch (error) {
            toast.error('Failed to load reminders')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchReminders()
    }, [page])

    // Filter reminders by status
    const filteredReminders = statusFilter === 'all'
        ? reminders
        : reminders.filter(r => r.status === statusFilter)

    const statusOptions = [
        { value: 'all', label: 'All' },
        { value: 'scheduled', label: 'Scheduled' },
        { value: 'processing', label: 'Processing' },
        { value: 'called', label: 'Called' },
        { value: 'failed', label: 'Failed' },
    ]

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Reminders</h1>
                    <p className="mt-1 text-slate-500 dark:text-slate-400">
                        View and manage all voice reminders
                    </p>
                </div>
                <Link to="/reminders/create" className="btn-primary inline-flex items-center gap-2">
                    <Bell className="h-5 w-5" />
                    New Reminder
                </Link>
            </div>

            {/* Filters */}
            <div className="glass-card p-4">
                <div className="flex items-center gap-4">
                    <Filter className="h-5 w-5 text-slate-400" />
                    <div className="flex flex-wrap gap-2">
                        {statusOptions.map(option => (
                            <button
                                key={option.value}
                                onClick={() => setStatusFilter(option.value)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium transition-all ${statusFilter === option.value
                                        ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/30'
                                        : 'bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 hover:bg-slate-200 dark:hover:bg-slate-700'
                                    }`}
                            >
                                {option.label}
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Reminders List */}
            <div className="glass-card overflow-hidden">
                {loading ? (
                    <div className="p-8 space-y-4">
                        {[...Array(5)].map((_, i) => (
                            <div key={i} className="flex items-center gap-4 animate-pulse">
                                <div className="h-12 w-12 bg-slate-200 dark:bg-slate-700 rounded-full" />
                                <div className="flex-1 space-y-2">
                                    <div className="h-4 w-64 bg-slate-200 dark:bg-slate-700 rounded" />
                                    <div className="h-3 w-40 bg-slate-200 dark:bg-slate-700 rounded" />
                                </div>
                                <div className="h-6 w-20 bg-slate-200 dark:bg-slate-700 rounded-full" />
                            </div>
                        ))}
                    </div>
                ) : filteredReminders.length === 0 ? (
                    <div className="text-center py-16">
                        <Bell className="h-12 w-12 mx-auto text-slate-300 dark:text-slate-600" />
                        <p className="mt-4 text-slate-500 dark:text-slate-400">
                            {statusFilter === 'all' ? 'No reminders yet' : `No ${statusFilter} reminders`}
                        </p>
                        <Link to="/reminders/create" className="btn-primary mt-4 inline-flex items-center gap-2">
                            <Bell className="h-5 w-5" />
                            Create a reminder
                        </Link>
                    </div>
                ) : (
                    <>
                        <table className="w-full">
                            <thead className="bg-slate-50 dark:bg-slate-800/50">
                                <tr>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                                        Reminder
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                                        Phone
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                                        Scheduled
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                                        Status
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                                {filteredReminders.map((reminder) => (
                                    <tr key={reminder.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-4">
                                                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center">
                                                    <Phone className="h-5 w-5 text-white" />
                                                </div>
                                                <div className="max-w-xs">
                                                    <p className="text-sm font-medium text-slate-900 dark:text-white truncate">
                                                        {reminder.message.substring(0, 40)}...
                                                    </p>
                                                    <p className="text-xs text-slate-500 dark:text-slate-400">
                                                        ID: {reminder.id.substring(0, 8)}...
                                                    </p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <p className="text-sm text-slate-600 dark:text-slate-300">
                                                {reminder.phone_number}
                                            </p>
                                        </td>
                                        <td className="px-6 py-4">
                                            <p className="text-sm text-slate-600 dark:text-slate-300">
                                                {format(new Date(reminder.scheduled_at), 'MMM d, yyyy')}
                                            </p>
                                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                                {format(new Date(reminder.scheduled_at), 'h:mm a')}
                                            </p>
                                        </td>
                                        <td className="px-6 py-4">
                                            <StatusBadge status={reminder.status} />
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <Link
                                                to={`/reminders/${reminder.id}`}
                                                className="inline-flex items-center gap-1 px-3 py-2 rounded-lg text-sm font-medium text-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-colors"
                                            >
                                                <Eye className="h-4 w-4" />
                                                View
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>

                        {/* Pagination */}
                        {totalPages > 1 && (
                            <div className="flex items-center justify-between px-6 py-4 border-t border-slate-100 dark:border-slate-700">
                                <button
                                    onClick={() => setPage(p => Math.max(1, p - 1))}
                                    disabled={page === 1}
                                    className="btn-secondary text-sm disabled:opacity-50"
                                >
                                    Previous
                                </button>
                                <span className="text-sm text-slate-500">
                                    Page {page} of {totalPages}
                                </span>
                                <button
                                    onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                                    disabled={page === totalPages}
                                    className="btn-secondary text-sm disabled:opacity-50"
                                >
                                    Next
                                </button>
                            </div>
                        )}
                    </>
                )}
            </div>
        </div>
    )
}
