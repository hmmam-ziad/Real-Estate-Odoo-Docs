{
    'name': 'Real Estate',
    'version': '1.0',
    'category': 'Real Estate/Brokerage',
    'summary': 'Module for managing real estate properties',
    'depends': [
        'base',
        'account',
        'mail',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_property_tag_views.xml',
        'views/res_partner_views.xml',
    ],
    "assets": {
        "web.assets_backend": [
            "estate/static/src/components/estate_calculator/estate_calculator.js",
            "estate/static/src/components/estate_calculator/estate_calculator.xml",
        ],
    },
    'installable': True,
    'application': True,
}