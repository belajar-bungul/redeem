from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.tools import format_amount

class ReedemStamp(models.Model):
    _name = 'reedem.stamp'

    partner_id = fields.Many2one(
        'res.partner',
        string='Customer',
        )
    program_id = fields.Many2one(
        'loyalty.program',
        string='Program',
        )
    stamp_point_saldo = fields.Float(
        string="Stamp Point Saldo",
        compute='_compute_stamp_point_saldo',
        store=True
    )

    @api.onchange('program_id', 'partner_id')
    def onchange_stamp_point_saldo(self):
        for record in self:
            saldo = self.sudo().env['loyalty.card'].search([('program_id','=', record.program_id.id),
                                                            ('partner_id', '=', record.partner_id.id)],
                                                            limit=1
                                                            )
            if saldo:
                record.stamp_point_saldo = saldo.points
            else:
                record.stamp_point_saldo = 0.0
    

    @api.depends('program_id', 'partner_id')
    def _compute_stamp_point_saldo(self):
        for record in self:
            saldo = self.sudo().env['loyalty.card'].search([('program_id','=', record.program_id.id),
                                                            ('partner_id', '=', record.partner_id.id)],
                                                            limit=1
                                                            )
            if saldo:
                record.stamp_point_saldo = saldo.points
            else:
                record.stamp_point_saldo = 0.0

    # helper field untuk domain
    stamp_reward_product_ids = fields.Many2many(
        'product.product',
        compute='_compute_stamp_reward_products',
        store=False,
    )

    @api.depends('program_id')
    def _compute_stamp_reward_products(self):
        for rec in self:
            if rec.program_id:
                rewards = self.env['stamp.reward'].search([('program_id', '=', rec.program_id.id)])
                rec.stamp_reward_product_ids = rewards.mapped('product_id')
            else:
                rec.stamp_reward_product_ids = False

    product_id = fields.Many2one(
        'product.product',
        string='Product',
        domain="[('id', 'in', stamp_reward_product_ids)]",  # domain pakai helper field
    )

    stamp_point_rules = fields.Float(
        string="Stamp Point Rules",
        compute='_compute_stamp_point_rules'
    )
    delivery_method = fields.Selection([('pickup', 'Pickup'),
                                        ('delivery','Delivery')])
    state = fields.Selection([('draft', 'Draft'),
                              ('done','Done')], default="draft",)

    @api.depends('program_id','product_id')
    def _compute_stamp_point_rules(self):
        for rec in self:
            if rec.program_id and rec.product_id:
                rewards = self.env['stamp.reward'].search([('program_id', '=', rec.program_id.id),
                                                           ('product_id', '=', rec.product_id.id)])
                rec.stamp_point_rules = rewards.point_rules
            else:
                rec.stamp_point_rules = 0.0

    def minus_point(self):
        for record in self:
            card = self.sudo().env['loyalty.card'].search([
                ('program_id', '=', record.program_id.id),
                ('partner_id', '=', record.partner_id.id),
            ], limit=1)

            if not card:
                raise UserError(_("No loyalty card found for this customer and program."))

            # total stamp yang dibutuhkan untuk redeem product ini
            required_points = record.stamp_point_rules

            # ambil semua issued history untuk kartu ini
            histories = self.env['loyalty.history'].sudo().search([
                ('card_id', '=', card.id),
            ], order="create_date asc, id asc")

            remaining = required_points

            for line in histories:
                issued = line.issued or 0.0   # issued = jumlah yang diberikan
                used = line.used or 0.0       # used = jumlah yang sudah dipakai
                available = issued - used     # sisa yang bisa dipakai

                if available <= 0:
                    continue

                if remaining <= available:
                    line.write({'used': used + remaining})
                    remaining = 0
                    break
                else:
                    line.write({'used': issued})  # habiskan line ini
                    remaining -= available

            # kalau masih ada sisa yang belum bisa dipenuhi
            if remaining > 0:
                raise ValidationError(_("Not enough stamp points to redeem."))

            # terakhir update saldo total di card
            card.points -= required_points


    def process_line(self):
        location_source = self.env['stock.location'].search([('is_stamp', '=', True)], limit=1)
        self.minus_point()
        for rec in self:
            scrap = self.sudo().env['stock.scrap'].create({
                'product_id': rec.product_id.id,
                'reedem_id': rec.id,
                'location_id': location_source.id
            })
            rec.state = 'done'
            scrap.with_context(skip_scrap_wizard=True).action_validate()


    def view_scrap(self):
        return {
            'name': _('Scrap Transfer'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'list,form',
            'res_model': 'stock.scrap',
            'domain': [('reedem_id', '=',  self.id)],
        }
        
        
        