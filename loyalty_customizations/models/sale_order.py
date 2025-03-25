from collections import defaultdict
from odoo.tools.translate import _
from odoo import api, fields, models, _
from odoo.tools.float_utils import float_round
from odoo.tools.safe_eval import safe_eval
import logging
_logger = logging.getLogger(__name__)



class SaleOrder(models.Model):
    _inherit = "sale.order"

    points_by_uom_qty = fields.Float(
        string="Points by UoM Qty",
        compute="_compute_points_by_uom_qty",
        store=True,
        copy=False
    )

    points_by_qty_delivered = fields.Float(
        string="Points by Qty Delivered",
        compute="_compute_points_by_qty_delivered",
        store=True,
        copy=False
    )
    is_delivery_compute = fields.Boolean(copy=False)

    previous_points_buffer = fields.Float(string="Previous Points Buffer", copy=False)
        

    @api.depends('state')
    def _compute_points_by_uom_qty(self):
        for order in self:
            points = order._compute_program_points()
            _logger.info("Points in compute by UoM Qty: %s", points)   
            _logger.info("Order name: %s", order.name)
            _logger.info("Order lines: %s", order.order_line.ids)
            order.points_by_uom_qty = points
            if not order.points_by_qty_delivered:
                order._recalculate_card_points() 

    def _recalculate_card_points(self):
        programs = self._get_applied_programs()
        for program in programs:
            if not self.partner_id.filtered_domain(safe_eval(program.partner_domain)):
                continue
            card = program.coupon_ids.filtered(lambda c: c.partner_id == self.partner_id)
            if not self.points_by_qty_delivered:
                card.points += self.points_by_uom_qty
                continue
            _logger.info("Points by UoM Qty: %s", self.points_by_uom_qty)
            _logger.info("Points by Qty Delivered: %s", self.points_by_qty_delivered)
            _logger.info("Previous Points Buffer: %s", self.previous_points_buffer)
            if self.points_by_qty_delivered: # 10
                if not self.previous_points_buffer: # 0
                    card.points += self.points_by_qty_delivered - self.points_by_uom_qty # 10 y 20
                    self.previous_points_buffer = self.points_by_qty_delivered #10
                    _logger.info('first if')
                else:
                    if self.previous_points_buffer > self.points_by_qty_delivered: #10 y 20
                        card.points -= self.previous_points_buffer # - 10
                        card.points +=  self.points_by_qty_delivered # + 20
                        self.previous_points_buffer = self.points_by_qty_delivered # 20
                        _logger.info('second if')

                    elif self.previous_points_buffer < self.points_by_qty_delivered: # 20 y 15
                        card.points -= self.previous_points_buffer # -20
                        card.points += self.points_by_qty_delivered # + 15
                        self.previous_points_buffer = self.points_by_qty_delivered # 15   
                        _logger.info('third if')
                    else:
                        card.points = card.points
                        _logger.info('fourth if')
            _logger.info("Card points: %s", card.points)

    @api.depends('order_line.qty_delivered', 'state')
    def _compute_points_by_qty_delivered(self):
        for order in self:
            _logger.info("Qty delivered Order name: %s", order.name)
            _logger.info("Qty delivered Order lines: %s", order.order_line.ids)
            qty_delivered = sum(order.order_line.mapped('qty_delivered'))
            if qty_delivered > 0:
                order.is_delivery_compute = True
                points = order._compute_program_points()
                _logger.info("Points in compute by Qty Delivered: %s", points)   
                order.points_by_qty_delivered = points
                order._recalculate_card_points()  


    def _compute_program_points(self):
        self.ensure_one()
        programs = self._get_applied_programs()
        for program in programs:
            _logger.info("Program name: %s", program.name)
            if not self.partner_id.filtered_domain(safe_eval(program.partner_domain)):
                continue
            status = self._program_check_compute_points(program)[program]
            all_points = status.get('points', False)
            if all_points:
                points = all_points[0]
                return points
        return 0


    def _program_check_compute_points(self, programs):
        """
        Checks the program validity from the order lines aswell as computing the number of points to add.

        Returns a dict containing the error message or the points that will be given with the keys 'points'.
        """
        self.ensure_one()

        # Prepare quantities
        order_lines = self._get_not_rewarded_order_lines()
        _logger.info("Order lines: %s", order_lines)
        _logger.info("sale order %s", order_lines.order_id.ids)
        products = order_lines.product_id
        products_qties = dict.fromkeys(products, 0)
        delivered_qtys = self.is_delivery_compute
        for line in order_lines:
            if delivered_qtys:
                products_qties[line.product_id] += line.qty_delivered
            else:
                products_qties[line.product_id] += line.product_uom_qty
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
        programs = self.env['loyalty.program'].search([])
        program_ids = []
        for program in programs: 
            if program.partner_domain and self.partner_id.filtered_domain(safe_eval(program.partner_domain)):
                program_ids.append(program.id)
        domain.append(('id', 'in', program_ids))
        domain.append('|')
        domain.append(('partner_ids', 'in', self.partner_id.id))
        domain.append(('partner_ids', '=', False))
        return domain