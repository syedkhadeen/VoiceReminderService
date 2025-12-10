import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import {
    ArrowLeft,
    Phone,
    MessageSquare,
    Calendar,
    Clock,
    User,
    CheckCircle,
    XCircle,
    Loader2,
    FileText,
    Activity
} from 'lucide-react'
import { remindersApi } from '../services/api'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

// Status configuration
const statusConfig = {
    scheduled: {
        icon: Clock,
        class: 'status-scheduled',
        label: 'Scheduled',
        color: 'text-blue-500',
        bgColor: 'bg-blue-500'
    },
    processing: {
        icon: Loader2,
        class: 'status-processing',
        label: 'Processing',
        color: 'text-yellow-500',
        bgColor: 'bg-yellow-500'
    },
    called: {
        icon: CheckCircle,
        class: 'status-called',
        label: 'Called',
        color: 'text-green-500',
        bgColor: 'bg-green-500'
    },
    failed: {
        icon: XCircle,
        class: 'status-failed',
        label: 'Failed',
        color: 'text-red-500',
        bgColor: 'bg-red-500'
    },
}

export default function ReminderDetail() {
    const { id } = useParams()
    const [reminder, setReminder] = useState(null)
    const [loading, setLoading] = useState(true)

    useEffect(() => {
        const fetchReminder = async () => {
            try {
                const data = await remindersApi.getById(id)
                setReminder(data)
            } catch (error) {
                toast.error('Failed to load reminder')
            } finally {
                setLoading(false)
            }
        }
        fetchReminder()

        // Poll for updates if status is processing
        const interval = setInterval(async () => {
            try {
                const data = await remindersApi.getById(id)
                setReminder(data)
                if (data.status !== 'processing' && data.status !== 'scheduled') {
                    clearInterval(interval)
                }
            } catch (error) {
                clearInterval(interval)
            }
        }, 5000)

        return () => clearInterval(interval)
    }, [id])

    if (loading) {
        return (
            <div className="space-y-8">
                <div className="h-8 w-32 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
                <div className="glass-card p-8 space-y-6">
                    <div className="h-8 w-48 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
                    <div className="h-4 w-full bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
                    <div className="h-4 w-3/4 bg-slate-200 dark:bg-slate-700 rounded animate-pulse" />
                </div>
            </div>
        )
    }

    if (!reminder) {
        return (
            <div className="text-center py-16">
                <p className="text-slate-500">Reminder not found</p>
                <Link to="/reminders" className="btn-primary mt-4">
                    Back to Reminders
                </Link>
            </div>
        )
    }

    const status = statusConfig[reminder.status] || statusConfig.scheduled
    const StatusIcon = status.icon

    return (
        <div className="space-y-8 max-w-4xl mx-auto">
            {/* Back button */}
            <Link
                to="/reminders"
                className="inline-flex items-center gap-2 text-slate-500 hover:text-slate-700 dark:hover:text-slate-300 transition-colors"
            >
                <ArrowLeft className="h-5 w-5" />
                Back to Reminders
            </Link>

            {/* Header Card */}
            <div className="glass-card p-8">
                <div className="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
                    <div className="flex items-start gap-4">
                        <div className={`p-4 rounded-2xl ${status.bgColor}/10`}>
                            <StatusIcon className={`h-8 w-8 ${status.color} ${reminder.status === 'processing' ? 'animate-spin' : ''}`} />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-slate-900 dark:text-white">
                                Reminder Details
                            </h1>
                            <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                                ID: {reminder.id}
                            </p>
                        </div>
                    </div>
                    <span className={`inline-flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${status.class}`}>
                        <StatusIcon className={`h-4 w-4 ${reminder.status === 'processing' ? 'animate-spin' : ''}`} />
                        {status.label}
                    </span>
                </div>
            </div>

            {/* Details Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Message */}
                <div className="glass-card p-6 md:col-span-2">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg bg-primary-100 dark:bg-primary-900/30">
                            <MessageSquare className="h-5 w-5 text-primary-500" />
                        </div>
                        <h3 className="font-semibold text-slate-900 dark:text-white">Message</h3>
                    </div>
                    <p className="text-slate-600 dark:text-slate-300 leading-relaxed">
                        {reminder.message}
                    </p>
                </div>

                {/* Phone Number */}
                <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg bg-green-100 dark:bg-green-900/30">
                            <Phone className="h-5 w-5 text-green-500" />
                        </div>
                        <h3 className="font-semibold text-slate-900 dark:text-white">Phone Number</h3>
                    </div>
                    <p className="text-xl font-mono text-slate-600 dark:text-slate-300">
                        {reminder.phone_number}
                    </p>
                </div>

                {/* Scheduled Time */}
                <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg bg-blue-100 dark:bg-blue-900/30">
                            <Calendar className="h-5 w-5 text-blue-500" />
                        </div>
                        <h3 className="font-semibold text-slate-900 dark:text-white">Scheduled For</h3>
                    </div>
                    <p className="text-xl font-medium text-slate-600 dark:text-slate-300">
                        {format(new Date(reminder.scheduled_at), 'MMMM d, yyyy')}
                    </p>
                    <p className="text-sm text-slate-500 dark:text-slate-400 mt-1">
                        {format(new Date(reminder.scheduled_at), 'h:mm a')}
                    </p>
                </div>

                {/* User ID */}
                <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-4">
                        <div className="p-2 rounded-lg bg-violet-100 dark:bg-violet-900/30">
                            <User className="h-5 w-5 text-violet-500" />
                        </div>
                        <h3 className="font-semibold text-slate-900 dark:text-white">User ID</h3>
                    </div>
                    <p className="text-sm font-mono text-slate-600 dark:text-slate-300 break-all">
                        {reminder.user_id}
                    </p>
                </div>

                {/* External Call ID */}
                {reminder.external_call_id && (
                    <div className="glass-card p-6">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="p-2 rounded-lg bg-amber-100 dark:bg-amber-900/30">
                                <Activity className="h-5 w-5 text-amber-500" />
                            </div>
                            <h3 className="font-semibold text-slate-900 dark:text-white">External Call ID</h3>
                        </div>
                        <p className="text-sm font-mono text-slate-600 dark:text-slate-300 break-all">
                            {reminder.external_call_id}
                        </p>
                    </div>
                )}
            </div>

            {/* Call Logs Timeline */}
            {reminder.call_logs && reminder.call_logs.length > 0 && (
                <div className="glass-card p-6">
                    <div className="flex items-center gap-3 mb-6">
                        <div className="p-2 rounded-lg bg-slate-100 dark:bg-slate-800">
                            <FileText className="h-5 w-5 text-slate-500" />
                        </div>
                        <h3 className="font-semibold text-slate-900 dark:text-white">Call Logs</h3>
                    </div>

                    <div className="space-y-4">
                        {reminder.call_logs.map((log, index) => (
                            <div
                                key={log.id}
                                className="relative pl-8 pb-4 last:pb-0"
                            >
                                {/* Timeline line */}
                                {index < reminder.call_logs.length - 1 && (
                                    <div className="absolute left-3 top-6 bottom-0 w-0.5 bg-slate-200 dark:bg-slate-700" />
                                )}

                                {/* Timeline dot */}
                                <div className={`absolute left-0 top-1 h-6 w-6 rounded-full flex items-center justify-center ${log.status === 'completed' || log.status === 'ended'
                                        ? 'bg-green-100 dark:bg-green-900/30'
                                        : log.status === 'failed'
                                            ? 'bg-red-100 dark:bg-red-900/30'
                                            : 'bg-blue-100 dark:bg-blue-900/30'
                                    }`}>
                                    {log.status === 'completed' || log.status === 'ended' ? (
                                        <CheckCircle className="h-4 w-4 text-green-500" />
                                    ) : log.status === 'failed' ? (
                                        <XCircle className="h-4 w-4 text-red-500" />
                                    ) : (
                                        <Clock className="h-4 w-4 text-blue-500" />
                                    )}
                                </div>

                                <div className="bg-slate-50 dark:bg-slate-800/50 rounded-xl p-4">
                                    <div className="flex items-center justify-between mb-2">
                                        <span className={`text-sm font-medium ${log.status === 'completed' || log.status === 'ended'
                                                ? 'text-green-600 dark:text-green-400'
                                                : log.status === 'failed'
                                                    ? 'text-red-600 dark:text-red-400'
                                                    : 'text-blue-600 dark:text-blue-400'
                                            }`}>
                                            {log.status.charAt(0).toUpperCase() + log.status.slice(1)}
                                        </span>
                                        <span className="text-xs text-slate-500">
                                            {format(new Date(log.received_at), 'MMM d, yyyy h:mm:ss a')}
                                        </span>
                                    </div>

                                    <p className="text-xs text-slate-500 mb-2">
                                        Call ID: {log.external_call_id}
                                    </p>

                                    {log.transcript && (
                                        <div className="mt-3 p-3 bg-white dark:bg-slate-900/50 rounded-lg">
                                            <p className="text-xs font-medium text-slate-500 mb-1">Transcript</p>
                                            <p className="text-sm text-slate-600 dark:text-slate-300">
                                                {log.transcript}
                                            </p>
                                        </div>
                                    )}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Timestamps */}
            <div className="glass-card p-6">
                <h3 className="font-semibold text-slate-900 dark:text-white mb-4">Timestamps</h3>
                <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>
                        <p className="text-slate-500">Created</p>
                        <p className="text-slate-700 dark:text-slate-300">
                            {format(new Date(reminder.created_at), 'MMM d, yyyy h:mm:ss a')}
                        </p>
                    </div>
                    <div>
                        <p className="text-slate-500">Updated</p>
                        <p className="text-slate-700 dark:text-slate-300">
                            {format(new Date(reminder.updated_at), 'MMM d, yyyy h:mm:ss a')}
                        </p>
                    </div>
                </div>
            </div>
        </div>
    )
}
