from objects.inanimate.order_buy import BuyOrder
from objects.inanimate.order_sell import SellOrder
from objects.animate.investment_bank import InvestmentBank
from objects.animate.company import Company
from objects.animate.market import Market
from objects.animate.value_investor import ValueInvestor
from objects.inanimate.share import Share

col2class = {
    "companies": Company,
    "markets": Market,
    "shares": Share,
    "investors": ValueInvestor,
    "investment_banks": InvestmentBank,
    "orders_buy": BuyOrder,
    "orders_sell": SellOrder,
}
