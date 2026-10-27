"""JSON routes under /api. Thin: parse input, call a service, shape the output."""

from flask import current_app, jsonify, request

from app.errors import DomainError
from app.services.catalog_service import CatalogService
from app.services.report_service import ReportService, parse_date
from app.services.search_service import SearchService
from app.services.stock_service import StockService


def _db():
    return current_app.config["DB"]


def _body():
    return request.get_json(silent=True) or {}


def _error(exc):
    if hasattr(exc, "to_dict"):
        return jsonify(exc.to_dict()), exc.status_code
    return jsonify({"message": str(exc)}), exc.status_code


def register_routes(app):
    @app.errorhandler(DomainError)
    def handle_domain_error(exc):
        return _error(exc)

    @app.route("/api/health")
    def health():
        return jsonify({"status": "ok"})

    # Categories and locations ----------------------------------------------

    @app.get("/api/categories")
    def list_categories():
        return jsonify(CatalogService(_db()).list_categories())

    @app.post("/api/categories")
    def create_category():
        cat = CatalogService(_db()).create_category(_body().get("name"))
        return jsonify(cat), 201

    @app.get("/api/locations")
    def list_locations():
        return jsonify(CatalogService(_db()).list_locations())

    @app.post("/api/locations")
    def create_location():
        loc = CatalogService(_db()).create_location(_body().get("name"))
        return jsonify(loc), 201

    # Items -----------------------------------------------------------------

    @app.get("/api/items")
    def list_items():
        return jsonify(CatalogService(_db()).list_items())

    @app.post("/api/items")
    def create_item():
        b = _body()
        item = CatalogService(_db()).create_item(
            sku=b.get("sku"),
            name=b.get("name"),
            category_id=b.get("category_id"),
            unit_cost_cents=b.get("unit_cost_cents"),
            reorder_level=b.get("reorder_level"),
        )
        return jsonify(item), 201

    @app.get("/api/items/<int:item_id>")
    def get_item(item_id):
        db = _db()
        item = CatalogService(db).get_item(item_id)
        item["levels"] = StockService(db).levels_for_item(item_id)
        item["total"] = sum(l["quantity"] or 0 for l in item["levels"])
        return jsonify(item)

    @app.post("/api/items/<int:item_id>/deactivate")
    def deactivate_item(item_id):
        return jsonify(CatalogService(_db()).deactivate_item(item_id))

    # Stock -----------------------------------------------------------------

    @app.post("/api/stock/receive")
    def receive():
        b = _body()
        qty = StockService(_db()).receive_stock(
            b.get("item_id"), b.get("location_id"), b.get("quantity"), b.get("reason"))
        return jsonify({"quantity": qty}), 201

    @app.post("/api/stock/issue")
    def issue():
        b = _body()
        qty = StockService(_db()).issue_stock(
            b.get("item_id"), b.get("location_id"), b.get("quantity"),
            b.get("reason"), confirm=bool(b.get("confirm")))
        return jsonify({"quantity": qty}), 201

    @app.post("/api/stock/adjust")
    def adjust():
        b = _body()
        qty = StockService(_db()).adjust_stock(
            b.get("item_id"), b.get("location_id"), b.get("delta"), b.get("reason"))
        return jsonify({"quantity": qty}), 201

    @app.get("/api/movements")
    def movements():
        item_id = request.args.get("item_id", type=int)
        return jsonify(StockService(_db()).history(item_id=item_id))

    # Reports and dashboard ---------------------------------------------------

    @app.get("/api/reports/valuation")
    def report_valuation():
        return jsonify(ReportService(_db()).valuation(
            location_id=request.args.get("location_id", type=int)))

    @app.get("/api/reports/low-stock")
    def report_low_stock():
        return jsonify(ReportService(_db()).low_stock())

    @app.get("/api/reports/negative-stock")
    def report_negative_stock():
        return jsonify(ReportService(_db()).negative_stock())

    @app.get("/api/reports/movements")
    def report_movements():
        a = request.args
        return jsonify(ReportService(_db()).movement_history(
            item_id=a.get("item_id", type=int), start=a.get("start"),
            end=a.get("end"), location_id=a.get("location_id", type=int)))

    @app.get("/api/reports/turnover")
    def report_turnover():
        a = request.args
        return jsonify(ReportService(_db()).turnover(
            start=a.get("start"), end=a.get("end"),
            location_id=a.get("location_id", type=int)))

    @app.get("/api/search")
    def search():
        a = request.args
        return jsonify(SearchService(_db()).search(
            q=a.get("q"),
            category_id=a.get("category_id", type=int),
            location_id=a.get("location_id", type=int),
            status=a.get("status"),
        ))

    @app.get("/api/dashboard")
    def dashboard():
        a = request.args
        as_of = a.get("as_of")
        as_of_day = parse_date(as_of, "as_of") if as_of else None
        return jsonify(ReportService(_db()).dashboard(
            as_of=as_of_day, days=a.get("days", default=30, type=int)))
