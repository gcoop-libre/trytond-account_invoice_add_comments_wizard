# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import ModelView, fields
from trytond.pool import Pool
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.wizard import Wizard, StateView, StateTransition, Button

__all__ = ['AddComments', 'AddCommentsWizard']


class AddComments(ModelView):
    'Add Comments'
    __name__ = 'invoice.add_comments'
    selected_invoices = fields.Integer('Selected Invoices', readonly=True)
    ignored_invoices = fields.Integer('Ignored Invoices', readonly=True, states={
            'invisible': Eval('ignored_invoices', 0) == 0,
            },
        help="The invoices that won't be changed because they are not in a state "
        "that allows it.")
    categories = fields.Many2Many('product.category', None, None, 'Categories',
        states={
            'readonly': Eval('selected_invoices', 0) == 0,
            }, depends=['selected_invoices'])
    comment = fields.Text('Comment',
        states={
            'readonly': Eval('selected_invoices', 0) == 0,
            }, depends=['selected_invoices'])


class AddCommentsWizard(Wizard):
    'Add Comments to Invoice'
    __name__ = 'invoice.add_comments.wizard'
    start_state = 'add_comments'
    add_comments = StateView('invoice.add_comments',
        'account_invoice_add_comments_wizard.add_comments_view_form', [
            Button('Cancel', 'end', 'tryton-cancel'),
            Button('Add', 'save_comments', 'tryton-ok', default=True),
            ])
    save_comments = StateTransition()

    @classmethod
    def __setup__(cls):
        super(AddCommentsWizard, cls).__setup__()
        cls._allowed_invoice_states = {'draft'}

    def default_add_comments(self, fields):
        Invoice = Pool().get('account.invoice')

        active_ids = Transaction().context['active_ids']
        selected_invoices = Invoice.search([
                ('id', 'in', active_ids),
                ('state', 'in', self._allowed_invoice_states),
                ], count=True)
        return {
            'selected_invoices': selected_invoices,
            'ignored_invoices': len(active_ids) - selected_invoices,
            }

    def transition_save_comments(self):
        Invoice = Pool().get('account.invoice')
        categories = self.add_comments.categories
        comment = self.add_comments.comment

        if not categories:
            return 'end'

        if not comment:
            return 'end'

        invoices = Invoice.search([
                ('id', 'in', Transaction().context['active_ids']),
                ('state', 'in', self._allowed_invoice_states),
                ])
        if not invoices:
            return 'end'

        to_save = []
        for invoice in invoices:
            for line in invoice.lines:
                if line.product and line.product.category in categories:
                    invoice.comment = comment
                    invoice.description = comment
                    to_save.append(invoice)
                    break
        if to_save:
            Invoice.save(to_save)
        return 'end'
