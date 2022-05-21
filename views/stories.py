from flask import Response
from flask_restful import Resource
from models import Story
from views import get_authorized_user_ids
import json
import flask_jwt_extended

class StoriesListEndpoint(Resource):

    def __init__(self, current_user):
        self.current_user = current_user
    
    @flask_jwt_extended.jwt_required()
    def get(self):
        # get stories created by one of these users:
        # print(get_authorized_user_ids(self.current_user))
        user_ids = get_authorized_user_ids(self.current_user)
        stories = Story.query.filter(Story.user_id.in_(user_ids)).all()
        stories_json = [story.to_dict() for story in stories]
        return Response(json.dumps(stories_json), mimetype="application/json", status=200)


def initialize_routes(api):
    api.add_resource(
        StoriesListEndpoint, 
        '/api/stories', 
        '/api/stories/', 
        resource_class_kwargs={'current_user': flask_jwt_extended.current_user}
    )
