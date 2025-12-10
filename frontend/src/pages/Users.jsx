import { useEffect, useState } from 'react'
import { Users as UsersIcon, Plus, Mail, Trash2, X, Loader2 } from 'lucide-react'
import { usersApi } from '../services/api'
import { format } from 'date-fns'
import toast from 'react-hot-toast'

// Modal component
function Modal({ isOpen, onClose, title, children }) {
    if (!isOpen) return null

    return (
        <div className="fixed inset-0 z-50 overflow-y-auto">
            <div className="flex min-h-full items-center justify-center p-4">
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm" onClick={onClose} />
                <div className="relative glass-card w-full max-w-md p-6 transform transition-all">
                    <div className="flex items-center justify-between mb-6">
                        <h3 className="text-lg font-semibold text-slate-900 dark:text-white">{title}</h3>
                        <button
                            onClick={onClose}
                            className="p-2 rounded-lg hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
                        >
                            <X className="h-5 w-5 text-slate-500" />
                        </button>
                    </div>
                    {children}
                </div>
            </div>
        </div>
    )
}

export default function Users() {
    const [users, setUsers] = useState([])
    const [loading, setLoading] = useState(true)
    const [modalOpen, setModalOpen] = useState(false)
    const [email, setEmail] = useState('')
    const [submitting, setSubmitting] = useState(false)
    const [page, setPage] = useState(1)
    const [totalPages, setTotalPages] = useState(1)

    const fetchUsers = async () => {
        try {
            setLoading(true)
            const data = await usersApi.getAll(page, 10)
            setUsers(data.items)
            setTotalPages(data.pages)
        } catch (error) {
            toast.error('Failed to load users')
        } finally {
            setLoading(false)
        }
    }

    useEffect(() => {
        fetchUsers()
    }, [page])

    const handleCreateUser = async (e) => {
        e.preventDefault()
        if (!email.trim()) return

        setSubmitting(true)
        try {
            await usersApi.create(email)
            toast.success('User created successfully!')
            setEmail('')
            setModalOpen(false)
            fetchUsers()
        } catch (error) {
            const message = error.response?.data?.detail || 'Failed to create user'
            toast.error(message)
        } finally {
            setSubmitting(false)
        }
    }

    const handleDeleteUser = async (id, userEmail) => {
        if (!confirm(`Are you sure you want to delete ${userEmail}?`)) return

        try {
            await usersApi.delete(id)
            toast.success('User deleted successfully')
            fetchUsers()
        } catch (error) {
            toast.error('Failed to delete user')
        }
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900 dark:text-white">Users</h1>
                    <p className="mt-1 text-slate-500 dark:text-slate-400">
                        Manage users who can receive voice reminders
                    </p>
                </div>
                <button onClick={() => setModalOpen(true)} className="btn-primary inline-flex items-center gap-2">
                    <Plus className="h-5 w-5" />
                    Add User
                </button>
            </div>

            {/* Users List */}
            <div className="glass-card overflow-hidden">
                {loading ? (
                    <div className="p-8 space-y-4">
                        {[...Array(5)].map((_, i) => (
                            <div key={i} className="flex items-center gap-4 animate-pulse">
                                <div className="h-12 w-12 bg-slate-200 dark:bg-slate-700 rounded-full" />
                                <div className="flex-1 space-y-2">
                                    <div className="h-4 w-48 bg-slate-200 dark:bg-slate-700 rounded" />
                                    <div className="h-3 w-32 bg-slate-200 dark:bg-slate-700 rounded" />
                                </div>
                            </div>
                        ))}
                    </div>
                ) : users.length === 0 ? (
                    <div className="text-center py-16">
                        <UsersIcon className="h-12 w-12 mx-auto text-slate-300 dark:text-slate-600" />
                        <p className="mt-4 text-slate-500 dark:text-slate-400">No users yet</p>
                        <button onClick={() => setModalOpen(true)} className="btn-primary mt-4 inline-flex items-center gap-2">
                            <Plus className="h-5 w-5" />
                            Add your first user
                        </button>
                    </div>
                ) : (
                    <>
                        <table className="w-full">
                            <thead className="bg-slate-50 dark:bg-slate-800/50">
                                <tr>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                                        User
                                    </th>
                                    <th className="px-6 py-4 text-left text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                                        Created
                                    </th>
                                    <th className="px-6 py-4 text-right text-xs font-semibold text-slate-500 dark:text-slate-400 uppercase tracking-wider">
                                        Actions
                                    </th>
                                </tr>
                            </thead>
                            <tbody className="divide-y divide-slate-100 dark:divide-slate-700">
                                {users.map((user) => (
                                    <tr key={user.id} className="hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors">
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-4">
                                                <div className="h-10 w-10 rounded-full bg-gradient-to-br from-primary-500 to-accent-500 flex items-center justify-center text-white font-semibold">
                                                    {user.email.charAt(0).toUpperCase()}
                                                </div>
                                                <div>
                                                    <p className="text-sm font-medium text-slate-900 dark:text-white">{user.email}</p>
                                                    <p className="text-xs text-slate-500 dark:text-slate-400">ID: {user.id.substring(0, 8)}...</p>
                                                </div>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <p className="text-sm text-slate-600 dark:text-slate-300">
                                                {format(new Date(user.created_at), 'MMM d, yyyy')}
                                            </p>
                                            <p className="text-xs text-slate-500 dark:text-slate-400">
                                                {format(new Date(user.created_at), 'h:mm a')}
                                            </p>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            <button
                                                onClick={() => handleDeleteUser(user.id, user.email)}
                                                className="p-2 rounded-lg text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                                            >
                                                <Trash2 className="h-5 w-5" />
                                            </button>
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

            {/* Create User Modal */}
            <Modal isOpen={modalOpen} onClose={() => setModalOpen(false)} title="Add New User">
                <form onSubmit={handleCreateUser} className="space-y-6">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-2">
                            Email Address
                        </label>
                        <div className="relative">
                            <Mail className="absolute left-4 top-1/2 -translate-y-1/2 h-5 w-5 text-slate-400" />
                            <input
                                type="email"
                                value={email}
                                onChange={(e) => setEmail(e.target.value)}
                                placeholder="user@example.com"
                                className="input-field pl-12"
                                required
                            />
                        </div>
                    </div>

                    <div className="flex gap-3">
                        <button
                            type="button"
                            onClick={() => setModalOpen(false)}
                            className="btn-secondary flex-1"
                        >
                            Cancel
                        </button>
                        <button
                            type="submit"
                            disabled={submitting}
                            className="btn-primary flex-1 inline-flex items-center justify-center gap-2"
                        >
                            {submitting ? (
                                <>
                                    <Loader2 className="h-5 w-5 animate-spin" />
                                    Creating...
                                </>
                            ) : (
                                <>
                                    <Plus className="h-5 w-5" />
                                    Create User
                                </>
                            )}
                        </button>
                    </div>
                </form>
            </Modal>
        </div>
    )
}
