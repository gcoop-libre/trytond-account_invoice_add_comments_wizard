# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.pool import Pool
from . import invoice


def register():
    Pool.register(
        invoice.AddComments,
        module='account_invoice_add_comments_wizard', type_='model')
    Pool.register(
        invoice.AddCommentsWizard,
        module='account_invoice_add_comments_wizard', type_='wizard')
