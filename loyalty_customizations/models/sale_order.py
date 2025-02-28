from odoo import models, fields, api
import logging
from collections import defaultdict
from odoo.tools.float_utils import float_round
from odoo.tools.translate import _
_logger = logging.getLogger(__name__)

from collections import defaultdict

import itertools

import random

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Command
from odoo.tools.float_utils import float_is_zero, float_round
from odoo.osv import expression

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    quantity_to_add_points = fields.Float(string="Cantidad para añadir a puntos", compute="_compute_quantity_to_add_points", store=True)

    @api.depends('product_id', 'product_uom_qty', 'qty_delivered')
    def _compute_quantity_to_add_points(self):
        for line in self:
            if not line.qty_delivered:
                line.quantity_to_add_points = line.product_uom_qty
                continue
            if line.product_uom_qty == line.qty_delivered:
                line.quantity_to_add_points = 0
                continue
            if line.product_uom_qty > line.qty_delivered:
                line.quantity_to_add_points = (line.product_uom_qty - line.qty_delivered) * -1
                continue
            line.quantity_to_add_points = 0
        self.order_id._try_apply_program(self.coupon_id.program_id)

        #TODO forget everything, only maintan program_check_compute_points and use _get_applied_programs to get the program in the order and run _program_check_compute_points with that data, obtain the card and discount the amount.



