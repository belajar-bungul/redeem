from odoo import models, fields, api, _
from collections import defaultdict
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError
from uuid import uuid4
import pytz
from datetime import datetime


class StockLocation(models.Model):
    _inherit = "stock.location"

    is_stamp = fields.Boolean(
        string="Redeem",
    )