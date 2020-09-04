import requests
from marshmallow import Schema, fields, post_load, ValidationError, validate
from flask import jsonify, abort, request, session, make_response

from src import db
from src.models import User, DgfObject, Comment
from src.api import bp
from src.api.auth import login_required


ME_URL = 'https://demo.data.gouv.fr/api/1/me/'


class LoginSchema(Schema):
    token = fields.Str(required=True)


class ObjectSchema(Schema):
    suspicious = fields.Boolean(required=True)
    read = fields.Boolean(required=True)
    deleted = fields.Boolean(required=True)
    dgf_type = fields.String(required=True, validate=validate.OneOf(['user', 'community_resource', 'organization', 'dataset', 'reuse']))
    dgf_id = fields.String(required=True)

    @post_load
    def make_object(self, data, **kwargs):
        return DgfObject(**data)


class UserSchema(Schema):
    first_name = fields.Str(required=True)
    last_name = fields.Str(required=True)
    email = fields.Email(required=True)
    dgf_id = fields.Str(required=True)

    @post_load
    def make_user(self, data, **kwargs):
        return User(**data)


@bp.route('/submit-token', methods=['POST'])
def submit_token():
    data = request.get_json(force=True) or {}

    errors = LoginSchema().validate(data)
    if errors:
        return make_response((errors, 400))
    token = data['token']

    r = requests.get(ME_URL, headers={'Authorization': f'Bearer {token}'})
    if r.status_code != 200:
        return make_response((r.json(), r.status_code))
    user_data = r.json()

    if not 'admin' in user_data['roles']:
        return make_response(('Not enough priviledges', 403))

    user = User.query.filter_by(dgf_id=user_data['id']).first()
    if user is None:
        new_user = User(
            first_name=user_data['first_name'],
            last_name=user_data['last_name'],
            email=user_data['email'],
            dgf_id=user_data['id'])
        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as err:
            return make_response((err.message, 500))

    session['user_id'] = user_data['id']
    return make_response(('success', 200))


@bp.route('/logout')
@login_required
def logout(user):
    session.pop(user.id, None)
    return make_response(('success', 200))


@bp.route('/objects', methods=['POST'])
@login_required
def create_object(user):
    data = request.get_json(force=True) or {}
    try:
        new_object = ObjectSchema().load(data)
    except ValidationError as err:
        return make_response((err.messages, 400))
    try:
        db.session.add(new_object)
        db.session.commit()
    except Exception as err:
        return make_response((err.messages, 500))
    return make_response(('success', 201))


@bp.route('/objects/<dgf_object_id>', methods=['GET'])
@login_required
def get_object(user, dgf_object_id):
    dgf_object = DgfObject.query.filter_by(dgf_id=dgf_object_id).first()
    if dgf_object is None:
        return make_response(('Object not found', 404))
    schema = ObjectSchema()
    result = schema.dump(dgf_object)
    return make_response((result, 200))


@bp.route('/objects/<dgf_object_id>', methods=['PUT'])
@login_required
def update_object(user, dgf_object_id):
    dgf_object = DgfObject.query.filter_by(dgf_id=dgf_object_id).first()
    if dgf_object is None:
        return make_response(('Object not found', 404))
    schema = ObjectSchema()
    result = schema.dump(dgf_object)
    return make_response((result, 200))
