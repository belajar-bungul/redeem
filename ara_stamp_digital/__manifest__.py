# encoding: utf-8
{
    "name": "Redeem Stamp",
    "version": "18.0.0.0.0",
    "license": "OPL-1",
    "summary": "Website Customization",
    "category": "Website",
    "author": "ARA SOFT",
    "website": "",
    "description": """
        Website Customization
    """,
    "depends": ["point_of_sale", "sale_loyalty", "pos_loyalty", "base", "website_sale", 'loyalty', 'sale', 'stock'],
    "images": [],
    "init_xml": [],
    "data": [
        "security/ir.model.access.csv",
        "views/loyalty_program_views.xml",
        "views/portal_menu.xml",
        "views/portal_my_redeems.xml",
        "views/portal_new_redeem.xml",
        "views/reedem_stamp_views.xml",
        "views/stock_location_views.xml",
        "views/portal_card.xml",
        "views/portal_product_stamp.xml",
    ],
    "price" : 96.22,
    "currency" : "USD",
    "installable": True,
    "images": ["static/description/banner.gif"],

}
