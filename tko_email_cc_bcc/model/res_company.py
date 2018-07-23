from odoo import models, fields


class ResCompany(models.Model):
    _inherit = "res.company"

    is_cc_visible = fields.Boolean(
        string="CC Visible",
        default=True
    )

    default_cc = fields.Many2many(
        string="Default CC",
        comodel_name="res.partner",
        relation="rel_cc_partner_ids",
        column1="company_id",
        column2="partner_cc_id"
    )

    is_bcc_visible = fields.Boolean(
        string="BCC Visible",
        default=True
    )

    default_bcc = fields.Many2many(
        string="Default BCC",
        comodel_name="res.partner",
        relation="rel_bcc_partner_ids",
        column1="company_id",
        column2="partner_bcc_id"
    )
