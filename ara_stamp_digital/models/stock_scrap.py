from odoo import models, fields, api, _
from collections import defaultdict
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from uuid import uuid4
import pytz
from datetime import datetime
from odoo.tools import float_compare, float_is_zero


class StockScrap(models.Model):
    _inherit = "stock.scrap"

    reedem_id = fields.Many2one(
        'reedem.stamp',
        string='Reedem',
    )

    def action_validate(self):
        self.ensure_one()
        if float_is_zero(self.scrap_qty, precision_rounding=self.product_uom_id.rounding):
            raise UserError(_('You can only enter positive quantities.'))

        # Jika skip_scrap_wizard = True → langsung do_scrap()
        if self.env.context.get('skip_scrap_wizard', False):
            return self.do_scrap()

        # Default Odoo behavior
        if self.check_available_qty():
            return self.do_scrap()
        else:
            ctx = dict(self.env.context)
            ctx.update({
                'default_product_id': self.product_id.id,
                'default_location_id': self.location_id.id,
                'default_scrap_id': self.id,
                'default_quantity': self.product_uom_id._compute_quantity(self.scrap_qty, self.product_id.uom_id),
                'default_product_uom_name': self.product_id.uom_name
            })
            return {
                'name': _('%(product)s: Insufficient Quantity To Scrap', product=self.product_id.display_name),
                'view_mode': 'form',
                'res_model': 'stock.warn.insufficient.qty.scrap',
                'view_id': self.env.ref('stock.stock_warn_insufficient_qty_scrap_form_view').id,
                'type': 'ir.actions.act_window',
                'context': ctx,
                'target': 'new'
            }

