from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_amount


class LoyaltyHistory(models.Model):
    _inherit = "loyalty.history"

    program_id = fields.Many2one(
        'loyalty.program',
        string='Program',
        related='card_id.program_id'
    )

    # @api.model
    # def create(self, vals):
    #     program = None
    #     if 'program_id' in vals:
    #         program = self.env['loyalty.program'].browse(vals['program_id'])
    #     elif 'card_id' in vals:
    #         card = self.env['loyalty.card'].browse(vals['card_id'])
    #         program = card.program_id

    #     # Jika program is_stamp True, lakukan pengecekan max_stamp
    #     if program and program.is_stamp:
    #         # Hitung total issued saat ini untuk card ini
    #         card_id = vals.get('card_id')
    #         current_total = self.env['loyalty.history'].search([('card_id', '=', card_id)]).mapped('issued')
    #         max_stamp = program.max_stamp
    #         incoming = vals.get('issued', 0.0)

    #         allowed = max_stamp - sum(current_total)
    #         if allowed <= 0:
    #             # Sudah penuh, tidak bisa buat
    #             return self.env['loyalty.history']
    #         elif incoming > allowed:
    #             # Partial, buat hanya sebanyak allowed
    #             vals['issued'] = allowed

    #     return super().create(vals)


