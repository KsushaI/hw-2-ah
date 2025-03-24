from aiohttp_apispec import docs, request_schema, response_schema
from aiohttp.web import json_response
from app.quiz.schemes import (
    ThemeSchema,
    QuestionSchema,
    ThemeListSchema,
    ListQuestionSchema,
    ThemeIdSchema
)
from app.web.app import View
from app.web.utils import json_response
from app.web.middlewares import auth_required


class ThemeAddView(View):
    @docs(tags=["quiz"], summary="Add new theme")
    @request_schema(ThemeSchema)
    @response_schema(ThemeSchema, 200)
    @auth_required
    async def post(self):
        title = self.data["title"]
        existing_theme = await self.store.quizzes.get_theme_by_title(title)
        if existing_theme:
            return json_response(
                data={"error": "Theme already exists"},
                status=409
            )
        theme = await self.store.quizzes.create_theme(title=title)
        return json_response(data=ThemeSchema().dump(theme))


class ThemeListView(View):
    @docs(tags=["quiz"], summary="List all themes")
    @response_schema(ThemeListSchema, 200)
    @auth_required
    async def get(self):
        themes = await self.store.quizzes.list_themes()
        return json_response(
            data={"themes": ThemeSchema().dump(themes, many=True)}
        )


class QuestionAddView(View):
    @docs(tags=["quiz"], summary="Add new question")
    @request_schema(QuestionSchema)
    @response_schema(QuestionSchema, 200)
    @auth_required
    async def post(self):
        data = self.data
        theme = await self.store.quizzes.get_theme_by_id(data["theme_id"])
        if not theme:
            return json_response(
                data={"error": "Theme not found"},
                status=404
            )

        existing_question = await self.store.quizzes.get_question_by_title(data["title"])
        if existing_question:
            return json_response(
                data={"error": "Question already exists"},
                status=409
            )

        correct_answers = sum(1 for a in data["answers"] if a["is_correct"])
        if correct_answers != 1:
            return json_response(
                data={"error": "Must have exactly one correct answer"},
                status=400
            )

        if len(data["answers"]) < 2:
            return json_response(
                data={"error": "Must have at least 2 answers"},
                status=400
            )

        question = await self.store.quizzes.create_question(
            title=data["title"],
            theme_id=data["theme_id"],
            answers=data["answers"]
        )
        return json_response(data=QuestionSchema().dump(question))


class QuestionListView(View):
    @docs(tags=["quiz"], summary="List questions")
    @response_schema(ListQuestionSchema, 200)
    @auth_required
    async def get(self):
        theme_id = self.request.query.get("theme_id")
        questions = await self.store.quizzes.list_questions(
            theme_id=int(theme_id) if theme_id else None
        )
        return json_response(
            data={"questions": QuestionSchema().dump(questions, many=True)}
        )