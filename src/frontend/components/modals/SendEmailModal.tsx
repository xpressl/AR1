'use client';

import React, { useState, useEffect } from 'react';
import { Modal, Button, Input } from '@/components/common';
import { X, Mail, Paperclip, Eye } from 'lucide-react';

interface SendEmailModalProps {
  isOpen: boolean;
  onClose: () => void;
  customerId: number;
  customerName: string;
  customerEmail?: string;
  emailType?: 'reminder' | 'statement' | 'custom';
  invoiceIds?: number[];
  onEmailSent?: () => void;
}

interface EmailTemplate {
  id: string;
  name: string;
  subject: string;
  body: string;
}

const defaultTemplates: EmailTemplate[] = [
  {
    id: 'reminder_gentle',
    name: 'Gentle Reminder',
    subject: 'Friendly Reminder: Invoice Payment Due',
    body: `Dear {{contact_name}},

This is a friendly reminder that you have an outstanding balance of {{total_due}} with invoices that are past due.

We would appreciate your prompt attention to this matter. If you have already sent payment, please disregard this notice.

If you have any questions or need to discuss payment arrangements, please don't hesitate to contact us.

Best regards,
{{company_name}}
Accounts Receivable`,
  },
  {
    id: 'reminder_firm',
    name: 'Firm Reminder',
    subject: 'Important: Past Due Balance Requires Immediate Attention',
    body: `Dear {{contact_name}},

Our records indicate that your account has a past due balance of {{total_due}}. Some invoices are significantly overdue.

Please arrange payment immediately to avoid any impact to your credit terms with us.

If you are experiencing difficulties, please contact us immediately to discuss payment arrangements.

Regards,
{{company_name}}
Accounts Receivable`,
  },
  {
    id: 'statement',
    name: 'Account Statement',
    subject: 'Your Account Statement from {{company_name}}',
    body: `Dear {{contact_name}},

Please find attached your account statement as of {{statement_date}}.

Current Balance: {{total_balance}}
Past Due Amount: {{past_due_amount}}

If you have any questions about your statement, please contact us.

Thank you for your business.

Best regards,
{{company_name}}
Accounts Receivable`,
  },
];

