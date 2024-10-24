# -*- coding: utf-8 -*-

from odoo import models
from odoo.tools import format_date
import datetime

class ResCurrency(models.Model):

    _inherit = "res.currency"

    def l10n_ar_action_get_afip_ws_currency_rate(self):
        date, rate = self._l10n_ar_get_afip_ws_currency_rate()
        formatted_date = format_date(self.env, datetime.datetime.strptime(date, '%Y%m%d'), date_format='EEEE, dd MMMM YYYY')
        
        # Convertir la fecha de string a objeto datetime
        date_obj = datetime.datetime.strptime(date, '%Y%m%d').date()
        # Actualizar el campo rate_ids (One2many con res.currency.rate)
        existing_rate = self.env['res.currency.rate'].search([
            ('currency_id', '=', self.id),
            ('name', '=', date_obj)
        ], limit=1)

        if existing_rate:
            # Si ya existe una tasa para esa fecha, la actualizamos
            existing_rate.write({
                'inverse_company_rate': rate
            })
        else:
            # Si no existe, creamos una nueva entrada en rate_ids usando Command
            self.write({
                'rate_ids': [(0, 0, {
                    'name': date_obj,
                    'inverse_company_rate': rate,
                    'currency_id': self.id,
                    'company_id': self.env.company.id,
                })]
            })