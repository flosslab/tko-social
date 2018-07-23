from odoo import models, fields, api


class Message(models.Model):
    _inherit = "mail.message"

    email_cc_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="mail_notification_cc",
        column1="message_id",
        column2="partner_id",
        string="CC",
        help="Partners that have a notification pushing this message in their mailboxes"
    )

    email_bcc_ids = fields.Many2many(
        comodel_name="res.partner",
        relation="mail_notification_bcc",
        column1="message_id",
        column2="partner_id",
        string="BCC",
        help="Partners that have a notification pushing this message in their mailboxes"
    )

    @api.multi
    def _notify(self, force_send=False, send_after_commit=True, user_signature=True):
        """ Add the related record followers to the destination partner_ids if is not a private message.
            Call mail_notification.notify to manage the email sending
        """
        group_user = self.env.ref("base.group_user")
        # have a sudoed copy to manipulate partners (public can go here with
        # website modules like forum / blog / ...
        self_sudo = self.sudo()

        # TDE CHECK: add partners / channels as arguments to be able to notify a message with / without computation ??
        self.ensure_one()  # tde: not sure, just for testinh, will see
        partners = self.env["res.partner"] | self.partner_ids
        channels = self.env["mail.channel"] | self.channel_ids

        # all followers of the mail.message document have to be added as partners and notified
        # and filter to employees only if the subtype is internal
        if self_sudo.subtype_id and self.model and self.res_id:
            followers = self.env["mail.followers"].sudo().search([
                ("res_model", "=", self.model),
                ("res_id", "=", self.res_id)
            ]).filtered(lambda fol: self.subtype_id in fol.subtype_ids)
            if self_sudo.subtype_id.internal:
                followers = followers.filtered(lambda fol: fol.channel_id or (
                        fol.partner_id.user_ids and group_user in fol.partner_id.user_ids[0].mapped("groups_id")))
            channels = self_sudo.channel_ids | followers.mapped("channel_id")
            partners = self_sudo.partner_ids | followers.mapped("partner_id")
        else:
            channels = self_sudo.channel_ids
            partners = self_sudo.partner_ids

        # if self.email_cc_ids:
        #     partners |= self.email_cc_ids
        # if self.email_bcc_ids:
        #     partners |= self.email_bcc_ids

        # remove author from notified partners
        if not self._context.get("mail_notify_author", False) and self_sudo.author_id:
            partners = partners - self_sudo.author_id

        # update message, with maybe custom values
        message_values = {
            "channel_ids": [(6, 0, channels.ids)],
            "needaction_partner_ids": [(6, 0, partners.ids)]
        }
        if self.model and self.res_id and hasattr(self.env[self.model], "message_get_message_notify_values"):
            message_values.update(
                self.env[self.model].browse(self.res_id).message_get_message_notify_values(self, message_values))
        self.write(message_values)
        # notify partners and channels
        partners._notify(self, force_send=force_send, send_after_commit=send_after_commit,
                         user_signature=user_signature)
        channels._notify(self)

        # Discard cache, because child / parent allow reading and therefore
        # change access rights.
        if self.parent_id:
            self.parent_id.invalidate_cache()

        return True
