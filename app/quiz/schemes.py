from marshmallow import Schema, fields, validate, EXCLUDE


class AnswerSchema(Schema):
    title = fields.Str(required=True)
    is_correct = fields.Bool(required=True)


class QuestionSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)
    theme_id = fields.Int(required=True)
    answers = fields.Nested(
        AnswerSchema,
        many=True,
        required=True,
        validate=validate.Length(min=2)
    )


class ThemeSchema(Schema):
    class Meta:
        unknown = EXCLUDE

    id = fields.Int(dump_only=True)
    title = fields.Str(required=True)


class ThemeListSchema(Schema):
    themes = fields.Nested(ThemeSchema, many=True)


class ThemeIdSchema(Schema):
    theme_id = fields.Int(required=True)


class ListQuestionSchema(Schema):
    questions = fields.Nested(QuestionSchema, many=True)