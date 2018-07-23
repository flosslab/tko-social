from odoo import models, api


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.model
    def _notify_prepare_email_values(self, message):
        mail_values = super()._notify_prepare_email_values(message)

        cc_email_list = message.email_cc_ids.mapped("email")
        bcc_email_list = message.email_bcc_ids.mapped("email")

        values = {
            "email_cc": ",".join(cc_email_list),
            "email_bcc": ",".join(bcc_email_list)
        }

        mail_values.update(values)

        return mail_values
