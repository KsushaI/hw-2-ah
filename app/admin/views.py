from aiohttp.web import json_response
from app.web.app import View
from app.admin.schemas import AdminSchema


class AdminLoginView(View):
    async def post(self):
        data = await self.request.json()
        schema = AdminSchema()
        try:
            validated = schema.load(data)
        except Exception as e:
            return json_response(
                {"status": "bad_request", "message": str(e)},
                status=400
            )

        admin = await self.store.admins.get_by_email(validated["email"])
        if not admin or admin.password != validated["password"]:
            return json_response(
                {"status": "unauthorized", "message": "Invalid credentials"},
                status=401
            )

        return json_response({
            "status": "ok",
            "data": {
                "id": admin.id,
                "email": admin.email
            }
        })


class AdminCurrentView(View):
    async def get(self):
        admin = self.request.admin
        if not admin:
            return json_response(
                {"status": "unauthorized", "message": "Not authenticated"},
                status=401
            )

        return json_response({
            "status": "ok",
            "data": {
                "id": admin.id,
                "email": admin.email
            }
        })