class SaleOrder(models.Model):
    _inherit = "sale.order"

    
    def _program_check_compute_points(self, programs):
        """
        Checks the program validity from the order lines aswell as computing the number of points to add.

        Returns a dict containing the error message or the points that will be given with the keys 'points'.
        """
        self.ensure_one()

        # Prepare quantities
        order_lines = self._get_not_rewarded_order_lines()
        products = order_lines.product_id
        products_qties = dict.fromkeys(products, 0)
        for line in order_lines:
            products_qties[line.product_id] += line.quantity_to_add_points
        # Contains the products that can be applied per rule
        products_per_rule = programs._get_valid_products(products)

        # Prepare amounts
        so_products_per_rule = programs._get_valid_products(self.order_line.product_id)
        lines_per_rule = defaultdict(lambda: self.env['sale.order.line'])
        # Skip lines that have no effect on the minimum amount to reach.
        for line in self.order_line - self._get_no_effect_on_threshold_lines():
            is_discount = line.reward_id.reward_type == 'discount'
            reward_program = line.reward_id.program_id
            # Skip lines for automatic discounts.
            if is_discount and reward_program.trigger == 'auto':
                continue
            for program in programs:
                # Skip lines for the current program's discounts.
                if is_discount and reward_program == program:
                    continue
                for rule in program.rule_ids:
                    # Skip lines to which the rule doesn't apply.
                    if line.product_id in so_products_per_rule.get(rule, []):
                        lines_per_rule[rule] |= line

        result = {}
        for program in programs:
            # Used for error messages
            # By default False, but True if no rules and applies_on current -> misconfigured coupons program
            code_matched = not bool(program.rule_ids) and program.applies_on == 'current' # Stays false if all triggers have code and none have been activated
            minimum_amount_matched = code_matched
            product_qty_matched = code_matched
            points = 0
            # Some rules may split their points per unit / money spent
            #  (i.e. gift cards 2x50$ must result in two 50$ codes)
            rule_points = []
            program_result = result.setdefault(program, dict())
            for rule in program.rule_ids:
                # prevent bottomless ewallet spending
                if program.program_type == 'ewallet' and not program.trigger_product_ids:
                    break
                if rule.mode == 'with_code' and rule not in self.code_enabled_rule_ids:
                    continue
                code_matched = True
                rule_amount = rule._compute_amount(self.currency_id)
                untaxed_amount = sum(lines_per_rule[rule].mapped('price_subtotal'))
                tax_amount = sum(lines_per_rule[rule].mapped('price_tax'))
                if rule_amount > (rule.minimum_amount_tax_mode == 'incl' and (untaxed_amount + tax_amount) or untaxed_amount):
                    continue
                minimum_amount_matched = True
                if not products_per_rule.get(rule):
                    continue
                rule_products = products_per_rule[rule]
                ordered_rule_products_qty = sum(products_qties[product] for product in rule_products)
                ordered_absolute_num = ordered_rule_products_qty if ordered_rule_products_qty > 0 else ordered_rule_products_qty * -1
                if ordered_absolute_num < rule.minimum_qty or not rule_products:
                    continue
                product_qty_matched = True
                if not rule.reward_point_amount:
                    continue
                # Count all points separately if the order is for the future and the split option is enabled
                if program.applies_on == 'future' and rule.reward_point_split and rule.reward_point_mode != 'order':
                    if rule.reward_point_mode == 'unit':
                        rule_points.extend(rule.reward_point_amount for _ in range(int(ordered_rule_products_qty)))
                    elif rule.reward_point_mode == 'money':
                        for line in self.order_line:
                            if line.is_reward_line or line.product_id not in rule_products or line.product_uom_qty <= 0:
                                continue
                            points_per_unit = float_round(
                                (rule.reward_point_amount * line.price_total / line.product_uom_qty),
                                precision_digits=2, rounding_method='DOWN')
                            if not points_per_unit:
                                continue
                            rule_points.extend([points_per_unit] * int(line.product_uom_qty))
                else:
                    # All checks have been passed we can now compute the points to give
                    if rule.reward_point_mode == 'order':
                        points += rule.reward_point_amount
                    elif rule.reward_point_mode == 'money':
                        # Compute amount paid for rule
                        # NOTE: this accounts for discounts -> 1 point per $ * (100$ - 30%) will
                        # result in 70 points
                        amount_paid = 0.0
                        rule_products = so_products_per_rule.get(rule, [])
                        for line in self.order_line - self._get_no_effect_on_threshold_lines():
                            if line.reward_id.program_id.program_type in [
                                'ewallet', 'gift_card', program.program_type
                            ]:
                                continue
                            amount_paid += line.price_total if line.product_id in rule_products else 0.0

                        points += float_round(rule.reward_point_amount * amount_paid, precision_digits=2, rounding_method='DOWN')
                    elif rule.reward_point_mode == 'unit':
                        points += rule.reward_point_amount * ordered_rule_products_qty
            # NOTE: for programs that are nominative we always allow the program to be 'applied' on the order
            #  with 0 points so that `_get_claimable_rewards` returns the rewards associated with those programs
            if not program.is_nominative:
                if not code_matched:
                    program_result['error'] = _("This program requires a code to be applied.")
                elif not minimum_amount_matched:
                    program_result['error'] = _(
                        'A minimum of %(amount)s %(currency)s should be purchased to get the reward',
                        amount=min(program.rule_ids.mapped('minimum_amount')),
                        currency=program.currency_id.name,
                    )
                elif not product_qty_matched:
                    program_result['error'] = _("You don't have the required product quantities on your sales order.")
            elif not self._allow_nominative_programs():
                program_result['error'] = _("This program is not available for public users.")
            if 'error' not in program_result:
                points_result = [points] + rule_points
                _logger.info('points result %s',points_result)
                program_result['points'] = points_result
        _logger.info(result)
        return result
    
    def _get_program_domain(self):
        domain = super(SaleOrder, self)._get_program_domain()
        domain.append(('partner_ids', 'in', self.partner_id.id))
        return domain
    
    def _try_apply_program(self, program, coupon=None):
        _logger.info('running try apply')
        """
        Tries to apply a program using the coupon if provided.

        This function provides the full routine to apply a program, it will check for applicability
        aswell as creating the necessary coupons and co-models to give the points to the customer.

        This function does not apply any reward to the order, rewards have to be given manually.

        Returns a dict containing the error message or containing the associated coupon(s).
        """
        self.ensure_one()
        # Basic checks
        if not program.filtered_domain(self._get_program_domain()):
            return {'error': _('The program is not available for this order.')}
        elif program in self._get_applied_programs():
            return {'error': _('This program is already applied to this order.')}
        # Check for applicability from the program's triggers/rules.
        # This step should also compute the amount of points to give for that program on that order.
        status = self._program_check_compute_points(program)[program]
        _logger.info('status %s',status)
        if 'error' in status:
            return status
        return self.__try_apply_program(program, coupon, status)
    
    

    def __try_apply_program(self, program, coupon, status):
        self.ensure_one()
        _logger.info('running try apply')
        all_points = status['points']
        points = all_points[0]
        _logger.info('points %s',points)
        coupons = coupon or self.env['loyalty.card']
        if coupon:
            if program.is_nominative:
                self._add_points_for_coupon({coupon: points})
        elif not coupon:
            # If the program only applies on the current order it does not make sense to fetch already existing coupons
            if program.is_nominative:
                coupon = self.env['loyalty.card'].search(
                    [('partner_id', '=', self.partner_id.id), ('program_id', '=', program.id)], limit=1)
                # Do not apply 'nominative' programs if no point is given and no coupon exists
                if not points and not coupon:
                    return {'error': _('No card found for this loyalty program and no points will be given with this order.')}
                elif coupon:
                    self._add_points_for_coupon({coupon: points})
                coupons = coupon
            if not coupon:
                all_points = [p for p in all_points if p]
                partner = False
                # Loyalty programs and ewallets are nominative
                if program.is_nominative:
                    partner = self.partner_id.id
                coupons = self.env['loyalty.card'].sudo().with_context(loyalty_no_mail=True, tracking_disable=True).create([{
                    'program_id': program.id,
                    'partner_id': partner,
                    'points': 0,
                    'order_id': self.id,
                } for _ in all_points])
                self._add_points_for_coupon({coupon: x for coupon, x in zip(coupons, all_points)})
        return {'coupon': coupons}