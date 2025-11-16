from odoo import http, fields
from odoo.http import request
import base64


class RedeemStampWebsite(http.Controller):

    # 1. List My Redeems
    @http.route('/my/redeems', type='http', auth="user", website=True)
    def website_my_redeems(self, **kw):
        partner = request.env.user.partner_id
        redeems = request.env['reedem.stamp'].sudo().search(
            [('partner_id', '=', partner.id)], order='create_date desc'
        )
        return request.render('ara_stamp_digital.website_my_redeems', {
            'redeems': redeems
        })

    # 2. Select Card
    @http.route('/my/redeems/select_card', type='http', auth="user", website=True)
    def website_select_loyalty_card(self, **kw):
        partner = request.env.user.partner_id
        cards = request.env['loyalty.card'].sudo().search([
            ('partner_id', '=', partner.id),
            ('program_id.active', '=', True),
            ('program_id.is_stamp', '=', True),
            '|',
            ('expiration_date', '>=', fields.Date.today()),
            ('expiration_date', '=', False),
        ])
        return request.render('ara_stamp_digital.website_select_card', {
            'cards': cards
        })

    # 3. Product List dari Card (baru ditambahkan)
    @http.route('/my/redeems_stamp/products/<int:card_id>', type='http', auth="user", website=True)
    def website_redeem_products(self, card_id, **kw):
        partner = request.env.user.partner_id
        card = request.env['loyalty.card'].sudo().browse(card_id)
        products = []
        if card.exists() and card.partner_id == partner:
            rewards = request.env['stamp.reward'].sudo().search([
                ('program_id', '=', card.program_id.id)
            ])
            products = [
                {
                    'id': r.product_id.id,
                    'name': r.product_id.display_name,
                    'point': r.point_rules,
                    'card_id': card.id,
                    'image': f"data:image/png;base64,{r.product_id.image_1920.decode()}" if r.product_id.image_1920 else '/ara_nk_mitra_point/static/no_image.png',

                }
                for r in rewards if r.product_id
            ]
        return request.render('ara_stamp_digital.website_redeem_stamp_products', {
            'card': card,
            'products': products,
        })

    # 4. Form New Redeem (prefill dari product)
    @http.route('/my/redeems_stamp/new', type='http', auth="user", website=True)
    def website_new_redeem(self, card_id=None, product_id=None, **kw):
        partner = request.env.user.partner_id
        card = None
        products = []
        selected_product = None

        if card_id:
            card = request.env['loyalty.card'].sudo().browse(int(card_id))
            if card.exists() and card.partner_id == partner:
                rewards = request.env['stamp.reward'].sudo().search([
                    ('program_id', '=', card.program_id.id)
                ])
                products = [
                    {
                        'id': r.product_id.id,
                        'name': r.product_id.display_name,
                        'point': r.point_rules,
                    }
                    for r in rewards if r.product_id
                ]

        if product_id:
            selected_product = request.env['product.product'].sudo().browse(
                int(product_id))

        return request.render('ara_stamp_digital.website_new_redeem', {
            'card': card,
            'products': products,
            'selected_product': selected_product,
        })

    # 5. Form Submit
    @http.route('/my/redeems_stamp/create', type='http', auth="user", website=True, methods=['POST'])
    def website_create_redeem(self, **post):
        partner = request.env.user.partner_id
        program_id = int(post.get('program_id', 0))
        product_id = int(post.get('product_id', 0))
        delivery_method = post.get('delivery_method')

        if not program_id or not product_id:
            return request.redirect('/my/redeems/select_card')

        # ambil kartu stamp user
        card = request.env['loyalty.card'].sudo().search([
            ('partner_id', '=', partner.id),
            ('program_id', '=', program_id),
        ], limit=1)

        # ambil reward produk
        reward = request.env['stamp.reward'].sudo().search([
            ('program_id', '=', program_id),
            ('product_id', '=', product_id),
        ], limit=1)

        # validasi point
        if not card or not reward:
            return request.redirect('/my/redeems/select_card')

        if card.points < reward.point_rules:
            request.session['redeem_error'] = (
                f"You need at least {reward.point_rules} stamp, "
                f"but you only have {card.points}."
            )
            return request.redirect(f"/my/redeems_stamp/new?card_id={card.id}&product_id={product_id}")

        # kalau lolos validasi, create
        vals = {
            'partner_id': partner.id,
            'program_id': program_id,
            'product_id': product_id,
            'delivery_method': delivery_method,
            'state': 'draft',
        }
        request.env['reedem.stamp'].sudo().create(vals)
        return request.redirect('/my/redeems')
