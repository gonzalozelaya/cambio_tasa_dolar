# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.tools import format_date
import datetime
import logging

_logger = logging.getLogger(__name__)
class ResCurrency(models.Model):
    _inherit = "res.currency"

    def l10n_ar_action_get_afip_ws_currency_rate(self):
        date, rate = self._l10n_ar_get_afip_ws_currency_rate()
        formatted_date = format_date(self.env, datetime.datetime.strptime(date, '%Y%m%d'), date_format='EEEE, dd MMMM YYYY')
        
        date_obj = datetime.datetime.strptime(date, '%Y%m%d').date()
        existing_rate = self.env['res.currency.rate'].search([
            ('currency_id', '=', self.id),
            ('name', '=', date_obj)
        ], limit=1)

        if existing_rate:
            existing_rate.write({
                'inverse_company_rate': rate
            })
        else:
            self.write({
                'rate_ids': [(0, 0, {
                    'name': date_obj,
                    'inverse_company_rate': rate,
                    'currency_id': self.id,
                    'company_id': self.env.company.id,
                })]
            })

    def _cron_update_currency_rates(self):
        """ Método llamado por el cron job para actualizar tasas de cambio """
        currencies = self.search([('active', '=', True),('l10n_ar_afip_code','=','DOL')])
        for currency in currencies:
            try:
                currency.l10n_ar_action_get_afip_ws_currency_rate()
            except Exception as e:
                _logger.error("Error updating currency rate for %s: %s", currency.name, str(e))

    @api.model
    def _setup_cron_job(self):
        """ Configura el cron job si no existe """
        cron = self.env.ref('account_calc_rate_from_invoice.cron_update_currency_rates', raise_if_not_found=False)
        if not cron:
            self.env['ir.cron'].create({
                'name': 'Actualizar tasas de cambio AFIP automáticamente',
                'model_id': self.env.ref('base.model_res_currency').id,
                'state': 'code',
                'code': 'model._cron_update_currency_rates()',
                'interval_number': 1,
                'interval_type': 'days',
                'numbercall': -1,
                'doall': False,
                'active': True,
                'nextcall': fields.Datetime.now().replace(hour=8, minute=0, second=0),  # Ejecutar a las 8 AM
                'user_id': self.env.ref('base.user_admin').id,
            })