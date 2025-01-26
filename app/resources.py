'''
CRUD API Endpoints
'''

from flask_restful import Resource, Api, reqparse
from app.models import Vendor, db

# Initialize the API object here
api = Api()

# Request parser for creating/updating vendors
vendor_parser = reqparse.RequestParser()
vendor_parser.add_argument("name", type=str, required=True, help="Name of the vendor is required")
vendor_parser.add_argument("service_type", type=str, required=True, help="Type of service is required")
vendor_parser.add_argument("price_range", type=str, required=False)

class VendorResource(Resource):
    def get(self, vendor_id):
        vendor = Vendor.query.get(vendor_id)
        if not vendor:
            return {"message": "Vendor not found"}, 404
        return vendor.to_dict(), 200

    def delete(self, vendor_id):
        vendor = Vendor.query.get(vendor_id)
        if not vendor:
            return {"message": "Vendor not found"}, 404
        db.session.delete(vendor)
        db.session.commit()
        return {"message": "Vendor deleted"}, 200

class VendorListResource(Resource):
    def get(self):
        vendors = Vendor.query.all()
        return [vendor.to_dict() for vendor in vendors], 200

    def post(self):
        args = vendor_parser.parse_args()
        new_vendor = Vendor(
            name=args["name"],
            service_type=args["service_type"],
            price_range=args.get("price_range")
        )
        db.session.add(new_vendor)
        db.session.commit()
        return new_vendor.to_dict(), 201

# Add resources to the API
api.add_resource(VendorResource, "/vendor/<int:vendor_id>")
api.add_resource(VendorListResource, "/vendors")