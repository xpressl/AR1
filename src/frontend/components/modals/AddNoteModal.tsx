'use client';

import React, { useState } from 'react';
import { Modal, Button, Input, Select, TextArea } from '@/components/common';
import { X, FileText, Phone, Mail, AlertTriangle } from 'lucide-react';

interface AddNoteModalProps {
  isOpen: boolean;
  onClose: () => void;
  customerId: number;
  customerName: string;
  onNoteAdded?: () => void;
}

type NoteType = 'general' | 'phone_call' | 'email' | 'promise_to_pay' | 'dispute' | 'internal';

interface NoteFormData {
  note_type: NoteType;
  content: string;
  contact_name?: string;
  contact_method?: string;
  follow_up_required: boolean;
  follow_up_date?: string;
  // Promise-to-pay specific
  promise_amount?: number;
  promise_date?: string;
}

const noteTypeOptions = [
  { value: 'general', label: 'General Note' },
  { value: 'phone_call', label: 'Phone Call' },
  { value: 'email', label: 'Email Correspondence' },
  { value: 'promise_to_pay', label: 'Promise to Pay' },
  { value: 'dispute', label: 'Dispute' },
  { value: 'internal', label: 'Internal Note' },
];

const noteTypeIcons: Record<NoteType, React.ReactNode> = {
  general: <FileText className="h-5 w-5" />,
  phone_call: <Phone className="h-5 w-5" />,
  email: <Mail className="h-5 w-5" />,
  promise_to_pay: <AlertTriangle className="h-5 w-5" />,
  dispute: <AlertTriangle className="h-5 w-5" />,
  internal: <FileText className="h-5 w-5" />,
};

export const AddNoteModal: React.FC<AddNoteModalProps> = ({
  isOpen,
  onClose,
  customerId,
  customerName,
  onNoteAdded,
}) => {
  const [formData, setFormData] = useState<NoteFormData>({
    note_type: 'general',
    content: '',
    follow_up_required: false,
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
        note_type: formData.note_type,
        content: formData.content,
        contact_name: formData.contact_name || null,
        contact_method: formData.contact_method || null,
        follow_up_required: formData.follow_up_required,
        follow_up_date: formData.follow_up_date || null,
        promise_amount: formData.promise_amount || null,
        promise_date: formData.promise_date || null,
        promise_status: formData.note_type === 'promise_to_pay' ? 'pending' : null,
      };

      const response = await fetch('/api/notes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to add note');
      }

      // Reset form and close
      setFormData({
        note_type: 'general',
        content: '',
        follow_up_required: false,
      });
      onNoteAdded?.();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const isPromiseType = formData.note_type === 'promise_to_pay';

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Note" size="lg">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b pb-3">
          <div>
            <h3 className="text-lg font-semibold">Add Note</h3>
            <p className="text-sm text-gray-500">Customer: {customerName}</p>
          </div>
          <button
            type="button"
            onClick={onClose}
            className="text-gray-400 hover:text-gray-500"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        {/* Note Type Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Note Type
          </label>
          <div className="grid grid-cols-3 gap-2">
            {noteTypeOptions.map((option) => (
              <button
                key={option.value}
                type="button"
                onClick={() =>
                  setFormData({ ...formData, note_type: option.value as NoteType })
                }
                className={`flex items-center gap-2 p-3 rounded-lg border transition-colors ${
                  formData.note_type === option.value
                    ? 'border-blue-500 bg-blue-50 text-blue-700'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
              >
                {noteTypeIcons[option.value as NoteType]}
                <span className="text-sm">{option.label}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Contact Info (for phone/email) */}
        {(formData.note_type === 'phone_call' || formData.note_type === 'email') && (
          <div className="grid grid-cols-2 gap-4">
            <Input
              label="Contact Name"
              value={formData.contact_name || ''}
              onChange={(e) =>
                setFormData({ ...formData, contact_name: e.target.value })
              }
              placeholder="Who did you speak with?"
            />
            <Input
              label="Contact Method"
              value={formData.contact_method || ''}
              onChange={(e) =>
                setFormData({ ...formData, contact_method: e.target.value })
              }
              placeholder="Phone/Email"
            />
          </div>
        )}

        {/* Promise-to-Pay Fields */}
        {isPromiseType && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 space-y-4">
            <h4 className="font-medium text-yellow-800">Promise to Pay Details</h4>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Promise Amount"
                type="number"
                step="0.01"
                value={formData.promise_amount || ''}
                onChange={(e) =>
                  setFormData({
                    ...formData,
                    promise_amount: parseFloat(e.target.value) || undefined,
                  })
                }
                placeholder="0.00"
                required={isPromiseType}
              />
              <Input
                label="Promise Date"
                type="date"
                value={formData.promise_date || ''}
                onChange={(e) =>
                  setFormData({ ...formData, promise_date: e.target.value })
                }
                required={isPromiseType}
              />
            </div>
          </div>
        )}

        {/* Note Content */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Note Content *
          </label>
          <textarea
            value={formData.content}
            onChange={(e) => setFormData({ ...formData, content: e.target.value })}
            rows={4}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            placeholder={
              isPromiseType
                ? 'Describe the promise details, payment method, etc.'
                : 'Enter your note here...'
            }
            required
          />
        </div>

        {/* Follow-up */}
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2">
            <input
              type="checkbox"
              checked={formData.follow_up_required}
              onChange={(e) =>
                setFormData({ ...formData, follow_up_required: e.target.checked })
              }
              className="h-4 w-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">Follow-up Required</span>
          </label>
          {formData.follow_up_required && (
            <Input
              type="date"
              value={formData.follow_up_date || ''}
              onChange={(e) =>
                setFormData({ ...formData, follow_up_date: e.target.value })
              }
              className="w-40"
            />
          )}
        </div>

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
          <Button type="submit" disabled={loading || !formData.content.trim()}>
            {loading ? 'Saving...' : 'Save Note'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default AddNoteModal;
