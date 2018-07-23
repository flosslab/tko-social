import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class MailComposer(models.TransientModel):
    _inherit = "mail.compose.message"

    email_cc_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="mail_compose_message_res_partner_cc_rel",
        column1="wizard_id",
        column2="partner_cc_id",
        string="Email CC",
        default=lambda self: self.default_email_cc_ids()
    )

    email_bcc_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="mail_compose_message_res_partner_bcc_rel",
        column1="wizard_id",
        column2="partner_bcc_id",
        string="Email BCC",
        default=lambda self: self.default_email_bcc_ids()
    )

    is_cc = fields.Boolean(
        default=lambda self: self.default_is_cc()
    )

    is_bcc = fields.Boolean(
        default=lambda self: self.default_is_bcc()
    )

    def default_email_cc_ids(self):
        if self.env.user.company_id.default_cc:
            return self.env.user.company_id.default_cc.ids

    def default_email_bcc_ids(self):
        if self.env.user.company_id.default_bcc:
            return self.env.user.company_id.default_bcc.ids

    def default_is_cc(self):
        if self.env.user.company_id.is_cc_visible:
            return True

    def default_is_bcc(self):
        if self.env.user.company_id.is_bcc_visible:
            return True

    @api.multi
    def get_mail_values(self, res_ids):
        res = super().get_mail_values(res_ids)

        for key, value in res.items():
            if self.email_bcc_ids:
                # value["email_bcc"] = wizard.email_bcc_ids[0].email
                value["email_bcc_ids"] = [(4, partner_bcc.id) for partner_bcc in self.email_bcc_ids]
            if self.email_cc_ids:
                # value["email_cc"] = wizard.email_cc_ids[0].email
                value["email_cc_ids"] = [(4, partner_cc.id) for partner_cc in self.email_cc_ids]

        return res