export const SendEmailModal: React.FC<SendEmailModalProps> = ({
  isOpen,
  onClose,
  customerId,
  customerName,
  customerEmail,
  emailType = 'custom',
  invoiceIds = [],
  onEmailSent,
}) => {
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [formData, setFormData] = useState({
    to: customerEmail || '',
    cc: '',
    subject: '',
    body: '',
    attachStatement: false,
    attachInvoices: false,
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showPreview, setShowPreview] = useState(false);

  // Apply template when selected
  useEffect(() => {
    if (selectedTemplate) {
      const template = defaultTemplates.find((t) => t.id === selectedTemplate);
      if (template) {
        setFormData((prev) => ({
          ...prev,
          subject: template.subject,
          body: template.body,
        }));
      }
    }
  }, [selectedTemplate]);

  // Set default template based on email type
  useEffect(() => {
    if (emailType === 'reminder') {
      setSelectedTemplate('reminder_gentle');
    } else if (emailType === 'statement') {
      setSelectedTemplate('statement');
      setFormData((prev) => ({ ...prev, attachStatement: true }));
    }
  }, [emailType]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      const payload = {
        customer_id: customerId,
        to_email: formData.to,
        cc_email: formData.cc || null,
        subject: formData.subject,
        body: formData.body,
        template_id: selectedTemplate || null,
        attach_statement: formData.attachStatement,
        attach_invoice_ids: formData.attachInvoices ? invoiceIds : [],
      };

      const response = await fetch('/api/email/send', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        throw new Error('Failed to send email');
      }

      onEmailSent?.();
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const processedBody = formData.body
    .replace(/\{\{contact_name\}\}/g, customerName.split(' ')[0] || 'Customer')
    .replace(/\{\{company_name\}\}/g, 'Building Supplies Co.')
    .replace(/\{\{total_due\}\}/g, '$X,XXX.XX')
    .replace(/\{\{total_balance\}\}/g, '$X,XXX.XX')
    .replace(/\{\{past_due_amount\}\}/g, '$X,XXX.XX')
    .replace(/\{\{statement_date\}\}/g, new Date().toLocaleDateString());

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Send Email" size="xl">
      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Header */}
        <div className="flex items-center justify-between border-b pb-3">
          <div className="flex items-center gap-2">
            <Mail className="h-5 w-5 text-blue-600" />
            <div>
              <h3 className="text-lg font-semibold">Send Email</h3>
              <p className="text-sm text-gray-500">To: {customerName}</p>
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

        {/* Template Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Email Template
          </label>
          <select
            value={selectedTemplate}
            onChange={(e) => setSelectedTemplate(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
          >
            <option value="">-- Custom Email --</option>
            {defaultTemplates.map((template) => (
              <option key={template.id} value={template.id}>
                {template.name}
              </option>
            ))}
          </select>
        </div>

        {/* Recipients */}
        <div className="grid grid-cols-2 gap-4">
          <Input
            label="To"
            type="email"
            value={formData.to}
            onChange={(e) => setFormData({ ...formData, to: e.target.value })}
            placeholder="customer@example.com"
            required
          />
          <Input
            label="CC (optional)"
            type="email"
            value={formData.cc}
            onChange={(e) => setFormData({ ...formData, cc: e.target.value })}
            placeholder="cc@example.com"
          />
        </div>

        {/* Subject */}
        <Input
          label="Subject"
          value={formData.subject}
          onChange={(e) => setFormData({ ...formData, subject: e.target.value })}
          placeholder="Email subject"
          required
        />

        {/* Body */}
        <div>
          <div className="flex justify-between items-center mb-1">
            <label className="block text-sm font-medium text-gray-700">
              Message
            </label>
            <button
              type="button"
              onClick={() => setShowPreview(!showPreview)}
              className="text-sm text-blue-600 hover:text-blue-700 flex items-center gap-1"
            >
              <Eye className="h-4 w-4" />
              {showPreview ? 'Edit' : 'Preview'}
            </button>
          </div>
          {showPreview ? (
            <div className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 min-h-[200px] whitespace-pre-wrap">
              {processedBody}
            </div>
          ) : (
            <textarea
              value={formData.body}
              onChange={(e) => setFormData({ ...formData, body: e.target.value })}
              rows={8}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="Enter your message..."
              required
            />
          )}
          <p className="text-xs text-gray-500 mt-1">
            Variables: {'{{contact_name}}'}, {'{{company_name}}'}, {'{{total_due}}'}, {'{{total_balance}}'}
          </p>
        </div>

        {/* Attachments */}
        <div className="bg-gray-50 rounded-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Paperclip className="h-4 w-4 text-gray-500" />
            <span className="text-sm font-medium text-gray-700">Attachments</span>
          </div>
          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={formData.attachStatement}
                onChange={(e) =>
                  setFormData({ ...formData, attachStatement: e.target.checked })
                }
                className="h-4 w-4 text-blue-600 border-gray-300 rounded"
              />
              <span className="text-sm text-gray-700">Attach Account Statement (PDF)</span>
            </label>
            {invoiceIds.length > 0 && (
              <label className="flex items-center gap-2">
                <input
                  type="checkbox"
                  checked={formData.attachInvoices}
                  onChange={(e) =>
                    setFormData({ ...formData, attachInvoices: e.target.checked })
                  }
                  className="h-4 w-4 text-blue-600 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">
                  Attach Selected Invoices ({invoiceIds.length})
                </span>
              </label>
            )}
          </div>
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
          <Button
            type="submit"
            disabled={loading || !formData.to || !formData.subject || !formData.body}
          >
            {loading ? 'Sending...' : 'Send Email'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default SendEmailModal;
