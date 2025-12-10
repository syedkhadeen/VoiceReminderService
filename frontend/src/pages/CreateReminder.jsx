import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
    Phone,
    MessageSquare,
    Calendar,
    Clock,
    User,
    Loader2,
    Sparkles,
    AlertCircle
} from 'lucide-react'
import { usersApi, remindersApi } from '../services/api'
import toast from 'react-hot-toast'

export default function CreateReminder() {
    const navigate = useNavigate()
    const [users, setUsers] = useState([])
    const [loading, setLoading] = useState(true)
    const [submitting, setSubmitting] = useState(false)
    const [errors, setErrors] = useState({})

    const [formData, setFormData] = useState({
        user_id: '',
        phone_number: '',
        message: '',
        scheduled_date: '',
        scheduled_time: '',
    })

    useEffect(() => {
        const fetchUsers = async () => {
            try {
                const data = await usersApi.getAll(1, 100)
                setUsers(data.items)
            } catch (error) {
                toast.error('Failed to load users')
            } finally {
                setLoading(false)
            }
        }
        fetchUsers()
    }, [])

    const validateForm = () => {
        const newErrors = {}

        if (!formData.user_id) {
            newErrors.user_id = 'Please select a user'
        }

        if (!formData.phone_number) {
            newErrors.phone_number = 'Phone number is required'
        } else if (!/^\+\d{10,15}$/.test(formData.phone_number)) {
            newErrors.phone_number = 'Use international format: +1234567890'
        }

        if (!formData.message.trim()) {
            newErrors.message = 'Message is required'
        } else if (formData.message.length < 5) {
            newErrors.message = 'Message must be at least 5 characters'
        }

        if (!formData.scheduled_date) {
            newErrors.scheduled_date = 'Date is required'
        }

        if (!formData.scheduled_time) {
            newErrors.scheduled_time = 'Time is required'
        }

        // Check if date/time is in the future
        if (formData.scheduled_date && formData.scheduled_time) {
            const scheduledAt = new Date(`${formData.scheduled_date}T${formData.scheduled_time}`)
            if (scheduledAt <= new Date()) {
                newErrors.scheduled_date = 'Scheduled time must be in the future'
            }
        }

        setErrors(newErrors)
        return Object.keys(newErrors).length === 0
    }

    const handleSubmit = async (e) => {
        e.preventDefault()

        if (!validateForm()) return

        setSubmitting(true)
        try {
            const scheduledAt = new Date(`${formData.scheduled_date}T${formData.scheduled_time}`)

            await remindersApi.create({
                user_id: formData.user_id,
                phone_number: formData.phone_number,
                message: formData.message,
                scheduled_at: scheduledAt.toISOString(),
            })

            toast.success('Reminder created successfully!')
            navigate('/reminders')
        } catch (error) {
            const message = error.response?.data?.detail || 'Failed to create reminder'
            toast.error(message)
        } finally {
            setSubmitting(false)
        }
    }

    const handleChange = (e) => {
        const { name, value } = e.target
        setFormData(prev => ({ ...prev, [name]: value }))
        // Clear error when user starts typing
        if (errors[name]) {
            setErrors(prev => ({ ...prev, [name]: null }))
        }
    }

    // Get min date (today)
    const today = new Date().toISOString().split('T')[0]

    return (
        <div className="max-w-2xl mx-auto space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-slate-900 dark:text-white">
                    Create Reminder
                </h1>
                <p className="mt-1 text-slate-500 dark:text-slate-400">
                    Schedule a new voice reminder for a user
                </p>
            </div>

            {/* Form */}
            <form onSubmit={handleSubmit} className="glass-card p-8 space-y-6">
                {/* User Selection */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        Select User *
                    </label>
                    <div className="relative">
                        <User className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                        <select
                            name="user_id"
                            value={formData.user_id}
                            onChange={handleChange}
                            className={`input-field pl-12 appearance-none ${errors.user_id ? 'border-red-500 focus:ring-red-500' : ''}`}
                            disabled={loading}
                        >
                            <option value="">Select a user...</option>
                            {users.map(user => (
                                <option key={user.id} value={user.id}>
                                    {user.email}
                                </option>
                            ))}
                        </select>
                    </div>
                    {errors.user_id && (
                        <p className="mt-2 text-sm text-red-500 flex items-center gap-1">
                            <AlertCircle className="h-4 w-4" />
                            {errors.user_id}
                        </p>
                    )}
                    {users.length === 0 && !loading && (
                        <p className="mt-2 text-sm text-amber-500">
                            No users found. Please create a user first.
                        </p>
                    )}
                </div>

                {/* Phone Number */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        Phone Number *
                    </label>
                    <div className="relative">
                        <Phone className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                        <input
                            type="tel"
                            name="phone_number"
                            value={formData.phone_number}
                            onChange={handleChange}
                            placeholder="+1234567890"
                            className={`input-field pl-12 ${errors.phone_number ? 'border-red-500 focus:ring-red-500' : ''}`}
                        />
                    </div>
                    {errors.phone_number ? (
                        <p className="mt-2 text-sm text-red-500 flex items-center gap-1">
                            <AlertCircle className="h-4 w-4" />
                            {errors.phone_number}
                        </p>
                    ) : (
                        <p className="mt-2 text-xs text-slate-500">
                            Use international format with country code (e.g., +1234567890)
                        </p>
                    )}
                </div>

                {/* Message */}
                <div>
                    <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                        Reminder Message *
                    </label>
                    <div className="relative">
                        <MessageSquare className="absolute left-4 top-4 h-5 w-5 text-slate-400" />
                        <textarea
                            name="message"
                            value={formData.message}
                            onChange={handleChange}
                            placeholder="Enter the message to be spoken in the call..."
                            rows={4}
                            className={`input-field pl-12 resize-none ${errors.message ? 'border-red-500 focus:ring-red-500' : ''}`}
                        />
                    </div>
                    {errors.message && (
                        <p className="mt-2 text-sm text-red-500 flex items-center gap-1">
                            <AlertCircle className="h-4 w-4" />
                            {errors.message}
                        </p>
                    )}
                    <p className="mt-2 text-xs text-slate-500">
                        {formData.message.length}/500 characters
                    </p>
                </div>

                {/* Date and Time */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-6">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            Date *
                        </label>
                        <div className="relative">
                            <Calendar className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                            <input
                                type="date"
                                name="scheduled_date"
                                value={formData.scheduled_date}
                                onChange={handleChange}
                                min={today}
                                className={`input-field pl-12 ${errors.scheduled_date ? 'border-red-500 focus:ring-red-500' : ''}`}
                            />
                        </div>
                        {errors.scheduled_date && (
                            <p className="mt-2 text-sm text-red-500 flex items-center gap-1">
                                <AlertCircle className="h-4 w-4" />
                                {errors.scheduled_date}
                            </p>
                        )}
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            Time *
                        </label>
                        <div className="relative">
                            <Clock className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                            <input
                                type="time"
                                name="scheduled_time"
                                value={formData.scheduled_time}
                                onChange={handleChange}
                                className={`input-field pl-12 ${errors.scheduled_time ? 'border-red-500 focus:ring-red-500' : ''}`}
                            />
                        </div>
                        {errors.scheduled_time && (
                            <p className="mt-2 text-sm text-red-500 flex items-center gap-1">
                                <AlertCircle className="h-4 w-4" />
                                {errors.scheduled_time}
                            </p>
                        )}
                    </div>
                </div>

                {/* Submit Button */}
                <div className="pt-4">
                    <button
                        type="submit"
                        disabled={submitting || users.length === 0}
                        className="btn-primary w-full inline-flex items-center justify-center gap-2"
                    >
                        {submitting ? (
                            <>
                                <Loader2 className="h-5 w-5 animate-spin" />
                                Creating Reminder...
                            </>
                        ) : (
                            <>
                                <Sparkles className="h-5 w-5" />
                                Create Reminder
                            </>
                        )}
                    </button>
                </div>
            </form>
        </div>
    )
}
