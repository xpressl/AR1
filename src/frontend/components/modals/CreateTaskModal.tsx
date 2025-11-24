'use client';

import React, { useState } from 'react';
import { Modal, Button, Input } from '@/components/common';
import { X, CheckSquare, Calendar, User, AlertCircle } from 'lucide-react';

interface CreateTaskModalProps {
  isOpen: boolean;
  onClose: () => void;
  customerId: number;
  customerName: string;
  invoiceId?: number;
  onTaskCreated?: () => void;
}

type TaskType = 'follow_up' | 'call' | 'email' | 'review' | 'escalation' | 'other';
type TaskPriority = 'low' | 'medium' | 'high' | 'critical';

interface TaskFormData {
  task_type: TaskType;
  title: string;
  description: string;
  priority: TaskPriority;
  due_date: string;
  assigned_to?: string;
}

const taskTypeOptions = [
  { value: 'follow_up', label: 'Follow Up', description: 'General follow-up action' },
  { value: 'call', label: 'Phone Call', description: 'Schedule a phone call' },
  { value: 'email', label: 'Send Email', description: 'Email communication needed' },
  { value: 'review', label: 'Account Review', description: 'Review account status' },
  { value: 'escalation', label: 'Escalation', description: 'Escalate to management' },
  { value: 'other', label: 'Other', description: 'Other task type' },
];

const priorityOptions = [
  { value: 'low', label: 'Low', color: 'bg-gray-100 text-gray-700' },
  { value: 'medium', label: 'Medium', color: 'bg-blue-100 text-blue-700' },
  { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-700' },
  { value: 'critical', label: 'Critical', color: 'bg-red-100 text-red-700' },
];

export const CreateTaskModal: React.FC<CreateTaskModalProps> = ({
  isOpen,
  onClose,
  customerId,
  customerName,
  invoiceId,
  onTaskCreated,
}) => {
  const [formData, setFormData] = useState<TaskFormData>({
    task_type: 'follow_up',
    title: '',
    description: '',
    priority: 'medium',
    due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        customer_id: customerId,
        invoice_id: invoiceId || null,
        task_type: formData.task_type,
        title: formData.title,
        description: formData.description || null,
        priority: formData.priority,
        due_date: formData.due_date,
        assigned_to: formData.assigned_to || null,
        status: 'pending',
      };

      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to create task');
      }

      // Reset form and close
      setFormData({
        task_type: 'follow_up',
        title: '',
        description: '',
        priority: 'medium',
        due_date: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
      });
      onTaskCreated?.();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  // Auto-generate title based on task type
  const generateTitle = (type: TaskType): string => {
    const titles: Record<TaskType, string> = {
      follow_up: `Follow up with ${customerName}`,
      call: `Call ${customerName}`,
      email: `Email ${customerName}`,
      review: `Review ${customerName} account`,
      escalation: `Escalate ${customerName} account`,
      other: '',
    };
    return titles[type];
  };

  const handleTaskTypeChange = (type: TaskType) => {
    setFormData({
      ...formData,
      task_type: type,
      title: formData.title || generateTitle(type),
    });
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Create Task" size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b pb-3">
          <div className="flex items-center gap-2">
            <CheckSquare className="h-5 w-5 text-green-600" />
            <div>
              <h3 className="text-lg font-semibold">Create Task</h3>
              <p className="text-sm text-gray-500">Customer: {customerName}</p>
            </div>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Task Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Task Type
          </label>
          <div className="grid grid-cols-3 gap-2">
            {taskTypeOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() => handleTaskTypeChange(option.value as TaskType)}
                className={`p-3 rounded-lg border text-left transition-colors ${
                  formData.task_type === option.value
                    ? 'border-green-500 bg-green-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                <div className="font-medium text-sm">{option.label}</div>
                <div className="text-xs text-gray-500">{option.description}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Title */}
        <Input
          label="Task Title"
          value={formData.title}
          onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          placeholder="Enter task title"
          required
        />

        {/* Description */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description (optional)
          </label>
          <textarea
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
            placeholder="Add additional details..."
          />
        </div>

        {/* Priority and Due Date */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Priority
            </label>
            <div className="flex gap-2">
              {priorityOptions.map((option) => (
                <button
                  key={option.value}
                  type="button"
                  onClick={() =>
                    setFormData({ ...formData, priority: option.value as TaskPriority })
                  }
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    formData.priority === option.value
                      ? `${option.color} ring-2 ring-offset-1 ring-current`
                      : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                  }`}
                >
                  {option.label}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              <Calendar className="h-4 w-4 inline mr-1" />
              Due Date
            </label>
            <Input
              type="date"
              value={formData.due_date}
              onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
              required
            />
          </div>
        </div>

        {/* Assigned To */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            <User className="h-4 w-4 inline mr-1" />
            Assign To (optional)
          </label>
          <select
            value={formData.assigned_to || ''}
            onChange={(e) => setFormData({ ...formData, assigned_to: e.target.value })}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500"
          >
            <option value="">-- Unassigned --</option>
            <option value="current_user">Assign to me</option>
            {/* TODO: Populate with actual users */}
          </select>
        </div>

        {/* Critical Priority Warning */}
        {formData.priority === 'critical' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 flex items-start gap-2">
            <AlertCircle className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
            <div>
              <div className="font-medium text-red-800">Critical Priority</div>
              <div className="text-sm text-red-600">
                This task will be flagged as urgent and may trigger notifications.
              </div>
            </div>
          </div>
        )}

        {/* Error Display */}
        {error && (
          <div className="bg-red-50 text-red-600 p-3 rounded-lg text-sm">
            {error}
          </div>
        )}

        {/* Actions */}
        <div className="flex justify-end gap-3 pt-4 border-t">
          <Button type="button" variant="secondary" onClick={onClose}>
            Cancel
          </Button>
          <Button type="submit" disabled={loading || !formData.title.trim()}>
            {loading ? 'Creating...' : 'Create Task'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default CreateTaskModal;
