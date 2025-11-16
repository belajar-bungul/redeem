from odoo import models, fields, api, _
from collections import defaultdict
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from uuid import uuid4
import pytz
from datetime import datetime


class LoyaltyProgram(models.Model):
    _inherit = "loyalty.program"

    is_stamp = fields.Boolean(
        string="Stamp",
    )
    # max_stamp = fields.Float("Max Stamp")
    stamp_reward_ids = fields.One2many('stamp.reward','program_id')

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for vals in vals_list:
    #         if vals.get('is_stamp') and vals.get('max_stamp', 0.0) == 0.0:
    #             raise ValidationError("Program Stamp tidak boleh 0 max stamp nya!")
    #     return super().create(vals_list)

    # def write(self, vals):
    #     for record in self:
    #         is_stamp = vals.get('is_stamp', record.is_stamp)
    #         max_stamp = vals.get('max_stamp', record.max_stamp)
    #         if is_stamp and max_stamp == 0.0:
    #             raise ValidationError("Program Stamp tidak boleh 0 max stamp nya!")
    #     return super().write(vals)
    
    @api.model
    def _load_pos_data_fields(self, config_id):
        # ambil field bawaan dari superclass
        fields = super()._load_pos_data_fields(config_id)

        # tambahkan field tambahanmu
        extra_fields = [
            'is_stamp',

        ]

        # pastikan tidak dobel
        for f in extra_fields:
            if f not in fields:
                fields.append(f)

        return fields

class StampReward(models.Model):
    _name = 'stamp.reward'

    program_id = fields.Many2one(
        'loyalty.program',
        string='program',
        )
    product_id = fields.Many2one(
        'product.product',
        string='Product',
        )
    point_rules = fields.Float(
        string="Point Rules",
    )